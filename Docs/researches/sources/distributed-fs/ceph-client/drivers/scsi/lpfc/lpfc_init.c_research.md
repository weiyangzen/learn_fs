# Research: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_init.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005291`: lines 1-8853, `Docs/researches/chunks/subset-b-005291_research.md`
- `subset-b-005292`: lines 8854-15820, `Docs/researches/chunks/subset-b-005292_research.md`

## Chunk Research

### subset-b-005291: lines 1-8853

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

### subset-b-005292: lines 8854-15820

# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_init.c lines 8854-15820

## Scope

This chunk covers the late and terminal portion of `lpfc_init.c`, from SLI4 RPI header setup through PCI probe/remove, power management, PCI error recovery, firmware update, congestion/RAS support, and module registration/exit. It is the code that turns previously defined low-level LPFC facilities into concrete PCI-device lifecycle behavior for both SLI3 (`LPFC_PCI_DEV_LP`) and SLI4 (`LPFC_PCI_DEV_OC`) adapters.

## Purpose

The code initializes and tears down Emulex/Broadcom LPFC Fibre Channel HBAs in the Linux SCSI/FC transport stack. In this chunk, initialization is organized around:

- Allocating `struct lpfc_hba` and creating the physical `struct lpfc_vport`/`Scsi_Host`.
- Mapping PCI BARs and SLI interface registers for SLI3 and SLI4 devices.
- Reading SLI4 firmware/device configuration, resource limits, FC4 capability, persistent topology, congestion signaling, function numbering, and SLI4 parameter descriptors.
- Allocating and creating SLI4 EQ/CQ/WQ/MQ/RQ queues and their lookup tables.
- Enabling interrupts with MSI-X/MSI/INTx fallback, including SLI4 CPU/vector/hardware-queue affinity mapping and CPU-hotplug handling.
- Handling removal, suspend/resume, PCI Advanced Error Reporting recovery, function reset, firmware download, congestion-buffer registration, OAS/RAS feature enablement, and final module registration.

## Important APIs, Types, and Functions

