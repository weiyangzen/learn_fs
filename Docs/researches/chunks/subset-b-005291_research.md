# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_init.c lines 1-8853

## Scope

This chunk covers the first half of the Emulex/Broadcom `lpfc_init.c` driver initialization file. The range starts with module includes, global state, and init-time prototypes, then covers HBA/VPD configuration, link bring-up/down paths, heartbeat and error-attention handling, VPD/model parsing, vport/SCSI-host creation, SLI4 asynchronous event dispatch, congestion-management timers and parameter parsing, PCI/SR-IOV helpers, SLI3/SLI4 driver-resource allocation, API table setup, IOCB/SGL list management, and the start of SLI4 RPI header initialization.

The chunk ends inside `lpfc_sli4_init_rpi_hdrs()` immediately after `rpi_hdr = lpfc_sli4_create_rpi_hdr(phba);`; the rest of RPI header posting/removal behavior is in the next chunk.

## Purpose

This code is the driver-side lifecycle coordinator for lpfc HBAs during probe, online/offline transitions, reset/recovery, link events, and first-stage resource setup. It bridges Linux PCI/SCSI/FC transport APIs with lpfc's SLI2/SLI3/SLI4 firmware mailbox and queue model.

At a high level, the chunk:

- Reads adapter revision, VPD, WWN, SLI4 parameter, and read-config mailbox data into `struct lpfc_hba` and `struct lpfc_vport`.
- Configures the physical port and vports, including FC transport host attributes, NPIV/VPI flags, SCSI host templates, VMID resources, and optional NVMe/NVMe target behavior.
- Starts and stops timers, delayed work, and worker-thread event paths for heartbeat, mailbox timeout, error attention polling, FCF rediscovery, VMID cleanup, interrupt moderation, idle-stat based polling, and CMF congestion management.
- Implements SLI3 and SLI4-specific recovery paths for link attention, error attention, board restart, function reset, offline/online transitions, and queue/resource cleanup.
- Allocates/free driver-owned DMA pools, IOCB lists, SGL/XRI state, CQ event pools, CPU/IRQ mapping arrays, per-cpu statistics, and FCF failover bitmaps.
- Dispatches SLI4 async completion queue events for link, FC, FCoE/FIP, DCBX, GRP5, SLI, congestion, optics, temperature, FA-WWN, and FCF failover events.

## Important APIs, Types, and Functions

### Initialization and VPD

- `lpfc_config_port_prep()` allocates a mailbox, optionally reads LC-HBA NV parameters with a licensed key, issues `READ_REV`, validates revision data, sets SLI3 feature flags, captures WWNs/random data, dumps VPD memory in chunks, and calls `lpfc_parse_vpd()`.
- `lpfc_config_port_post()` performs post-`CONFIG_PORT` work: reads service parameters and config, updates FC host WWNs and max NPIV vports, bounds queue depth to firmware `max_xri`, records link media table `lmt`, derives model strings, stops FCP/extra rings until ready, posts SLI3 ELS receive buffers, configures MSI-X attentions, enables SLI3 host interrupts, starts heartbeat/error-attention/ELS timers, optionally initializes or downs the link, enables async events, and reads option ROM version.
- `lpfc_sli4_refresh_params()` reads `GET_SLI4_PARAMETERS` and refreshes dynamic `mi_cap`, `mi_ver`, `cmf`, and `pls` feature fields in `phba->sli4_hba.pc_sli4_params`.
- `lpfc_fill_vpd()` and `lpfc_parse_vpd()` parse PCI VPD tags and populate serial number, model description, model name, program type, and port strings.
- `lpfc_get_hba_model_desc()` and `lpfc_get_atto_model_desc()` map PCI device IDs and link-speed capabilities to user-visible model name/description strings.
- `lpfc_hba_init()` implements LC-HBA challenge-key hash setup using `lpfc_sha_init()`, `lpfc_sha_iterate()`, and `lpfc_challenge_key()`.

