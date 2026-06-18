# subset-b-005358 grouped source research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/smartpqi_sas_transport.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/smartpqi_sas_transport.c

Purpose: this file adapts the Microchip SmartPQI controller driver to the Linux SAS transport class. It creates transport objects for the controller SAS host, per-device SAS ports, PHYs, and remote PHYs, and provides the `sas_function_template` callbacks used by sysfs and BSG/SMP paths.

Important APIs, types, and functions: local helpers allocate and tear down `pqi_sas_node`, `pqi_sas_port`, and `pqi_sas_phy` wrappers around `sas_port`, `sas_phy`, and `sas_rphy`. `pqi_add_sas_host()` creates the controller node, a host port, and a synthetic PHY using `ctrl_info->sas_address`; `pqi_delete_sas_host()` frees the whole node tree. `pqi_add_sas_device()` allocates a port/rphy for a `pqi_scsi_dev`, selects expander or end-device rphy allocation, and sets target protocols from Smart Array device type. `pqi_remove_sas_device()` reverses that link. `pqi_find_device_by_sas_rphy()` maps transport objects back to driver devices.

Control flow: add paths build Linux transport objects first, publish them with `sas_port_add()`, `sas_phy_add()`, and `sas_rphy_add()`, then link the driver-side device pointer. Remove paths walk list heads with safe iteration, delete PHYs from ports, delete ports, and clear `device->sas_port`. SMP BSG handling validates the target is a fanout expander and that request/reply payloads are single-SG, builds a CSMI SMP passthrough buffer, calls `pqi_csmi_smp_passthru()`, copies firmware response data back to BSG buffers, and finishes with `bsg_job_done()`.

State and persistence: no on-disk state exists. Runtime state is held in `ctrl_info->sas_host`, each `pqi_scsi_dev->sas_port`, Linux SAS class devices, and linked lists under each node/port. Enclosure and bay identifiers are derived on demand under `scsi_device_list_lock` from discovered PQI device metadata and enclosure WWIDs.

Dependencies and integration: depends on `smartpqi.h`, the SCSI host/device layer, `scsi_transport_sas`, BSG, and CSMI/BMIC passthrough types implemented elsewhere in SmartPQI. The exported `pqi_sas_transport_functions` integrates with the SAS transport template used when the SmartPQI host is registered.

Risks: most PHY operation callbacks are stubs and report no link management support, so user actions such as speed setting and reset are no-ops. `pqi_build_csmi_smp_passthru_buffer()` uses the request SG count for `sg_copy_to_buffer()` but passes `job->reply_payload.sg_cnt`, which should be reviewed carefully because it can under-copy or over-trust a reply count. Identifier lookup relies on enclosure metadata conventions such as `box_index`, `phys_box_on_bus`, `bay`, connector bytes, and VSEP drive number.

Test signals: useful validation includes hot add/remove of SAS and SATA devices, expander SMP passthrough through `sg_ses` or `smp_utils`, sysfs SAS enclosure/bay identifiers, failure injection for `sas_*_alloc/add` errors, and lockdep/KASAN coverage around device removal while transport attributes are queried.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/smartpqi_sas_transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/smartpqi_sis.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/smartpqi_sis.c

Purpose: this file implements the Smart Array legacy SIS mailbox/doorbell interface used before or beside PQI mode. It waits for controller readiness, sends synchronous SIS commands, discovers PQI capabilities, initializes the PQI base structure, toggles interrupt/reset/shutdown bits, and waits for firmware triage or controller logging to finish.

Important APIs, types, and functions: `sis_wait_for_ctrl_ready()` and `sis_wait_for_ctrl_ready_resume()` poll `sis_firmware_status` for `SIS_CTRL_KERNEL_UP` and fail on `SIS_CTRL_KERNEL_PANIC`. `sis_send_sync_cmd()` is the central mailbox command routine for `SIS_CMD_GET_ADAPTER_PROPERTIES`, `SIS_CMD_GET_PQI_CAPABILITIES`, and `SIS_CMD_INIT_BASE_STRUCT_ADDRESS`. `sis_get_ctrl_properties()` validates extended properties and marks `pqi_reset_quiesce_supported`. `sis_get_pqi_capabilities()` fills controller queue and config-table limits. `sis_init_base_struct_addr()` builds a DMA-mapped `sis_base_struct`. Doorbell helpers implement MSI-X/INTx enable, SIS mode reenable, reset quiesce, kdump notification, soft reset, and shutdown.

Control flow: synchronous SIS commands write command and parameters into mailbox registers, clear controller-to-host doorbell, mask interrupts, force the mask write to post via readback, ring host-to-controller `SIS_CMD_READY`, poll for `SIS_CMD_COMPLETE`, validate mailbox status, then read return mailboxes. The base-structure path allocates an aligned structure, fills little-endian physical error-buffer metadata from `ctrl_info`, maps it for DMA, passes the DMA address via mailboxes, then unmaps and frees it.

State and persistence: state is entirely MMIO and `pqi_ctrl_info` runtime fields. The global `sis_ctrl_ready_timeout_secs` controls the normal ready wait. The driver scratch register is a small persistent controller register exposed through `sis_write_driver_scratch()` and `sis_read_driver_scratch()`, but this file does not persist data to disk.

Dependencies and integration: depends on `smartpqi.h`, PCI DMA mapping, jiffies polling, and unaligned endian helpers. It is called by SmartPQI initialization, reset, resume, shutdown, kdump, and diagnostic flows before normal PQI operational queues are available.

Risks: all waits are polling loops, so timeout constants directly affect boot, resume, reset, and panic paths. Hardware disappearance can appear as all-ones status and is only partly distinguished from panic/offline. Doorbell helper return values are ignored by `sis_enable_msix()` and `sis_enable_intx()`, so failures there may only surface later. The packed base structure is protocol-critical, making the `BUILD_BUG_ON()` checks essential.