- `lpfc_sli4_create_rpi_hdr()` / `lpfc_sli4_remove_rpi_hdrs()` allocate and free 4 KiB DMA RPI header templates for SLI4 ports that do not use extents. They update `phba->sli4_hba.lpfc_rpi_hdr_list`, `next_rpi`, and `rpi_hdrs_in_use`.
- `lpfc_hba_alloc()` / `lpfc_hba_free()` own the main `struct lpfc_hba` lifetime and board-number allocation through `lpfc_get_instance()`/`idr_remove()`.
- `lpfc_create_shost()` / `lpfc_destroy_shost()` create or destroy the physical vport and SCSI host, initialize FC timers, attach debugfs, stash `Scsi_Host` in PCI driver data, set FDMI/SmartSAN masks, and handle NVMe target-only pport setup.
- `lpfc_sli_pci_mem_setup()` / `lpfc_sli_pci_mem_unset()` map SLI3 BAR0/BAR2, allocate SLI2 SLIM and HBQ DMA areas, and set register pointers such as `HAregaddr`, `CAregaddr`, `HSregaddr`, and `HCregaddr`.
- `lpfc_sli4_pci_mem_setup()` / `lpfc_sli4_pci_mem_unset()` map SLI4 config, control, doorbell, and DPP BARs according to `lpfc_sli_intf_if_type`. They select if-type-specific EQ/CQ doorbell handlers and populate SLI4 register pointers with helpers `lpfc_sli4_bar0_register_memmap()`, `lpfc_sli4_bar1_register_memmap()`, and `lpfc_sli4_bar2_register_memmap()`.
- `lpfc_sli4_post_status_check()` waits up to 30 seconds for POST readiness through the port semaphore/status registers, checks unrecoverable-error registers, records `work_status[]`, and flags PLDV state for supported adapters.
- `lpfc_create_bootstrap_mbox()` / `lpfc_destroy_bootstrap_mbox()` allocate a 16-byte-aligned coherent DMA bootstrap mailbox region and encode the SLI4 high/low 30-bit mailbox DMA address format.
- `lpfc_sli4_read_config()` issues `READ_CONFIG`, captures max/base XRI/VPI/VFI/RPI/FCFI and queue resource counts, lmt, link info, FA-PWWN, trunking, extents, encryption support, BB credit support, persistent topology, congestion-registration mode, forced link speed, PF/VF function config, and clamps queue depth/vport counts to driver limits.
- `lpfc_get_sli4_parameters()` issues `GET_SLI4_PARAMETERS` and fills `phba->sli4_hba.pc_sli4_params` plus driver feature knobs such as PHWQ, xPSGL, NVMe, suppress-response, EQDR, max segment size, embedded FCP I/O, expanded WQ/CQ page use, MDS diagnostics, and NSLER.
- `lpfc_sli4_queue_verify()`, `lpfc_sli4_queue_create()`, `lpfc_sli4_queue_setup()`, `lpfc_sli4_queue_unset()`, and `lpfc_sli4_queue_destroy()` split queue lifecycle into host-memory allocation, firmware creation, firmware destruction, and host-memory release.
- `lpfc_alloc_io_wq_cq()` creates per-hardware-queue I/O CQ/WQ objects, while `lpfc_create_wq_cq()` performs firmware-side CQ then WQ/MQ creation and binds WQs to rings.
- `lpfc_sli4_cq_event_pool_create()`, `lpfc_sli4_cq_event_pool_destroy()`, `lpfc_sli4_cq_event_alloc()`, and release variants manage a pool of `struct lpfc_cq_event` entries used by ISR/worker slow-path event handoff.
- `lpfc_pci_function_reset()` performs if-type-specific SLI4 function/port reset: mailbox reset for if-type 0, status/ready polling and control-register INIT_PORT for if-type 2/6.
- `lpfc_sli_enable_intr()` and `lpfc_sli4_enable_intr()` enable interrupts with fallback from MSI-X to MSI to INTx. SLI4 uses `request_threaded_irq()` for MSI-X EQ handlers and records `lpfc_hba_eq_hdl` state.
- `lpfc_cpu_affinity_check()`, `lpfc_find_cpu_handle()`, `lpfc_sli4_enable_msix()`, `lpfc_irq_rebalance()`, `lpfc_cpu_online()`, and `lpfc_cpu_offline()` build and maintain the SLI4 CPU/EQ/hardware-queue map, including NUMA/non-hyperthread modes and temporary EQ polling during CPU offline.
- `lpfc_pci_probe_one_s3()` and `lpfc_pci_probe_one_s4()` are the primary attach paths. `lpfc_pci_probe_one()` dispatches by reading `LPFC_SLI_INTF`.
- `lpfc_pci_remove_one_s3()` and `lpfc_pci_remove_one_s4()` perform complete detach. SLI4 additionally unregisters congestion buffers, tears down NVMe/NVMeT transport objects, destroys multixri pools, calls `lpfc_sli4_hba_unset()`, and unmaps SLI4 BARs.
- `lpfc_pci_suspend_one_*()`, `lpfc_pci_resume_one_*()`, `lpfc_io_error_detected_*()`, `lpfc_io_slot_reset_*()`, and `lpfc_io_resume_*()` integrate with PCI PM and AER callbacks.
- `lpfc_write_firmware()` and `lpfc_sli4_request_firmware_update()` implement synchronous or asynchronous `.grp` firmware download through Linux firmware APIs and LPFC object-write mailbox plumbing.
- `lpfc_init_congestion_buf()`, `lpfc_init_congestion_stat()`, `lpfc_reg_congestion_buf()`, and `lpfc_unreg_congestion_buf()` manage the CMF/FPIN congestion information buffer shared with firmware.
- `lpfc_sli4_oas_verify()` and `lpfc_sli4_ras_init()` gate optional OAS and RAS firmware logging based on adapter support and module parameters.
- `lpfc_init()` and `lpfc_exit()` register/unregister the misc management device, FC transport templates, CPU-hotplug state, PCI driver, and global HBA IDR.

## Control Flow

### SLI4 Probe

`lpfc_pci_probe_one()` reads `LPFC_SLI_INTF`; valid SLI4 devices go to `lpfc_pci_probe_one_s4()`, all others use the SLI3 path. The SLI4 probe path:

1. Allocates `phba`, initializes `poll_list`, enables the PCI device, and installs SLI API callbacks for `LPFC_PCI_DEV_OC`.
2. Maps SLI4 PCI memory with `lpfc_sli4_pci_mem_setup()`, which validates `SLI_INTF`, optionally reads `ASIC_ID`, maps BARs by if-type, and assigns doorbell/interrupt helper functions.
3. Allocates SLI4-specific and common driver resources, initializes RRQ and FCF-priority lists, and sets model strings.
4. Stops the port to a known state, initializes CPU map and EQ-handle arrays, enables interrupts, reduces to one IRQ/MRQ for non-MSI-X, and computes CPU affinity.
5. Creates the physical `Scsi_Host`/vport and sysfs attributes.
6. Calls `lpfc_sli4_hba_setup()` for the firmware/device bring-up, then records/logs interrupt mode, posts adapter-arrival event via `lpfc_post_init_setup()`, creates NVMe localport when configured, optionally requests firmware update, creates static vports, sets up the CPU-hotplug poll timer, and registers the hotplug instance.
7. On failure, unwinds in reverse order: sysfs, shost, interrupts, common resources, SLI4 resources, BAR mappings, PCI enablement, and `phba`.

### SLI3 Probe

`lpfc_pci_probe_one_s3()` follows the older SLI3 sequence: allocate HBA, enable PCI, set LP API table, map SLIM/control BARs and coherent SLIM/HBQ DMA, set up SLI3 resources and IOCB lists, create common resources, create shost/sysfs, then loop through interrupt modes. Each interrupt mode is validated by `lpfc_sli_hba_setup()` plus an active interrupt counter check before accepting the mode. It then posts init setup and creates static vports.

### Queue Lifecycle

SLI4 queue management is two-phase:

- `lpfc_sli4_queue_create()` allocates host queue descriptors and DMA-backed queue pages, initializes hardware-queue lock/list state, creates per-vector EQ descriptors, per-HDWQ I/O CQ/WQ pairs, NVMeT MRQ arrays when enabled, slow-path mailbox/ELS/NVMe-LS queues, unsolicited RQs, and clears per-HDWQ protocol stats.
- `lpfc_sli4_queue_setup()` creates firmware queues in dependency order: query firmware config, create EQs, create I/O CQ/WQs, create mailbox MQ/CQ, optional NVMeT CQ sets/MRQs, ELS WQ/CQ, NVMe LS WQ/CQ, unsolicited RQ, tune EQ delay, and build `cq_lookup`.
- `lpfc_sli4_queue_unset()` destroys firmware-side objects in reverse-ish dependency order.
- `lpfc_sli4_queue_destroy()` marks `LPFC_QUEUE_FREE_INIT`, waits for `LPFC_QUEUE_FREE_WAIT` users to drain, cleans poll lists, frees queue descriptors and backing resources, clears `lpfc_wq_list`, and drops the free-init flag.

### Interrupt and Affinity Flow

SLI4 MSI-X allocation starts with `cfg_irq_chann`, optionally constrained by NUMA/non-hyperthread affinity masks. Each allocated vector gets an `lpfc_hba_eq_hdl`, handler name, IRQ number, and threaded interrupt. The CPU map records first-IRQ CPUs and later `lpfc_cpu_affinity_check()` fills in missing CPU-to-EQ and CPU-to-HDWQ assignments, preferring same package/core, then package, then round-robin. CPU-hotplug callbacks rebalance affinities and switch affected EQs into or out of polling when an IRQ-affinitized CPU goes offline or online.

### Removal and Reset Flow

SLI4 remove marks the vport unloading, unregisters congestion buffers, removes sysfs and NPIV vports, removes FC/SCSI hosts, runs node and NVMe/NVMeT cleanup, frees I/O and IOCB resources, calls `lpfc_sli4_hba_unset()`, unsets driver resources, unmaps BARs, releases PCI resources, and frees the HBA. `lpfc_sli4_hba_unset()` itself stops timers, blocks async mailboxes, waits for or force-completes an active mailbox, aborts IOCBs, waits for XRI exchange-busy lists to drain when PCI is still online, removes CPU-hotplug state, disables interrupts/SR-IOV, stops the worker thread, stops RAS logging, unsets and destroys queues, resets the function, frees RAS DMA, and clears port work events.

PCI AER paths split by generation. For SLI4 frozen errors, `HBA_PCI_ERR` prevents duplicate reset preparation, management and SCSI I/O are blocked/flushed, queues and interrupts are destroyed/disabled, and PCI is disabled. Slot reset re-enables the PCI device, restores and re-saves config state, clears `LPFC_SLI_ACTIVE`, reinitializes CPU mapping, reenables interrupts, recomputes affinity, and returns recovered. Actual SLI restart is deferred to `lpfc_io_resume_s4()` because the function reset mailbox needs DMA enabled.

## State and Persistence Behavior