### Link, Online/Offline, and Reset Paths

- `lpfc_hba_init_link()` and `lpfc_hba_init_link_fc_topology()` issue `INIT_LINK` with validated user link speed/topology and set `cfg_suppress_link_up` once accepted.
- `lpfc_hba_down_link()` issues `DOWN_LINK`.
- `lpfc_hba_down_prep()` disables SLI3 interrupts and cleans discovery resources for the physical and virtual ports.
- `lpfc_hba_down_post_s3()` frees posted ELS buffers and cleans TX completion queues.
- `lpfc_hba_down_post_s4()` frees HBQ buffers, aborts TX completions, returns aborted ELS SGLs and IO buffers to free lists, reposts aborted NVMET contexts, and drains slow-path events.
- `lpfc_online()` blocks management IO, runs SLI4 or SLI3 HBA setup, recreates NVMe local port state when needed, clears `FC_OFFLINE_MODE`, sets VPI registration/init flags, resets non-physical VPIs when firmware cleared them, creates multi-XRI pools, registers CPU hotplug state, and unblocks management IO.
- `lpfc_offline_prep()` blocks management IO, marks link down, clears VPI/VFI/RPI state across vports/nodes, drives fabric nodes through recovery/removal events, shuts down mailbox handling, and flushes the workqueue.
- `lpfc_offline()` stops the port, destroys NVMe/NVMET transport ports, stops vport timers, calls `lpfc_sli_hba_down()`, clears work events, sets `FC_OFFLINE_MODE`, removes CPU hotplug if appropriate, and tears down multi-XRI pools.
- `lpfc_reset_hba()` chooses graceful or no-wait offline prep depending on `LPFC_SLI_ACTIVE` and `MBX_TMO_ERR`, may perform PCI function reset, restarts the board, and calls `lpfc_online()`.

### Timers, Work, and Heartbeat

- `lpfc_hb_timeout()` posts `WORKER_HB_TMO` to the physical port event bitmap and wakes the worker.
- `lpfc_rrq_timeout()` marks `HBA_RRQ_ACTIVE` and wakes the worker unless unloading.
- `lpfc_issue_hb_mbox()`, `lpfc_hb_mbox_cmpl()`, `lpfc_issue_hb_tmo()`, and `lpfc_hb_timeout_handler()` implement heartbeat mailbox pacing, outstanding-heartbeat tracking, skipped-heartbeat accounting, stale ELS buffer cleanup, vport timeout checks, FDMI checks, and multi-XRI rebalance hooks.
- `lpfc_idle_stat_delay_work()` samples CPU idle counters and toggles EQ handling between workqueue and threaded IRQ modes.
- `lpfc_hb_eq_delay_work()` computes adaptive EQ interrupt delay from per-cpu interrupt counts and moves EQs between per-cpu lists when their last CPU changes.
- `lpfc_stop_vport_timers()`, `lpfc_stop_hba_timers()`, `lpfc_stop_port_s3()`, `lpfc_stop_port_s4()`, and `lpfc_stop_port()` cancel the timer/delayed-work set for vports and HBAs.

### Error Attention and Link Attention

- `lpfc_offline_eratt()` and `lpfc_sli4_offline_eratt()` are terminal offline paths for SLI3 and SLI4 hardware errors.
- `lpfc_handle_deferred_eratt()` handles SLI3 deferred ERATT conditions by waiting for `HS_FFER1` to clear and preserving host-status data.
- `lpfc_handle_eratt_s3()` handles SLI3 FFER6/FFER8 link recovery, critical temperature, dump events, and unrecoverable hardware errors.
- `lpfc_sli4_port_sta_fn_reset()` blocks devices, waits for port ready when required, clears mailbox-active state for no-wait paths, flushes IO and abort lists, disables/re-enables interrupts, restarts the board, and brings the HBA online.
- `lpfc_handle_eratt_s4()` handles SLI4 interface-type specific UE/port-status conditions, over-temperature, firmware-update/debug-dump/provisioning port-down reasons, reset-needed recovery, dump events, and fallback offline.
- `lpfc_handle_latt()` is the SLI3 link-attention worker path: it flushes ELS commands, blocks ELS IOCBs, issues `READ_TOPOLOGY`, clears link attention in HA, or restores interrupts and marks the HBA error on failure.