Test signals: validate with controllers in cold boot, resume, kdump, firmware panic, reset-quiesce supported/unsupported, and shutdown paths. Fault injection should cover DMA mapping failure, mailbox timeout, non-success command status, and doorbell bit never clearing. Compile-time structure layout checks are built into `sis_verify_structures()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/smartpqi_sis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/smartpqi_sis.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/smartpqi_sis.h

Purpose: this header exposes the SmartPQI SIS interface functions implemented in `smartpqi_sis.c` to the rest of the SmartPQI driver.

Important APIs, types, and functions: it declares readiness checks, firmware-running and kernel-up queries, controller property and PQI capability discovery, base-structure initialization, interrupt mode selection, shutdown/reset/quiesce operations, scratch register access, product-id readout, firmware triage wait, controller logging support/wait, kdump notification, and `sis_verify_structures()`. It also declares the tunable `sis_ctrl_ready_timeout_secs`.

Control flow: consumers include this header after `struct pqi_ctrl_info` and `enum pqi_ctrl_shutdown_reason` are visible from `smartpqi.h`. Calls normally occur in controller initialization order: wait ready, get properties, get capabilities, initialize base structure, enable interrupt mode, then proceed to PQI setup. Reset and crash paths call the doorbell helpers later in the lifecycle.

State and persistence: this header owns no state. It exposes functions that mutate or observe MMIO state through `pqi_ctrl_info` and a single exported timeout variable.

Dependencies and integration: it is tightly coupled to SmartPQI internal controller types and to the SIS register layout in `smartpqi.h`. It has include guards and no standalone Linux includes, relying on including translation units for type visibility.

Risks: because it exposes low-level controller lifecycle operations, mismatched ordering by callers can leave firmware in the wrong mode. The external timeout variable is global across controllers, so module parameter or debug modification affects all adapters.

Test signals: build coverage should catch prototype drift with `smartpqi_sis.c`; runtime testing should verify each declared operation is called in expected probe, resume, shutdown, kdump, and reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/smartpqi_sis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sni_53c710.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sni_53c710.c

Purpose: this is a small platform driver for SNI RM systems using an NCR/Symbios 53c710 SCSI controller. It binds platform device `snirm_53c710`, configures the generic `53c700` core, requests the IRQ, and registers a SCSI host.

Important APIs, types, and functions: `snirm710_template` supplies a `scsi_host_template` with host id 7. `snirm710_probe()` obtains the memory resource, allocates `NCR_700_Host_Parameters`, maps the 0x100-byte MMIO window, sets clock/endian/chip/burst parameters, calls `NCR_700_detect()`, requests `NCR_700_intr`, stores the host in driver data, and starts `scsi_scan_host()`. `snirm710_driver_remove()` removes the SCSI host, releases the NCR core, frees the IRQ, unmaps MMIO, and frees host parameters.

Control flow: platform probe is linear: resource lookup, hostdata allocation, DMA mask setup, `ioremap`, core detect, IRQ lookup/request, SCSI scan. Each failure jumps to cleanup labels that release the host and hostdata. Remove is the inverse path after `scsi_remove_host()`.

State and persistence: no persistent state exists. Runtime state is `Scsi_Host`, `NCR_700_Host_Parameters`, MMIO mapping, IRQ registration, and platform driver data.

Dependencies and integration: depends on platform devices, generic `53c700` driver helpers, Linux SCSI mid-layer, SPI transport includes, and 32-bit DMA capability. It is registered via `module_platform_driver()`.

Risks: `dma_set_mask()` return is not checked. The probe failure path always returns `-ENODEV`, even for allocation or IRQ errors, which loses diagnostic precision. `hostdata->base` is not checked after `ioremap()`. IRQ request failure also maps to `-ENODEV`. The code assumes fixed clock and initiator ID suitable for SNI RM hardware.

Test signals: boot on matching SNI RM hardware or platform emulation should show host registration and scan. Negative tests should cover missing MEM resource, missing IRQ, failed `NCR_700_detect()`, and remove/unbind with outstanding devices. Static analysis can flag unchecked mapping and DMA mask returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sni_53c710.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/Makefile

Purpose: this Makefile defines the object composition for the Cisco SNIC SCSI driver.

Important APIs, types, and functions: it builds `snic.o` when `CONFIG_SCSI_SNIC` is enabled. The base object list includes sysfs attributes, main PCI/SCSI lifecycle, vNIC resource setup, interrupt handling, control/version exchange, request allocation, SCSI command/error handling, discovery, completion queue support, interrupt control, devcmd support, and work queue support. With `CONFIG_SCSI_SNIC_DEBUG_FS`, it also includes debugfs and trace files.

Control flow: Kbuild combines the listed `snic-y` objects into one module or built-in object. Conditional `snic-$(CONFIG_SCSI_SNIC_DEBUG_FS)` keeps trace/debugfs code out when the option is disabled while preserving stubs/macros in headers.

State and persistence: no runtime state is defined here, but build-time selection determines whether debugfs state and trace buffers exist in `struct snic_global` and per-host structures.

Dependencies and integration: this Makefile assumes neighboring vNIC support files such as `vnic_wq.c`, headers, and resource definitions are in the same directory and compiled as part of the SNIC driver.

Risks: object ordering matters only for link completeness, but omitting a core object would surface as unresolved symbols. Debugfs-dependent declarations must remain protected by `CONFIG_SCSI_SNIC_DEBUG_FS` to avoid link failures in non-debug builds.

Test signals: build with `CONFIG_SCSI_SNIC=m/y` and with debugfs enabled and disabled. Module load should expose the same PCI ID support in both builds, with only debugfs files differing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/cq_desc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/cq_desc.h

Purpose: this header defines the common 16-byte vNIC completion queue descriptor layout and decoding helper.

Important APIs, types, and functions: `enum cq_desc_types` assigns descriptor types for WQ/RQ/FCP/copy completions. `struct cq_desc` contains completed index, queue number, type-specific bytes, and a combined type/color byte. `cq_desc_dec()` extracts color, type, queue number, and completed index using masks.

Control flow: completion service loops call `cq_desc_dec()` before consuming an entry. The helper reads the color bit first, issues `rmb()`, then reads the rest of the descriptor. This matches the hardware contract that color is written last and prevents stale descriptor fields.

State and persistence: no state is stored here. State is in hardware-owned CQ rings and consumer fields such as `vnic_cq.to_clean` and `last_color`.

Dependencies and integration: included by Ethernet CQ descriptors and `vnic_cq.h`. It depends on little-endian conversion helpers and memory barriers from kernel headers included by users.

Risks: descriptor bit masks are protocol-critical. If hardware changes field widths or write ordering, all CQ consumers can mis-handle completions. The helper assumes descriptor memory is DMA coherent and color toggling is valid.

Test signals: exercise CQ wraparound, color toggles, and mixed descriptor types. Hardware or emulator tests should confirm completed indexes and queue numbers match WQ service expectations under interrupt load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/cq_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/cq_enet_desc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/cq_enet_desc.h

Purpose: this header defines the Ethernet work-queue completion descriptor format used by SNIC to acknowledge posted host request descriptors.

Important APIs, types, and functions: `struct cq_enet_wq_desc` mirrors the common 16-byte CQ descriptor with reserved type-specific bytes. `cq_enet_wq_desc_dec()` delegates to `cq_desc_dec()` to extract type, color, queue number, and completed index.

Control flow: SNIC's WQ completion path services CQ entries for posted host requests, decodes this descriptor, and then calls `svnic_wq_service()` to free or mark WQ buffers whose indexes have completed.

State and persistence: no state is held here. Descriptor state lives in the DMA CQ ring and in each WQ buffer's `os_buf`, DMA address, and posted indexes.

Dependencies and integration: includes `cq_desc.h` and is used by `snic_io.c` and `snic_res.c` when allocating and servicing the WQ-associated completion queue.

Risks: the file intentionally treats the descriptor as the generic `cq_desc`; any type-specific data added by hardware would be ignored. Correct memory ordering relies on `cq_desc_dec()`.

Test signals: WQ completion interrupt tests should verify that request DMA mappings are eventually unmapped or acknowledged and that ring indices are advanced correctly when the CQ wraps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/cq_enet_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic.h

Purpose: this is the central SNIC driver header. It defines driver identity, limits, command flag bits, state enums, debug macros, interrupt indexes, firmware info, per-adapter state, global state, and cross-file function prototypes.

Important APIs, types, and functions: the most important types are `struct snic`, `struct snic_global`, `struct snic_fw_info`, `struct snic_work`, and MSI-X entry/state enums. Macros such as `CMD_SP`, `CMD_STATE`, `CMD_FLAGS`, `CMD_ABTS_STATUS`, and `CMD_LR_STATUS` access per-command private state allocated through `scsi_host_template.cmd_size`. Tag high bits `SNIC_TAG_ABORT`, `SNIC_TAG_DEV_RST`, and `SNIC_TAG_IOCTL_DEV_RST` multiplex task-management completions. Logging, soft-assert, and trace macros are also defined here.

Control flow: all SNIC implementation files include this header to share the adapter state. Probe initializes `struct snic`, resources fill its `vdev`, WQ/CQ/INTR arrays, discovery fills `disc`, SCSI queueing uses request pools and hashed locks, and ISR/completion handlers dispatch through prototypes declared here.

State and persistence: runtime state includes adapter online/offline/reset state, firmware capabilities, discovery target list, vNIC BAR/resources, PCI device, interrupts, mempools, special untagged request list, per-command locks, work items, and debugfs handles. There is no disk persistence.

Dependencies and integration: this header ties the SCSI mid-layer, PCI/vNIC resource layer, discovery layer, stats, trace, and firmware-interface headers together. It is therefore a high-coupling point for the SNIC module.

Risks: command state is spread across private SCSI command memory and `snic_req_info`, so locking discipline around `CMD_SP` is critical. Many `SNIC_BUG_ON` checks become `WARN_ON_ONCE` in non-debug builds, allowing execution to continue after invariant violations. Constants assume one WQ and one firmware CQ lane. Debug macros can emit verbose logs in hot paths.

Test signals: build variants should cover debugfs enabled/disabled, queue depth parameters, and all SCSI EH callbacks. Lockdep and KCSAN are valuable around command state flags, `snic_lock`, host lock, and hashed request locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_attrs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_attrs.c

Purpose: this file exposes SNIC host attributes through SCSI host sysfs groups.

Important APIs, types, and functions: show callbacks return the adapter symbolic name, driver state string, driver version, and link state. `snic_show_link_state()` refreshes link status from `svnic_dev_link_status()` for direct-attached SNIC_DAS configurations. `snic_host_groups` exports the attribute group to the `scsi_host_template`.

Control flow: sysfs reads resolve the `Scsi_Host` through `class_to_shost(dev)`, then read `struct snic` via `shost_priv()`. Values are emitted with `sysfs_emit()`. There are no store callbacks; all attributes are read-only.

State and persistence: the file only observes runtime fields: `snic->name`, `snic->state`, `snic->config.xpt_type`, and `snic->link_status`. No persistent configuration is accepted.

Dependencies and integration: depends on `snic_state_str`, `snic_get_state()`, `SNIC_DRV_VERSION`, and the vNIC notify path. The attribute group is referenced by `snic_host_template.shost_groups` in `snic_main.c`.

Risks: the state string is indexed by `snic_get_state()` without a local bounds check, relying on state enum integrity. Link state reads may touch the notify buffer and cached checksum path, so sysfs reads can reflect stale or unavailable firmware notify data.

Test signals: verify `/sys/class/scsi_host/host*/snic_sym_name`, `snic_state`, `drv_version`, and `link_state` during online, offline, and removal windows. KASAN/lockdep testing should cover concurrent sysfs reads and PCI unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_attrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_ctl.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_ctl.c

Purpose: this file implements SNIC control-plane requests that are sent over the normal firmware work queue, primarily link events and exchange-version negotiation.

Important APIs, types, and functions: `snic_handle_link()` reads link status/down counts and currently asserts not implemented for non-DAS link handling. `snic_ver_enc()` converts dotted driver version text to a 32-bit firmware value. `snic_queue_exch_ver_req()` allocates an untagged request, encodes `SNIC_REQ_EXCH_VER`, adds it to `spl_cmd_list`, and queues it. `snic_io_exch_ver_cmpl_handler()` decodes firmware version, host id, max concurrent I/O, max SGs, max I/O size, max targets, I/O timeout, and adjusts `shost` limits. `snic_get_conf()` synchronously retries exchange-version up to three times with a stack completion.

Control flow: probe calls `snic_get_conf()` after queues and interrupts are enabled. That function clears `fwinfo`, installs a completion pointer under `snic_lock`, delays for hardware resource initialization, queues exchange-version, waits up to two seconds per attempt, and clears the wait pointer on success or final failure. The completion handler runs from firmware CQ interrupt context, fills `fwinfo`, completes the waiter, and releases the untagged request.

State and persistence: `snic->fwinfo` is the key mutable state. Untagged control requests live on `snic->spl_cmd_list` until completion or cleanup. Link status is cached in `snic->link_status` and `link_down_cnt`.

Dependencies and integration: uses `snic_req_init()`, `snic_handle_untagged_req()`, `snic_queue_wq_desc()`, `snic_release_untagged_req()`, firmware wire structs from `snic_fwint.h`, and vNIC notify helpers.

Risks: link handling intentionally calls `SNIC_ASSERT_NOT_IMPL(1)` for non-DAS events. Exchange-version failure blocks probe. Completion assumes returned `hid` matches config and adjusts SCSI limits at runtime. The version parser returns `-1` for invalid strings, which is then cast to `u32` in the request field.

Test signals: probe should show exchange-version completion and populated firmware limits. Tests should cover ignored first exchange request, firmware max SG smaller/larger than driver max, zero or invalid firmware version response, and link event interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_ctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_debugfs.c

Purpose: this optional file creates debugfs directories and files for SNIC statistics and trace output when `CONFIG_SCSI_SNIC_DEBUG_FS` is enabled.

Important APIs, types, and functions: `snic_debugfs_init()` creates `/sys/kernel/debug/snic` and a `statistics` child directory. `snic_stats_debugfs_init()` creates per-host `stats` and `reset_stats` files. `snic_stats_show()` formats I/O, abort, reset, firmware, and miscellaneous counters. `snic_reset_stats_write()` toggles `snic->reset_stats` and zeroes cumulative counters while preserving active counts. Trace helpers create `tracing_enable` and `trace`, with seq operations pulling records from `snic_get_trc_data()`.

Control flow: global debugfs setup happens during SNIC global initialization; per-host setup happens in probe before PCI resource setup and is removed in probe failure/remove. Reading `stats` is a seq-file snapshot of atomic counters. Writing `reset_stats` copies a small user buffer, parses an integer, and resets counters when nonzero. Reading `trace` drains one formatted trace record per seq show call.

State and persistence: state is debugfs dentries in `snic_global` and per `struct snic`, atomic stats in `snic->s_stats`, `snic->reset_stats`, and the trace ring. Debugfs content is runtime-only and disappears when the module unloads.

Dependencies and integration: depends on Linux debugfs, seq-file helpers, SNIC stats definitions, and trace APIs from `snic_trc.c`. It uses `simple_read_from_buffer()` and `copy_from_user()`.

Risks: stats reset uses raw `memset()` over structures containing atomics, which is common in older driver code but deserves care under concurrent updates. Debugfs creation return values are not checked. Trace reads are destructive because `snic_get_trc_data()` advances `rd_idx`.

Test signals: with debugfs enabled, verify directory/file creation and removal across probe/unbind, stats values changing under I/O, reset_stats behavior with valid/invalid writes, and trace enable/disable. Run with CONFIG_DEBUG_ATOMIC_SLEEP and lockdep during concurrent reads and I/O completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_disc.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_disc.c

Purpose: this file implements SNIC target discovery and target device lifecycle. It sends report-targets firmware requests, converts returned target IDs into Linux device objects, starts SCSI scans, and removes targets safely during unbind or target deletion.

Important APIs, types, and functions: `snic_disc_init()`, `snic_disc_start()`, and `snic_disc_term()` manage discovery state. `snic_queue_report_tgt_req()` allocates a request plus DMA response buffer and queues `SNIC_REQ_REPORT_TGTS`. `snic_report_tgt_cmpl_handler()` handles firmware completion, stores target response data, and queues `tgt_work`. `snic_tgt_create()` creates `struct snic_tgt`, initializes an embedded `struct device`, assigns `scsi_tgt_id`, adds it to `disc.tgt_list`, and queues scan work. `snic_tgt_del_all()` queues deletion work for all targets.

Control flow: discovery starts by checking `in_remove`, transitioning `disc.state` to pending, and posting a report-targets request. Completion unmaps the DMA response, transfers ownership of the response buffer to discovery work when targets exist, and releases the untagged request. Target discovery work restarts discovery if a request arrived while one was in progress; otherwise it creates targets and queues `scsi_scan_target()`. Deletion blocks target I/O, aborts outstanding target commands, unblocks offline, removes SCSI target children, deletes the device, and drops the reference.

State and persistence: discovery state lives in `struct snic_disc`: target list, mutex, state, pending request count, next SCSI target id, response target count, and response buffer pointer. Each `struct snic_tgt` stores hardware target id, synthetic SCSI target id, state, flags, device, and work items. No persistent storage exists.

Dependencies and integration: depends on firmware request formats, SNIC request allocation/WQ queueing, SCSI scan/remove/block APIs, host lock, and the global ordered event workqueue.

Risks: discovery uses both mutex and host lock, and target deletion has to coordinate with scan work and outstanding SCSI commands. Several `SNIC_BUG_ON` checks trust firmware target counts and types. Response buffer lifetime crosses interrupt and workqueue contexts. `disc_timeout` exists in the header but is not used here.

Test signals: validate initial discovery, repeated discovery while pending, no-target response, max-target boundary, target add/remove, PCI unbind during discovery, and deletion with outstanding I/O. Device model reference counting should be checked with KASAN and driver-core debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_disc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_disc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_disc.h

Purpose: this header defines SNIC discovery state, target objects, target states, and discovery-related APIs shared across the SNIC driver.

Important APIs, types, and functions: `enum snic_disc_state`, `struct snic_disc`, `enum snic_tgt_state`, `struct snic_tgt_priv`, and `struct snic_tgt` describe discovery and targets. Inline helpers map devices and SCSI targets to SNIC targets, test whether a `struct device` belongs to SNIC, convert targets to `Scsi_Host`, and check target readiness. Function declarations cover discovery init/start/term, report-target and target-info completions, discovery work, target release/deletion, and target I/O abort.

Control flow: `snic_main.c` initializes `snic->disc` and work items, `snic_disc.c` fills the target list, and `snic_scsi.c` uses `starget_to_tgt()` and `snic_tgt_chkready()` before queueing commands or selecting task-management behavior.

State and persistence: the header defines runtime-only structures. `disc.tgt_list`, `disc.state`, `disc.req_cnt`, `disc.rtgt_info`, and `snic_tgt.state/flags` drive target availability. `snic_tgt.dev.release` is used to verify SNIC target devices.

Dependencies and integration: includes `snic_fwint.h` for target wire types. It integrates Linux device model, SCSI target structures, workqueues, and SNIC firmware discovery responses.

Risks: `name` in `struct snic_tgt_priv` is declared as `char *name[SNIC_TGT_NAM_LEN]`, an array of pointers, not a character buffer; it is unused here but easy to misuse. `snic_tgt_chkready()` assumes non-null target pointers in callers unless checked earlier.

Test signals: build and runtime tests should exercise `starget_to_tgt()` for SNIC and non-SNIC parent devices, target readiness transitions, and target deletion while SCSI mid-layer still holds references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_disc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_fwint.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_fwint.h

Purpose: this header defines the SNIC host-to-firmware and firmware-to-host wire protocol. It contains request/response opcodes, status codes, common headers, payload structures, color-bit helpers, and sizing constants.

Important APIs, types, and functions: `enum snic_io_type` defines request, completion, ACK, and async event message types. `enum snic_io_status` maps firmware completion statuses to driver behavior. `struct snic_io_hdr` is the common message header encoded/decoded by `snic_io_hdr_enc()` and `snic_io_hdr_dec()`. Payloads include exchange-version, report-targets, initiator command, task management, HBA reset, notify, and async event structures. `struct snic_host_req` is the 128-byte host request format, and `struct snic_fw_req` is the 64-byte firmware completion format. `snic_color_enc()` and `snic_color_dec()` manage completion color.

Control flow: control, discovery, SCSI I/O, task-management, reset, and CQ service paths all fill or parse these structures. Host requests are DMA-mapped and posted to the vNIC WQ. Firmware completions are consumed from the firmware CQ, decoded by type/status, and dispatched by `snic_io_cmpl_handler()`.

State and persistence: no software state is persisted here, but the structures define in-memory DMA ABI shared with firmware. Fields such as host id, command id, initiator context, SG counts, target/lun ids, sense address, and async event ids are runtime protocol state.

Dependencies and integration: used by nearly every SNIC implementation file, especially `snic_ctl.c`, `snic_disc.c`, `snic_res.h`, `snic_scsi.c`, and `vnic_cq_fw.h`. It assumes kernel endian types and memory barriers are available.

Risks: ABI drift is high risk because most structures have fixed expected sizes but `VERIFY_REQ_SZ` and `VERIFY_CMPL_SZ` are empty macros in this snapshot. `ulong init_ctx` is embedded in DMA-visible protocol and assumes host/firmware compatibility for pointer-width context. Color bit placement in the last byte is protocol-critical.

Test signals: firmware interoperability tests should cover every request/completion type, each status mapping, 32-bit and 64-bit build assumptions where relevant, CQ color wrap, endian correctness, and structure size/layout validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_fwint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_io.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_io.c

Purpose: this file provides common request allocation, WQ descriptor queueing, WQ completion acknowledgement, untagged request tracking, DMA unmapping, descriptor debugging, and simple timing stats for SNIC.

Important APIs, types, and functions: `snic_queue_wq_desc()` maps a request buffer for DMA, checks WQ descriptor availability, posts an Ethernet WQ descriptor, and increments active firmware request stats. `snic_req_init()` allocates `snic_req_info` plus `snic_host_req` and optional SG descriptors from the correct mempool. `snic_abort_req_init()` and `snic_dr_req_init()` allocate task-management request buffers. `snic_req_free()` unmaps request/abort/reset DMA mappings and returns memory to pools. `snic_handle_untagged_req()`, `snic_release_untagged_req()`, and `snic_free_all_untagged_reqs()` maintain `spl_cmd_list`. `snic_wq_cmpl_handler()` services WQ ACK completions.

Control flow: SCSI, discovery, and control paths allocate request info, initialize firmware payloads, and call `snic_queue_wq_desc()`. WQ completions arrive on CQ0 and clear `buf->os_buf` through `snic_wq_cmpl_frame_send()`. Error/remove paths clean WQ buffers and untagged requests, unmapping response buffers when present.

State and persistence: state is mempool-backed request objects, DMA mappings in request fields, WQ ring state, `fw.actv_reqs`, `spl_cmd_list`, and per-request response buffer addresses. No persistent state exists.

Dependencies and integration: depends on vNIC WQ/CQ helpers, firmware wire structs, SNIC stats, PCI DMA APIs, SCSI DMA APIs indirectly through request users, and locks in `struct snic`.

Risks: `snic_req_init()` selects default vs max SG pool using `sg_cnt <= SNIC_REQ_CACHE_DFLT_SGL`, comparing SG count to enum value 0 rather than descriptor capacity; any nonzero SG count goes to max pool. WQ availability is global and assumes one queue. Request lifetime is split between WQ ACK, firmware completion, and cleanup paths, so double-free and stale DMA mapping risks are concentrated here.

Test signals: run I/O with SG counts 0, 1, 32, 60, queue-full conditions, DMA mapping failures, control request cleanup during remove, and WQ CQ wraparound. KASAN/DMA-API debug should catch mapping lifetime mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_io.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_io.h

Purpose: this header defines SNIC request allocation sizes, SG descriptor formats, per-SCSI-command private state, request-info state, and request helper prototypes.

Important APIs, types, and functions: `struct snic_sg_desc`, `struct snic_dflt_sgl`, and `struct snic_max_sgl` define DMA SG entries. `enum snic_req_cache_type` selects mempools for default SG, max SG, and task-management request buffers. `struct snic_internal_io_state` is stored in `scsi_cmnd` private memory and carries request pointer, flags, state, abort status, and LUN reset status. `struct snic_req_info` ties a firmware request to a SCSI command, target id, DMA response buffer, abort/reset request buffers, and completions. Macros convert between request info, request, and SGL memory.

Control flow: queueing allocates `snic_req_info`, stores it in `CMD_SP(sc)`, initializes `rqi->req`, posts the request, and later completion/error paths use `req_to_rqi()` or `CMD_SP()` to find state and free it.

State and persistence: all structures are runtime-only. They are the core state machines for command lifetime, task management, and cleanup.

Dependencies and integration: used by `snic_io.c`, `snic_scsi.c`, discovery, control, and resource helpers. It depends on firmware request type declarations from `snic_fwint.h` through including users.

Risks: the `CMD_SP` macro stores `struct snic_req_info *` as `char *`, so type discipline is manual. `req_to_rqi()` trusts `hdr.init_ctx`, which is firmware-visible and must not be corrupted. Cache sizing and 16-byte alignment must match DMA and firmware assumptions.

Test signals: allocation/free tests under memory pressure, task-management reuse, command timeout races, and DMA API debug are most valuable. Compile-time checks for cache object sizes and alignment would reduce risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_isr.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_isr.c

Purpose: this file manages SNIC MSI-X interrupt mode, requests/free IRQs, and implements the three interrupt handlers for WQ ACK completions, firmware I/O completions, and error/notify events.

Important APIs, types, and functions: `snic_isr_msix_wq()` services WQ completions and returns credits on `SNIC_MSIX_WQ`. `snic_isr_msix_io_cmpl()` services firmware CQ completions and returns credits on `SNIC_MSIX_IO_CMPL`. `snic_isr_msix_err_notify()` returns all credits, logs queue errors, and queues link handling. `snic_set_intr_mode()` allocates exactly three MSI-X vectors and sets vNIC interrupt mode. `snic_request_intr()` assigns names/handlers and calls `request_irq()`. `snic_free_intr()` and `snic_clear_intr_mode()` reverse setup.

Control flow: probe discovers resource counts, calls `snic_set_intr_mode()`, allocates resources, requests interrupts, then unmasks them. Each ISR updates stats, services the relevant queue, and returns vNIC interrupt credits so hardware can reassert interrupts.

State and persistence: runtime state includes `snic->msix[]`, `intr[]`, `intr_count`, `err_intr_offset`, and ISR stats. No persistent state exists.

Dependencies and integration: depends on PCI MSI-X APIs, vNIC interrupt credit helpers, SNIC WQ/FW CQ completion handlers, and queue error/link handlers.

Risks: only MSI-X is supported, with hard assertions if another mode is used. Resource counts must support one WQ, one firmware CQ, and one error/notify vector. Error/notify ISR queues link work that is partly unimplemented for non-DAS.

Test signals: probe on hardware with insufficient MSI-X vectors, IRQ request failure rollback, high-rate WQ and firmware CQ interrupts, error notify interrupts, and unbind while interrupts are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_isr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_main.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_main.c

Purpose: this is the SNIC PCI/SCSI driver entry point. It registers the PCI driver, creates global state, probes/removes adapters, configures the SCSI host template, and orchestrates vNIC, firmware, interrupt, mempool, debugfs, and discovery lifecycle.

Important APIs, types, and functions: `snic_host_template` wires queuecommand, SCSI EH abort/device reset/host reset callbacks, device init/configure callbacks, queue depth changes, host attributes, and command private size. `snic_probe()` is the main initialization path. `snic_remove()` performs teardown. `snic_global_data_init()` creates global request slab caches, event workqueue, and optional debugfs/trace. Module init/exit register and unregister the PCI driver.

Control flow: probe allocates `Scsi_Host`, enables PCI, requests BARs, sets DMA mask, maps BAR0, discovers vNIC resources, initializes devcmd2, opens and initializes the vNIC, reads vNIC config, configures queue limits and resource counts, sets MSI-X, allocates rings/interrupts, initializes locks and mempools, sets notify buffer, adds the adapter to the global list, enables WQs and vNIC, requests/unmasks interrupts, exchanges firmware version, adds the SCSI host, marks online, and starts discovery. Remove marks offline, stops link events, drains work, marks `in_remove`, cleans queues and SCSI commands, removes targets, removes debugfs and host, unregisters notify/interrupt/resources/vNIC/BAR/PCI, and drops the host.

State and persistence: global runtime state is `snic_glob`; per-adapter runtime state is `struct snic`. Module parameters include `snic_log_level`, `snic_max_qdepth`, and optional `snic_trace_max_pages`. No persistent storage is written.

Dependencies and integration: integrates Linux PCI, SCSI mid-layer, block queue timeout configuration, vNIC devcmd/resources, SNIC discovery/SCSI/control/ISR files, mempools/slab caches, workqueues, and debugfs.

Risks: the probe path is long with many cleanup labels; ordering mistakes can leak resources or use uninitialized debugfs handles. Debugfs per-host init happens before PCI enable, so early probe failures rely on cleanup. `snic_del_host()` returns early if `work_q` is null and then does not call `scsi_remove_host()`, which matters for partially added hosts. The driver taints non-x86_64 instead of refusing load. Only one hardware shape and MSI-X mode are effectively supported.

Test signals: test successful probe/remove, every probe failure label via fault injection, module unload with active I/O, firmware exchange timeout, discovery failure after host add, sysfs/debugfs lifetime, non-default queue depth, and SCSI EH host reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_res.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_res.c

Purpose: this file reads SNIC vNIC configuration, discovers resource counts, allocates/frees WQ/CQ/interrupt resources, initializes rings and interrupt controls, clears stats, and logs queue errors.

Important APIs, types, and functions: `snic_get_vnic_config()` reads fields from firmware using `svnic_dev_spec()` and clamps descriptor counts, MTU, throttle, timeout, retry, LUN, and interrupt timer values. `snic_get_res_counts()` reads WQ/CQ/INTR resource counts. `snic_alloc_vnic_res()` allocates WQs, WQ CQs, firmware CQs, and interrupt controls, initializes each, dumps/clears stats, and rolls back on failure. `snic_free_vnic_res()` and `snic_log_q_error()` free resources and report WQ error status.

Control flow: probe calls config read, resource count discovery, MSI-X setup, then resource allocation. Allocation first creates WQ rings, then CQs, then INTR controls, then initializes hardware registers. On any failure, it frees all resources allocated so far.

State and persistence: runtime state includes `snic->config`, `wq_count`, `cq_count`, `intr_count`, `wq[]`, `cq[]`, `intr[]`, `stats`, and queue error MMIO registers. No persistent state exists.

Dependencies and integration: depends on vNIC resource/control headers, WQ/CQ/INTR allocation APIs, firmware-specific config structure `vnic_snic_config`, and stats dump/clear devcmds.

Risks: the code asserts exactly MSI-X mode and `cq_count == 2 * wq_count`. It assumes one WQ and one firmware CQ in other files. Firmware config values are clamped, but resource counts are trusted after nonzero assertions. Stats dump failure aborts resource allocation.

Test signals: probe against minimum/maximum config values, insufficient CQ/INTR resources, descriptor allocation failure, stats dump failure, queue error injection, and ring cleanup after partial allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_res.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_res.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_res.h

Purpose: this header provides inline firmware request initialization helpers and the WQ Ethernet descriptor posting helper, plus resource-management prototypes.

Important APIs, types, and functions: `snic_icmnd_init()` fills a `SNIC_REQ_ICMND` request with command id, host id, context, flags, target/lun, CDB, data length, SGL address, sense address, and sense length. `snic_itmf_init()` fills a `SNIC_REQ_ITMF` task-management request. `snic_queue_wq_eth_desc()` obtains the next vNIC WQ descriptor, encodes a `wq_enet_desc`, and posts it through `svnic_wq_post()`.

Control flow: SCSI queueing and task-management paths initialize requests with these helpers before calling `snic_queue_wq_desc()`. That queueing routine maps the whole request buffer for DMA and then calls the WQ descriptor helper.

State and persistence: the header mutates request buffers and WQ ring state supplied by callers. It owns no state.

Dependencies and integration: includes SNIC I/O, WQ descriptor, vNIC WQ, firmware interface, and CQ firmware headers. It is shared by `snic_scsi.c`, `snic_res.c`, and queueing code.

Risks: helpers trust CDB length and caller-provided LUN pointer. `snic_itmf_init()` leaves timeout unfilled despite a timeout field in the wire structure. `snic_queue_wq_eth_desc()` hard-codes offload/vlan/fcoe fields for SNIC use and assumes a descriptor is available.

Test signals: validate encoded host requests with firmware or trace dumps for read, write, no-data, abort, LUN reset, and HBA reset requests. DMA/IOMMU testing should verify WQ descriptors point at mapped request buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_res.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_scsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_scsi.c

Purpose: this is the SNIC SCSI data path and error-handling engine. It queues SCSI commands to firmware, handles firmware completions, maps firmware statuses to SCSI results, processes task-management completions, implements abort/LUN reset/host reset callbacks, cleans pending commands, and aborts target I/O during target deletion.

Important APIs, types, and functions: public SCSI entry points are `snic_queuecommand()`, `snic_abort_cmd()`, `snic_device_reset()`, `snic_host_reset()`, `snic_reset()`, `snic_shutdown_scsi_cleanup()`, and `snic_tgt_scsi_abort_io()`. Completion dispatch enters through `snic_fwcq_cmpl_handler()` and `snic_io_cmpl_handler()`, then calls handlers for exchange-version, report-targets, SCSI I/O, ITMF, HBA reset, ACK, and async notifications. Internal helpers include `snic_issue_scsi_req()`, `snic_queue_icmnd_req()`, `snic_icmnd_cmpl_handler()`, `snic_send_abort_and_wait()`, `snic_abort_finish()`, `snic_send_dr_and_wait()`, `snic_dr_finish()`, and `snic_scsi_cleanup()`.

Control flow: `snic_queuecommand()` validates target readiness and adapter online state, increments `ios_inflight`, maps the SCSI SG list, allocates a request, links it through `CMD_SP(sc)`, fills the firmware initiator command, maps the sense buffer, posts the WQ descriptor, and returns host-busy on queue failure. Firmware completions are serviced from firmware CQs using color bits; I/O completions locate the command by tag, acquire a hashed I/O lock, ignore completions already owned by task management, set SCSI result/residual/sense status, clear `CMD_SP`, release DMA/request buffers, call `scsi_done()`, and update stats.

State and persistence: command state lives in `struct snic_internal_io_state` inside `scsi_cmnd`, `struct snic_req_info`, firmware active request counters, atomic stats, `snic->state`, `remove_wait`, and completion pointers inside request info. No persistent state exists.

Dependencies and integration: tightly integrates SCSI mid-layer tagging and EH callbacks, SNIC firmware protocol, SNIC request pools, vNIC firmware CQ service, discovery target objects, stats, trace, and PCI DMA APIs.

Risks: this file has the highest concurrency risk. Normal completions race with aborts and LUN resets; correctness depends on clearing `CMD_SP` only under the hashed I/O lock. Several waits use `wait_for_completion_timeout()` but the return value is not checked directly; later status fields determine timeout. `SNIC_MSG_ACK`, async event handling, and non-DAS link behavior are marked not implemented. HBA reset cleanup completes outstanding commands with transport disruption and may synthesize task-management completions. Error paths must not double-complete SCSI commands.

Test signals: run heavy tagged I/O, queue-full behavior, CHECK CONDITION/sense data, under-run/over-run, firmware status variants, abort timeout and success, abort racing normal completion, LUN reset with pending I/O, host reset, target deletion with outstanding I/O, firmware CQ wraparound, and module remove under load. Lockdep, KASAN, KCSAN, DMA-API debug, and SCSI fault injection are especially valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_stats.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_stats.h

Purpose: this header defines SNIC driver statistics structures and small inline update helpers.

Important APIs, types, and functions: `struct snic_io_stats`, `snic_abort_stats`, `snic_reset_stats`, `snic_fw_stats`, `snic_misc_stats`, and aggregate `struct snic_stats` hold atomic counters for active/completed/failed I/O, SG distribution, abort/reset outcomes, firmware errors, ISR activity, queue depth changes, and miscellaneous conditions. `snic_stats_update_active_ios()` updates maximum active I/O and total I/O count. `snic_stats_update_io_cmpl()` decrements active I/O and increments completion unless a reset skip counter is active.

Control flow: queueing, completion, abort, reset, ISR, debugfs reset, and cleanup paths update these counters. Debugfs reads format them for operators.

State and persistence: stats are per-adapter runtime atomic counters in `snic->s_stats`, plus an `io_cmpl_skip` used to reconcile stats after reset. They are not persisted and can be reset via debugfs when enabled.

Dependencies and integration: declarations for debugfs init/remove are implemented only in the debugfs build. The header relies on `SNIC_MAX_SG_DESC_CNT` being defined by included context before use.

Risks: stats are advisory and can be approximate under concurrency, especially max counters updated with read-then-set rather than compare/exchange. Resetting stats while I/O is active uses skip logic but can still produce transiently surprising values.

Test signals: debugfs stats under sustained I/O, aborts, firmware errors, queue full, and resets should move expected counters. Race testing should check for negative active counts or completion mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_trc.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_trc.c

Purpose: this optional debugfs file implements the SNIC in-memory circular trace buffer.

Important APIs, types, and functions: `snic_trc_init()` allocates a vmalloc trace buffer sized by `snic_trace_max_pages`, initializes lock and indexes, creates debugfs trace files, and enables tracing. `snic_get_trc_buf()` reserves the next trace record with wraparound and overwrite handling. `snic_get_trc_data()` returns the next complete formatted record and advances the read index. `snic_trc_free()` disables tracing, removes debugfs files, and frees the buffer.

Control flow: hot paths call `SNIC_TRC()` from `snic_trc.h`, which calls `snic_trace()`, which obtains a record and writes data fields, setting timestamp last as the completion marker. Debugfs trace reads call `snic_get_trc_data()` to drain records.

State and persistence: state is `snic_glob->trc`: spinlock, buffer pointer, max index, read/write indexes, and enable flag. It is runtime-only and lost on unload.

Dependencies and integration: compiled only with `CONFIG_SCSI_SNIC_DEBUG_FS`. It uses vmalloc, jiffies/time formatting, debugfs setup from `snic_debugfs.c`, and trace record definitions/macros from `snic_trc.h`.

Risks: trace records store `char *fn` function-name pointers, which are valid only while module text remains loaded. Reads are destructive. The writer marks `td->ts = 0` only when overwriting read index, so readers use timestamp as a coarse write-complete marker.

Test signals: enable tracing under I/O, read trace repeatedly, force wraparound with a small page count, unload while trace files are open, and verify no invalid memory access with KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_trc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_trc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_trc.h

Purpose: this header defines SNIC trace data structures, trace APIs, and trace macros for debugfs and non-debug builds.

Important APIs, types, and functions: under `CONFIG_SCSI_SNIC_DEBUG_FS`, `struct snic_trc_data` defines a packed 64-byte trace record with timestamp, function pointer, host number, tag, and five data fields; `struct snic_trc` defines the ring buffer. It declares trace/debugfs lifecycle APIs and defines `snic_trace()` plus `SNIC_TRC()`. Without debugfs, `SNIC_TRC()` falls back to conditional printk-style logging. `SNIC_TRC_CMD()` and `SNIC_TRC_CMD_STATE_FLAGS()` compact SCSI command and state data into integers.

Control flow: SCSI queueing, completion, abort, reset, and cleanup paths invoke `SNIC_TRC()`. In debugfs builds records are appended to the ring; otherwise output depends on `snic_log_level`.

State and persistence: trace state exists only when debugfs is enabled and is stored in `snic_glob->trc`. There is no persistent trace storage.

Dependencies and integration: depends on `snic_glob`, `snic_log_level`, command-state macros from `snic.h`, and debugfs implementation in `snic_trc.c`/`snic_debugfs.c`.

Risks: macros evaluate command fields directly, so callers must only pass valid `scsi_cmnd` pointers. The non-debug fallback emits logs from hot paths when logging bit 0x2 is set. Trace entry size is fixed at 64 bytes and must match structure layout.

Test signals: compile both debugfs and non-debug variants, verify trace entries include expected command tags/states, and test ring wrap/read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_trc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_cq.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_cq.c

Purpose: this file implements allocation, initialization, cleanup, and free operations for vNIC completion queues used by SNIC.

Important APIs, types, and functions: `svnic_cq_alloc()` binds a `vnic_cq` to an MMIO CQ control resource and allocates a coherent descriptor ring. `svnic_cq_init()` programs ring base, size, color, head/tail, interrupt enable, CQ entry enable, interrupt offset, and optional message address. `svnic_cq_clean()` resets software consumer state, hardware head/tail/color, and clears descriptors. `svnic_cq_free()` frees the descriptor ring and clears the control pointer.

Control flow: probe resource allocation calls `svnic_cq_alloc()` for WQ ACK CQs and firmware CQs, then `svnic_cq_init()`. Cleanup and remove call `svnic_cq_clean()` and `svnic_cq_free()`.

State and persistence: runtime state includes `vnic_cq.index`, `vdev`, MMIO `ctrl`, DMA ring, `to_clean`, and `last_color`. No persistent state exists.

Dependencies and integration: depends on vNIC resource discovery for CQ controls, coherent DMA ring helpers from `vnic_dev.c`, and service loops in `vnic_cq.h`/`vnic_cq_fw.h`.

Risks: register programming order and color initialization must match hardware expectations. `writeq()` is provided by `vnic_dev.h` if the architecture lacks it. Cleanup clears descriptors while hardware should already be disabled or quiesced.

Test signals: allocate/init/free under fault injection, CQ wraparound, interrupt offset validation, and cleanup after active completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_cq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_cq.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_cq.h

Purpose: this header defines vNIC completion queue control registers, software CQ state, and the generic CQ service loop.

Important APIs, types, and functions: `struct vnic_cq_ctrl` maps the hardware CQ control register block. `struct vnic_cq` stores index, vNIC pointer, control MMIO pointer, descriptor ring, consumer index, and color. `svnic_cq_service()` decodes common CQ descriptors, loops while descriptor color differs from `last_color`, invokes a caller-supplied service callback, advances `to_clean`, toggles color at ring wrap, and stops at `work_to_do`.

Control flow: WQ ACK processing uses this generic service loop, while firmware completions use the SNIC-specific variant in `vnic_cq_fw.h`. The callback decides whether to continue or break.

State and persistence: state is runtime CQ ring and consumer color/index. No persistent state exists.

Dependencies and integration: includes `cq_desc.h` and `vnic_dev.h`. Allocation/init/free implementations are in `vnic_cq.c`; SNIC calls them from resource and cleanup paths.

Risks: `work_to_do` is unsigned, and callers pass `-1` to mean unlimited, which becomes a large unsigned value. That is intentional but should be understood. Correctness depends on hardware color-bit behavior and memory barriers in `cq_desc_dec()`.

Test signals: service zero, finite, and unlimited work budgets; callback break behavior; ring wrap; and stale descriptor avoidance under DMA stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_cq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_cq_fw.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_cq_fw.h

Purpose: this header defines the firmware-completion CQ service loop for SNIC-specific `struct snic_fw_req` entries.

Important APIs, types, and functions: `vnic_cq_fw_service()` reads a firmware completion descriptor at `cq->to_clean`, extracts its color with `snic_color_dec()`, invokes a callback with `vdev`, CQ index, and descriptor pointer, advances the consumer index, toggles `last_color` on wrap, and enforces a work budget.

Control flow: `snic_fwcq_cmpl_handler()` calls this for firmware-to-host CQs. The callback is `snic_io_cmpl_handler()`, which dispatches by firmware response type.

State and persistence: state is CQ ring memory, `to_clean`, and `last_color`. No persistent state exists.

Dependencies and integration: includes `snic_fwint.h` for `snic_fw_req` and color decode. It assumes `struct vnic_cq` is visible through including context.

Risks: same unsigned work-budget behavior as generic CQ service applies. The loop trusts firmware completion descriptors once color changes; malformed type/status is handled later with assertions in `snic_scsi.c`.

Test signals: firmware CQ wraparound, malformed completion types, high completion rates, and limited work budget behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_cq_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_dev.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_dev.c

Purpose: this file implements the generic vNIC device layer used by SNIC: resource discovery from BAR0, coherent descriptor ring allocation, devcmd2 command submission, firmware info/config/stat/notify/open/init/enable/disable commands, notify checksum handling, and vNIC registration cleanup.

Important APIs, types, and functions: internal `struct vnic_dev` tracks PCI device, resources, interrupt mode, devcmd2 controller, notify/stats/fw_info DMA buffers, and command args. `vnic_dev_discover_res()` parses the BAR resource table. `svnic_dev_alloc_desc_ring()` and `svnic_dev_free_desc_ring()` manage aligned coherent rings. `svnic_dev_init_devcmd2()` allocates a devcmd2 WQ and result ring and issues `CMD_INITIALIZE_DEVCMD2`. `svnic_dev_cmd()` wraps command execution. Public helpers implement `svnic_dev_spec()`, stats dump/clear, notify set/unset, link status/down count, open/open_done, init, enable/disable, close, and unregister.

Control flow: probe calls `svnic_dev_alloc_discover()`, `svnic_dev_cmd_init()`, then vNIC open/init/config flows. Devcmd2 posts a command descriptor to a WQ, rings `posted_index`, waits for the corresponding result color, copies result args for read commands, and handles error/timeout. Notify reads copy a DMA buffer until its checksum is stable.

State and persistence: all state is runtime. Coherent DMA buffers cache firmware info, stats, notify area, devcmd2 command/result rings, and normal descriptor rings. `vdev->intr_mode` is software state used by SNIC setup.

Dependencies and integration: depends on vNIC resource definitions, devcmd ABI, vNIC WQ helpers, PCI DMA, MMIO I/O accessors, and SNIC probe/resource code.

Risks: devcmd2 result color management is critical. The code checks `0xFFFFFFFF` fetch/posted indexes as hardware removal indicators. Resource discovery bounds checking handles strided resources but uses BAR0 length for all BAR offsets in this single-BAR driver. `svnic_dev_cmd()` assumes `devcmd_rtn` is initialized. Notify checksum loop can spin until a consistent copy is seen.

Test signals: resource table validation, missing devcmd2 resource, devcmd timeout/error, hardware surprise removal, notify checksum stability, stats/firmware info DMA allocation failure, open/init/enable/disable sequencing, and unregister after partial initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_dev.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_dev.h

Purpose: this header exposes vNIC device abstractions, descriptor ring metadata, interrupt mode enum, BAR descriptor, MMIO 64-bit access fallbacks, and vNIC device APIs.

Important APIs, types, and functions: `enum vnic_dev_intr_mode` names unknown, INTx, MSI, and MSI-X modes. `struct vnic_dev_bar` describes mapped PCI BARs. `struct vnic_dev_ring` tracks coherent descriptor memory, aligned base, descriptor size/count, and availability. Function declarations cover private data lookup, resource count/address lookup, ring allocation/free/clear, devcmd execution, firmware info, config reads, stats, notify, link status, lifecycle commands, resource discovery, interrupt mode get/set, unregister, and devcmd initialization.

Control flow: SNIC probe creates a `vnic_dev`, reads resources/config, allocates rings, sets MSI-X mode, and uses lifecycle commands. Resource-specific code uses `svnic_dev_get_res()` to bind WQ/CQ/INTR control structures.

State and persistence: header-defined structures are runtime-only and back DMA/MMIO state. No persistent state exists.

Dependencies and integration: includes `vnic_resource.h` and `vnic_devcmd.h`. It provides `readq`/`writeq` fallbacks for architectures without native helpers.

Risks: `vnic_dev` is opaque to most callers, so lifecycle ordering is enforced by convention. Descriptor ring fields must be initialized through `svnic_dev_desc_ring_size()` before allocation. `writeq` fallback writes low then high halves, which must match device expectations.

Test signals: compile on architectures with and without native `readq/writeq`, ring alignment checks, resource lookup bounds, and lifecycle call ordering in probe/remove fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_devcmd.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_devcmd.h

Purpose: this header defines the vNIC device-command ABI used for firmware control operations and devcmd2 ring commands.

Important APIs, types, and functions: command encoding macros `_CMDC`, `_CMDCNW`, `_CMD_DIR`, `_CMD_FLAGS`, `_CMD_VTYPE`, and `_CMD_N` pack direction, flags, vNIC type, and command number. `enum vnic_devcmd_cmd` defines firmware info, device-specific config, stats, notify, open/status/close, init/status/deinit, enable/disable, capability, and devcmd2 initialization commands. Error/status enums define firmware command outcomes. Structures define firmware info, notify buffer, provision info, legacy devcmd registers, devcmd2 descriptors, devcmd2 results, and ring sizing constants.

Control flow: `vnic_dev.c` builds commands with this ABI and submits them through devcmd2. Config, stats, notify, lifecycle, and initialization operations all map to these command values and argument conventions.

State and persistence: ABI structures are DMA/MMIO runtime protocol state. Notify data contains link status, port speed, MTU, message level, uplink interface, status, error, and link-down count. No data is persisted by this header.

Dependencies and integration: consumed by `vnic_dev.c` and included by `vnic_dev.h`. It is generic to multiple vNIC types but SNIC uses `_CMD_VTYPE_SCSI`-capable commands through `_CMD_VTYPE_ALL`.

Risks: packed bit layout is protocol-critical. Error codes are firmware-specific and are returned directly by devcmd2. NOWAIT commands do not produce results, so callers must not expect readback. The original MMIO devcmd struct remains defined but SNIC initializes only devcmd2 in this driver.

Test signals: verify command numbers and direction flags against firmware, devcmd2 result error propagation, unsupported capability command behavior, notify buffer sizing, and lifecycle command fallback from `CMD_ENABLE_WAIT` to `CMD_ENABLE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_devcmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_intr.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_intr.c