- The persistent driver object is `struct lpfc_hba`; this chunk mutates fields across PCI lifecycle: `sli_rev`, `pci_dev_grp`, BAR addresses, register pointers, `intr_type`, `intr_mode`, `cfg_irq_chann`, queue-resource counts, SLI4 capability descriptors, link/topology settings, congestion settings, NVMe support, and feature flags.
- SLI4 READ_CONFIG values persist in `phba->sli4_hba.max_cfg_param`, `lnk_info`, `bbscn_params`, `fawwpn_flag`, `conf_trunk`, `extents_in_use`, and queue-related config. These values drive later queue allocation and XRI/IOCB reservations.
- Persistent topology support sets `HBA_PERSISTENT_TOPO` and can override `cfg_topology` from firmware state. Invalid or unsupported persistent topology falls back to module parameters.
- Forced link speed from READ_CONFIG sets `HBA_FORCED_LINK_SPEED` and rewrites `cfg_link_speed`.
- Congestion management initializes a coherent `lpfc_cgn_info` buffer, atomics, timestamps, frequency defaults, and CRC. Registration is firmware-visible through `REG_CONGESTION_BUF`; unregister stops CMF first.
- Queue state spans firmware queue IDs, host descriptors, child lists, `lpfc_wq_list`, `cq_lookup`, CPU maps, per-HDWQ stats, and the queue-free flags used to coordinate teardown.
- Interrupt state persists in `phba->intr_type`, `phba->intr_mode`, `phba->sli.slistat.sli_intr`, `sli4_hba.hba_eq_hdl[]`, and affinity masks. CPU-hotplug registration is per-HBA and must be removed before full teardown.
- The firmware update path persists firmware to the adapter by streaming `.grp` file contents through DMA buffers to `lpfc_wr_object()`. It skips update when image revision matches current firmware.
- Module-level state includes the PCI driver registration, FC transport templates, misc device `lpfcmgmt`, dynamic CPU-hotplug state ID, `lpfc_pldv_detect`, `lpfc_present_cpu`, and `lpfc_hba_index`.
- The debug ring buffer state uses atomics `dbg_log_idx`, `dbg_log_cnt`, and `dbg_log_dmping`; `lpfc_dmp_dbg()` drains it to dev_info and resets the count.

## Dependencies and Integration Points

- Linux PCI core: `pci_register_driver`, `pci_alloc_irq_vectors`, `pci_irq_vector`, `pci_irq_get_affinity`, `pci_enable_device_mem`, `pci_restore_state`, `pci_save_state`, `pci_disable_device`, `pci_disable_sriov`, AER callbacks, PCI BAR resource APIs, and config-space reads/writes.
- Linux interrupt and CPU-hotplug APIs: `request_irq`, `request_threaded_irq`, `free_irq`, affinity masks, `irq_set_affinity`, `cpuhp_setup_state_multi`, per-HBA cpuhp instances, RCU synchronization, and timers.
- Linux DMA/I/O mapping APIs: `dma_set_mask_and_coherent`, `dma_set_max_seg_size`, `dma_alloc_coherent`, `dma_free_coherent`, `ioremap`, `iounmap`, `readl`, `writel`, and ordered PCI config reads for flushes.
- SCSI and FC transport layers: `Scsi_Host`, `scsi_host_set_prot`, `scsi_host_set_guard`, `fc_attach_transport`, `fc_release_transport`, `fc_remove_host`, `scsi_remove_host`, `fc_host_post_vendor_event`, NPIV vport termination, and host/vport sysfs/debugfs integration.
- LPFC internal subsystems: SLI mailbox commands (`lpfc_sli_issue_mbox`, `lpfc_sli_issue_mbox_wait`, `lpfc_sli4_config`), queue create/destroy functions, ring/IO abort/flush paths, worker thread `lpfc_do_work`, memory pools, debugfs, NVMe/NVMeT transport hooks, RAS firmware logging, CMF/FPIN congestion management, and vport/static-vport helpers.
- Linux firmware loader: `request_firmware_nowait`, `request_firmware`, `release_firmware`; image validation depends on LPFC group-header format and ASIC generation magic constants.
- Kernel module integration: `module_init`, `module_exit`, `MODULE_DEVICE_TABLE`, `MODULE_LICENSE`, `MODULE_DESCRIPTION`, `MODULE_AUTHOR`, and `MODULE_VERSION`.

## Risks and Edge Cases