### Buffer, XRI, SGL, and Pool Management

- `lpfc_sli3_post_buffer()` allocates IOCB and one or two DMA buffers per ring buffer post, fills 64-bit BDEs, issues `CMD_QUE_RING_BUF64_CN`, and tracks missed buffer count.
- `lpfc_sli4_els_sgl_update()` and `lpfc_sli4_nvmet_sgl_update()` resize ELS/NVMET SGL lists after function reset and remap logical XRIs to physical XRI tags.
- `lpfc_io_buf_flush()` drains per-hardware-queue get/put IO lists into a temporary list sorted by XRI so POST_SGL can use contiguous ranges.
- `lpfc_io_buf_replenish()` redistributes IO buffers round-robin across hardware queues and resets current IOCB completions.
- `lpfc_sli4_io_sgl_update()` computes available IO XRIs, shrinks oversized IO buffer populations, remaps XRIs, and replenishes per-HWQ lists.
- `lpfc_new_io_buf()` allocates SLI4 IO buffers from `lpfc_sg_dma_buf_pool`, enforces BlockGuard alignment where needed, assigns XRI and IOTAG, initializes command/response and optional extended-SGL lists, and posts SGLs.
- `lpfc_create_multixri_pools()`, `lpfc_destroy_multixri_pools()`, `lpfc_create_expedite_pool()`, and `lpfc_destroy_expedite_pool()` move IO buffers between HWQ put lists and public/private/expedite XRI pools for rebalance and NVMe expedite behavior.
- `lpfc_free_iocb_list()`, `lpfc_init_iocb_list()`, `lpfc_free_sgl_list()`, `lpfc_free_els_sgl_list()`, `lpfc_free_nvmet_sgl_list()`, `lpfc_init_active_sgl_array()`, `lpfc_free_active_sgl()`, and `lpfc_init_sgl_list()` provide core IOCB/SGL list allocation and teardown.

### Vports, SCSI Host Integration, and Attributes

- `lpfc_vmid_res_alloc()` allocates VMID arrays, priority bitmaps, locks, limits, timeout configuration, and hash tables when VMID is enabled. It disables SLI4-only VMID modes on SLI3.
- `lpfc_create_port()` selects the physical/vport SCSI host template, optionally disables host reset for configured WWPNs, sets SG table size and hardware queue count, allocates `Scsi_Host`, initializes `struct lpfc_vport`, allocates VMID resources, sets timers/lists/locks, configures BlockGuard, adds the host with DMA parent, and links the vport into `phba->port_list`.
- `destroy_port()` removes debugfs, FC/SCSI hosts, unlinks the vport, and calls `lpfc_cleanup()`.
- `lpfc_cleanup()` drives outstanding nodes through discovery removal/recovery, flushes IO on unloading plus PCI offline, waits for the node list to drain, and cleans vport RRQs.
- `lpfc_scan_finished()` lets SCSI scanning complete after unloading, long waits, link-down timeout, vport ready/no discovery state, or no active mailbox.
- `lpfc_host_attrib_init()` publishes WWNs, supported/active FC4s, symbolic name, speeds, max frame size, dev-loss timeout, and max NPIV vports into FC transport attributes.

### SLI4 Async Events and Congestion Management