Purpose: this file implements minimal vNIC interrupt control allocation, initialization, cleanup, and free helpers.

Important APIs, types, and functions: `svnic_intr_alloc()` binds a `vnic_intr` to an interrupt control MMIO resource by index. `svnic_intr_init()` programs coalescing timer, coalescing type, mask-on-assertion, and clears credits. `svnic_intr_clean()` clears interrupt credits. `svnic_intr_free()` drops the control pointer.

Control flow: SNIC resource allocation calls `svnic_intr_alloc()` for each interrupt vector and later `svnic_intr_init()` after CQ/WQ setup. ISR paths return credits through inline helpers from `vnic_intr.h` rather than this file. Cleanup calls `svnic_intr_clean()` and `svnic_intr_free()`.

State and persistence: runtime state is `vnic_intr.index`, `vdev`, and MMIO `ctrl` pointer plus hardware credit/coalescing registers. No persistent state exists.

Dependencies and integration: depends on vNIC resource lookup, vNIC interrupt structures, PCI/MMIO accessors, and SNIC MSI-X setup.

Risks: allocation fails if resource discovery did not expose enough interrupt controls. Initialization assumes the resource is valid and hardware accepts timer/type values already clamped in SNIC config. Cleaning credits while interrupts are still enabled would lose interrupt accounting.

Test signals: resource count fault injection, interrupt coalescing configuration, cleanup after active interrupts, and remove/unbind with vectors masked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_intr.c -->