- Initialization/unwind ordering is critical. Many routines assume partially initialized fields are either valid or NULL; mismatched cleanup can double-free queues, unmap uninitialized BARs, or leave interrupts active against freed state.
- SLI4 queue teardown waits indefinitely while `LPFC_QUEUE_FREE_WAIT` remains set. Bugs in queue users can hang remove/reset/suspend paths.
- `lpfc_sli4_xri_exchange_busy_wait()` waits forever after the initial timeout, logging periodically. This prevents unsafe reset/unload while exchange-busy lists are non-empty, but it can make device removal hang if completions never arrive.
- `lpfc_pci_function_reset()` treats port-not-ready and RN-after-reset as fatal and logs a board-mode firmware reset hint. Register-read failures or stale status on if-type 2/6 abort the bring-up path.
- `lpfc_sli4_read_config()` computes `qmin -= 4` after using firmware max WQ/CQ counts; extremely small queue-count responses would underflow as an unsigned value unless firmware guarantees enough slow-path resources.
- CPU affinity mapping depends on present/possible CPU masks, PCI managed affinity, NUMA masks, and hyperthread detection. Hotplug code must not race with unload; `FC_UNLOADING` and cpuhp removal/synchronize_rcu are used to reduce this risk.
- In SLI4 MSI-X setup, partial vector allocation failure must unwind only already requested IRQs and clear affinity flags. Any stale `eqhdl->irq` or handler state risks freeing the wrong IRQ later.
- Firmware update validates magic values by adapter generation and logs detailed failures, but the async `request_firmware_nowait()` callback carries `phba` as context. The broader driver must ensure the HBA is not freed while an internal firmware update callback may still run.
- Congestion-buffer CRC and endian fields must match firmware expectations. Any structure layout/version drift affects CMF/FPIN behavior.
- Suspend/resume paths restart worker threads and interrupts but are intentionally minimal; failures after worker-thread creation can leave partially resumed state unless higher-level PM recovery handles it.
- SLI3 and SLI4 dispatch wrappers depend on `phba->pci_dev_grp`. Corruption or incomplete probe setup routes removal/PM/AER to the wrong generation path.

## Test Signals

- Successful SLI4 probe should log PCI memory setup, interrupt mode, CPU affinity assignments (`3333`/`3335`/`3336` style messages), queue setup messages for EQ/CQ/WQ/MQ/RQ, SCSI scan (`0428`), adapter-arrival vendor event, and optional NVMe localport registration.
- SLI3 probe should show accepted interrupt mode only after active interrupt testing; fallback messages indicate MSI-X/MSI problems but can be valid if INTx succeeds.
- READ_CONFIG and GET_SLI4_PARAMETERS logs should show sane resource counts, topology selection, congestion registration choices, firmware NVMe support, embedded I/O settings, and no mailbox status/add-status failures.
- Queue failure testing should verify `lpfc_sli4_queue_create()` and `lpfc_sli4_queue_setup()` unwind through `queue_destroy`/`queue_unset` without leaked DMA memory, leaked IRQs, or stale `cq_lookup`.
- Removal tests should confirm sysfs/debugfs removal, vport termination, FC/SCSI host removal, NVMe/NVMeT teardown, congestion unregister, interrupt disable, queue destroy, BAR unmap, PCI disable, and HBA free complete without use-after-free warnings.
- PCI AER tests should exercise normal, frozen, permanent, and unknown states for both SLI3 and SLI4 and verify returned `pci_ers_result_t` values, `HBA_PCI_ERR` gating, slot-reset reinitialization, and `io_resume` online behavior.
- CPU-hotplug tests should verify EQ polling starts when the last CPU for an IRQ vector is going offline, stops when its mapped CPU returns online, and affinity is restored for NUMA/non-hyperthread modes.
- Firmware-update tests should cover matching revision skip, unsupported magic/generation, administrative lockout, DMA allocation failure, object-write failure, and async callback completion.
- Congestion/RAS tests should validate buffer CRC updates, register/unregister mailbox success/failure handling, CMF stop on unregister, and RAS enablement only for supported generations/functions.

## Unresolved Cross-Chunk References

- The actual implementations of `lpfc_sli4_hba_setup()`, `lpfc_sli4_driver_resource_setup()`, mailbox builders, queue create/destroy helpers, NVMe/NVMeT transport handlers, and most constants/bitfield macros are outside this chunk. This chunk shows how they are sequenced and how their results are persisted, but full semantics require the earlier declarations and helper definitions in neighboring files/chunks.
- The beginning of `lpfc_init.c` defines device IDs, module parameters, global state, and common resource setup/cleanup used heavily here.