- `lpfc_sli4_async_event_proc()` drains `sp_asynce_work_queue` under `asynce_list_lock`, dispatches by trailer code, and returns CQ events to the pool.
- `lpfc_sli4_async_link_evt()` handles generic FC/FCoE link ACQEs; for FC mode it issues `READ_TOPOLOGY`, while FCoE mode synthesizes the mailbox completion directly.
- `lpfc_sli4_async_fc_evt()` handles FC link ACQEs, including trunking events, link-state updates, informational attention types, MDS flags, unexpected WWPN, and read-topology continuation.
- `lpfc_update_trunk_link_status()` maintains per-port trunk link state/faults, logical/physical speed, `fc_linkspeed`, and re-signals CMF after speed changes.
- `lpfc_sli4_async_fip_evt()` handles FCoE/FIP events for new/modified FCF records, table full, FCF dead fast failover, and CVL; it coordinates FCF rediscovery flags, round-robin bitmaps, per-vport CVL, FDISC retry, and fallback rediscovery.
- `lpfc_sli4_async_sli_evt()` handles SLI internal events such as over/normal temperature, optics misconfiguration, remote DPort, congestion parameter changes, FA-WWN misconfiguration, EEPROM failure, congestion signals, remote degrade, and CM stats reset.
- `lpfc_sli4_async_grp5_evt()` updates logical link speed from GRP5 events.
- `lpfc_sli4_cgn_params_read()`, `lpfc_cgn_params_parse()`, and `lpfc_cgn_params_val()` read firmware congestion parameters from `LPFC_PORT_CFG_NAME`, validate magic/mode, copy them into `phba->cgn_p`, update congestion-info CRC, transition CMF modes, issue EDC when needed, and unblock IO when leaving managed throttling.
- `lpfc_cmf_start()`, `lpfc_cmf_stop()`, `lpfc_cmf_signal_init()`, `lpfc_cmf_timer()`, `lpfc_cmf_stats_timer()`, `lpfc_cgn_update_stat()`, and `lpfc_calc_cmf_latency()` implement CMF rate interval accounting, firmware sync WQEs, per-cpu byte/latency collection, driver/fabric congestion counters, minute/hour/day rollups, and congestion-info CRC updates.

### PCI, SR-IOV, and Driver Resource Setup

- `lpfc_enable_pci_dev()` and `lpfc_disable_pci_dev()` wrap PCI memory enable, resource request/release, bus mastering, MWI, saved PCI state, and EEH fundamental reset flag.
- `lpfc_sli_sriov_nr_virtfn_get()` reads PCIe SR-IOV total VF capability; `lpfc_sli_probe_sriov_nr_virtfn()` validates and enables configured VFs.
- `lpfc_api_table_setup()` sets the PCI device group and installs init, SCSI, SLI, and mailbox function tables.
- `lpfc_init_api_table_setup()` selects SLI3 vs SLI4 implementations for down-post, error-attention, stop-port, link init/down, and selective reset.
- `lpfc_setup_driver_resource_phase1()` initializes common atomics, locks, lists, wait queues, timers, delayed work, and unblock work.
- `lpfc_sli_driver_resource_setup()` configures SLI3 resources: module params, SLI rings, SG DMA buffer sizing, SLI setup/queue init, driver memory, DMA pools, and optional SR-IOV.
- `lpfc_sli4_driver_resource_setup()` configures SLI4 resources: CPU counts, workqueue, RRQ/FCF/CMF timers, mailbox extension context, FCoE defaults, HBQ callbacks, VMID timer, abort/SGL/async queues, extent lists, memory, POST status, PCI function reset, bootstrap mailbox, endian negotiation, read-config, RRQ pool, optional NVMET enablement by WWPN, SLI4 parameters, SGL DMA sizing, DMA pools, OAS/RAS verification, queue verification, CQ event pool, SGL/active SGL/RPI header structures, FCF bitmap, EQ handles, CPU map, per-cpu EQ/debug/CMF stats, idle stats, and optional SR-IOV.
- `lpfc_sli_driver_resource_unset()` and `lpfc_sli4_driver_resource_unset()` reverse their respective allocations, including SLI4 per-cpu state, RPI headers/RPIs, FCF bitmap, active/ELS/NVMET SGLs, CQ event pool, resource identifiers, bootstrap mailbox, driver memory, and FCF connection records.
- `lpfc_setup_driver_resource_phase2()` starts the kernel worker thread; `lpfc_unset_driver_resource_phase2()` destroys the workqueue and stops the worker.

## Control Flow

Probe and initial bring-up enter through resource setup, API table setup, port creation, SLI setup, and then configuration port prep/post routines. The control-flow shape is intentionally staged:

1. Common driver resources are initialized in phase 1 before device-specific setup.
2. SLI3 or SLI4 setup allocates DMA pools and hardware/firmware-facing resources.
3. `lpfc_create_port()` creates the physical port's `Scsi_Host` and later NPIV vports.
4. `lpfc_config_port_prep()` reads revision/VPD/WWN data before `CONFIG_PORT`.
5. `lpfc_config_port_post()` reads service/config data, publishes FC host attributes, posts receive buffers, enables interrupts/timers, starts link initialization, enables async events, and queues option-ROM version retrieval.
6. The worker thread handles timer-posted and interrupt-posted events, including heartbeat, link attention, FCF rediscovery, and SLI4 async events.

Online/offline transitions are guarded by management-IO blocking. Online paths call SLI setup again as needed, clear offline flags on all vports, restore VPI/NVMe state, and recreate XRI pools. Offline prep tears down discovery and mailbox state before `lpfc_offline()` stops timers/ports, destroys NVMe transports, calls SLI down, clears work events, and sets offline flags.

Error paths branch heavily by SLI revision and interface type. SLI3 error attention uses host-status bits (`HS_FFER*`, `HS_CRIT_TEMP`) and board restart/online paths. SLI4 error attention reads SLI port status/error registers or IF type 0 semaphore/UE registers, attempts function reset where possible, and falls back to offline error state. Link events similarly differ: SLI3 uses HA/LATT and `READ_TOPOLOGY`; SLI4 receives ACQEs and either issues or synthesizes read-topology continuation.

## State and Persistence Behavior

Most state is kernel-resident in `struct lpfc_hba`, `struct lpfc_vport`, SLI rings/queues, per-HWQ lists, and FC transport host attributes. Important durable fields in this chunk include:

- Adapter identity and capability: `vpd`, `wwnn`, `wwpn`, `RandomData`, `SerialNumber`, `ModelName`, `ModelDesc`, `ProgramType`, `Port`, `lmt`, `sli_rev`, `sli3_options`, `max_vpi`, `max_vports`, SLI4 parameters, `cfg_*` module-derived settings.
- Link and lifecycle state: `link_state`, `link_flag`, `fc_linkspeed`, `sli4_hba.link_state`, `FC_OFFLINE_MODE`, `FC_UNLOADING`, `FC_LOADING`, VPI/VFI/RPI registered flags, `HBA_SETUP`, `HBA_PCI_ERR`, `MBX_TMO_ERR`, `HBA_ERATT_HANDLED`, `DEFER_ERATT`, `HBA_HBEAT_*`, `HBA_RRQ_ACTIVE`.
- Work/timer state: worker thread, workqueues, timer objects, delayed work, work event bitmaps, `last_completion_time`, skipped heartbeat timestamp, FCF rediscovery flags and event tags.
- Queue/buffer state: SLI3 rings, ELS post buffers, TX completion queues, SLI4 ELS/NVMET/IO SGL lists, active SGL pointer array, XRI counts, public/private/expedite XRI pools, per-HWQ get/put/abort lists, CQ event pools, CPU/EQ maps.
- Congestion state: `cgn_i` DMA buffer, `cgn_p` firmware parameters, CMF mode/rates/counters/timers, per-cpu `cmf_stat`, FPIN/signal counters, minute/hour/day congestion ring indexes, CRC fields.
- FCoE/FCF state: `fcf.fcf_flag`, current/failover records, FCF round-robin bitmap, FCoE event tags, CVL tags, FCF connection list, VLAN/FC map defaults.

Hardware-persistent state is changed through firmware mailboxes and PCI APIs: `READ_REV`, `READ_NV`, `READ_CONFIG`, `READ_TOPOLOGY`, `INIT_LINK`, `DOWN_LINK`, `CONFIG_MSI`, SLI4 `GET_SLI4_PARAMETERS`, read-object for congestion parameters, PCI function reset, SR-IOV enablement, board restart/reset, SGL/RPI resource posts, and CMF sync WQEs.

Concurrency is controlled with spinlocks (`hbalock`, per-list locks, host locks), atomics, per-cpu storage, timer/workqueue sequencing, and mailbox issue modes (`MBX_POLL`, `MBX_NOWAIT`, `LPFC_MBX_WAIT`, `LPFC_MBX_NO_WAIT`). The code frequently splices lists under locks and processes/free them after dropping locks.

## Dependencies and Integration Points

This chunk depends on Linux kernel PCI, SCSI, FC transport, timer, workqueue, kthread, DMA pool, IDR, cpuhotplug, firmware, and per-cpu APIs. It also depends on lpfc-local headers for hardware register/bitfield definitions, mailbox commands, SLI queue types, discovery state machines, NVMe/NVMET support, logging, vport state, and device IDs.

Major internal integration points include:

- SLI layer: `lpfc_sli_issue_mbox()`, `lpfc_sli_hba_setup()`, `lpfc_sli4_hba_setup()`, `lpfc_sli_hba_down()`, `lpfc_sli_brdrestart()`, `lpfc_sli_brdreset()`, `lpfc_sli_brdready()`, IOCB issue/cancel/release helpers, SGL/RPI/XRI allocation helpers, queue verification, and mailbox resource preparation/cleanup.
- Discovery and ELS: `lpfc_disc_state_machine()`, `lpfc_linkdown()`, `lpfc_linkdown_port()`, `lpfc_els_flush_all_cmd()`, `lpfc_mbx_cmpl_read_topology()`, FLOGI/FDISC retry, Fabric node creation, and dev-loss handling.
- SCSI/FC transport: `scsi_host_alloc()`, `scsi_add_host_with_dma()`, `fc_host_*` attributes, `fc_host_post_vendor_event()`, `fc_remove_host()`, `scsi_remove_host()`, and block/unblock of SCSI devices during recovery.
- NVMe/NVMET: local/target port create/destroy, NVMET memory and context buffer allocation/posting, NVMe abort/NVMELS flush paths, and NVMe-specific SGL/segment limits.
- FCoE/FCF: FCF record scan/read, rediscovery, round-robin failover bitmap manipulation, FCF dead failthrough, FCF connection records, and CVL handling across all vports.
- Congestion management: EDC/FPIN signaling, firmware read-object path, CMF sync WQE issue/completion data, rx monitor debug reporting, and congestion info buffer registration.
- PCI/platform: PCI enable/disable, MSI/MSI-X configuration, SR-IOV enablement, PCI channel offline checks, PCI function reset, and EEH recovery expectations.

## Risks

- Initialization ordering is fragile. Many later paths assume mailbox pools, SLI memory, DMA pools, workqueues, timers, queue structures, and FC host state were initialized in the staged order used here.
- Error cleanup must exactly mirror partial allocation. `lpfc_sli4_driver_resource_setup()` has a long failure ladder; missing one free or freeing an uninitialized object can leak kernel memory, DMA pools, per-cpu state, or leave stale firmware resources.
- Link/error recovery races are likely if state bits or locks change. Heartbeat timers, async events, mailbox completion, offline prep, PCI error recovery, and worker-thread handling all touch shared link, mailbox, queue, and vport state.
- Management IO blocking waits on active mailbox completion. A mailbox that never completes can delay online/offline transitions until timeout and still proceed with partially active firmware state.
- VPD parsing trusts length fields enough to walk the provided buffer. The outer parser bounds the VPD region length, but malformed tags and string lengths are still sensitive because they populate fixed-size HBA strings.
- SLI3 and SLI4 paths share wrapper entry points but different assumptions. Using the wrong function table entry for a PCI device group would cause wrong interrupt, reset, buffer, and mailbox behavior.
- SGL/XRI remapping after reset is high risk. IO/ELS/NVMET SGL counts must stay consistent with firmware `max_xri`, sorted POST_SGL requirements, active SGL arrays, and per-HWQ list counts.
- CMF timers modify IO throttling and counters asynchronously. Incorrect atomic/reset sequencing can undercount bytes, fail to unblock IO, or apply the wrong bandwidth interval after link speed or firmware parameter changes.
- FCF failover and CVL handling are stateful across all vports. Incorrect flag transitions can suppress needed rediscovery, duplicate scans, or reinstantiate VLinks while a vport is being deleted.
- SR-IOV enablement is intentionally non-fatal for unsupported devices, but enabling VFs changes PCI topology and should not be attempted after resources are already exposed incorrectly.
- The chunk ends mid-RPI header initialization, so this document alone cannot validate the full RPI header allocation/posting/unposting lifecycle.

## Test and Validation Signals

Useful validation should cover both build-time and hardware/runtime behavior:

- Build the lpfc driver with SCSI FC transport, NVMe FC, optional NVMET, debugfs, BlockGuard/DIF, MSI/MSI-X, and SR-IOV configurations to catch API and conditional-compilation issues.
- Probe SLI3 and SLI4 adapters and verify resource setup logs, DMA pool sizing, SCSI host registration, FC transport attributes, VPD/model strings, WWNs, supported speeds, and queue depth adjustments.
- Exercise link initialization and suppression modes: valid/invalid configured link speeds, `INIT_LINK`, `DOWN_LINK`, link-up/link-down ACQEs, SLI3 LATT, FCoE synthesized topology completion, and FC read-topology mailbox completion.
- Run reset and recovery tests: mailbox timeout reset, PCI function reset, board restart, SLI3 FFER6/FFER8 recovery, SLI4 port-status reset-needed events, firmware-update port-down events, PCI channel offline, and reset-disabled mode.
- Verify timer/work behavior: heartbeat mailbox issue/completion/timeout, RRQ timer, ELS timer cancellation, FCF rediscovery timer, idle-stat polling changes, adaptive EQ delay, and worker-thread startup/stop.
- Test SGL/XRI/resource accounting under probe, reset, and unload: IOCB list counts, ELS/NVMET SGL grow/shrink, IO buffer flush/replenish sorted by XRI, active SGL array allocation, DMA pool cleanup, and multi-XRI pool create/destroy.
- Validate vport and discovery flows: NPIV vport creation/removal, VPI register/init flags after online, CVL on one/all vports, node-list cleanup, fabric-node recovery/removal, scan-finished timing, and dev-loss interactions.
- Validate FCoE/FCF flows with FCF new/modified/dead/table-full events, fast failover, FCF rediscovery, round-robin bitmap updates, CVL fallback, and FDISC retry.
- Exercise CMF/EDC/FPIN behavior: firmware congestion parameter read-object, mode transitions OFF/MANAGED/MONITOR, CMF sync WQEs, per-cpu byte and latency counters, IO unblocking, rx monitor records, minute/hour/day stats, and congestion-info CRC updates.
- Test optics/temperature/FA-WWN events and confirm FC vendor events, speed refresh, `fawwpn_flag` updates, and over-temperature offline behavior.
- Validate SR-IOV configured VF count handling on capable and incapable devices, including bounds check against PCI SR-IOV total VF capability.

## Unresolved Cross-Chunk References

The RPI header initialization path starts at the end of this chunk but its allocation/posting completion and cleanup details continue after line 8853. The final per-file report should merge this document with the next chunk before drawing conclusions about `lpfc_sli4_init_rpi_hdrs()`, `lpfc_sli4_create_rpi_hdr()`, and `lpfc_sli4_remove_rpi_hdrs()`.
