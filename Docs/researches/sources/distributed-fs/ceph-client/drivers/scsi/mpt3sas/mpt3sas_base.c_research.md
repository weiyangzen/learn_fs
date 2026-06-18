# sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_base.c

## Purpose

`mpt3sas_base.c` is the common hardware/firmware access layer for the Linux `mpt3sas`/`mpt2sas` Fusion MPT SAS HBA driver. It owns controller bring-up and teardown, PCI BAR mapping, DMA mask setup, MSI-X or legacy interrupt setup, request/reply queue allocation, IOC doorbell handshakes, IOC initialization, fault/coredump watchdog handling, reset recovery, and the base command submission/completion API used by SCSI, transport, config, control, and diagnostic layers.

The file is not Ceph-specific despite living under this source snapshot's Ceph client tree. It is a kernel SCSI low-level driver component for Broadcom/LSI/Avago SAS2/SAS3/SAS35 controllers, including SAS/SATA devices, integrated RAID firmware, NVMe/PCIe devices through MPI 2.6 encapsulation, WarpDrive behavior, mCPU endpoints, and OEM-specific quirks.

## Important APIs, Types, and Functions

- `struct MPT3SAS_ADAPTER`: central adapter object declared in `mpt3sas_base.h`; this file fills in function pointers and maintains fields such as `facts`, `pfacts`, `request`, `reply`, `reply_free`, `reply_post`, `chain_lookup`, `pcie_sg_lookup`, `cpu_msix_table`, command state blocks, event masks, and reset flags.
- `mpt_callbacks[MPT_MAX_CALLBACKS]`: global callback table used by reply processing to route completions by callback index. Public APIs are `mpt3sas_base_register_callback_handler()`, `mpt3sas_base_release_callback_handler()`, and `mpt3sas_base_initialize_callback_handler()`.
- Module parameters: `max_queue_depth`, `max_sgl_entries`, `msix_disable`, `smp_affinity_enable`, `max_msix_vectors`, `irqpoll_weight`, `mpt3sas_fwfault_debug`, `perf_mode`, and `poll_queues`. These alter queue depth, SG depth, interrupt strategy, watchdog fault behavior, interrupt coalescing, high-IOPS queues, and io_uring polling.
- MMIO helpers: `_base_readl_aero()`, `_base_readl_ext_retry()`, `_base_writeq()`, `_base_mpi_ep_writeq()`, plus BAR0 clone helpers for mCPU endpoints. Aero controllers retry zero register reads; mCPU endpoints need 32-bit write sequencing and BAR0 request/reply cloning.
- Resource APIs: `mpt3sas_base_map_resources()`, `mpt3sas_base_unmap_resources()`, `mpt3sas_base_free_resources()`, `mpt3sas_base_attach()`, and `mpt3sas_base_detach()`.
- Request/reply APIs: `mpt3sas_base_get_msg_frame()`, `mpt3sas_base_get_sense_buffer()`, `mpt3sas_base_get_sense_buffer_dma()`, `mpt3sas_base_get_pcie_sgl()`, `mpt3sas_base_get_pcie_sgl_dma()`, `mpt3sas_base_get_reply_virt_addr()`, `mpt3sas_base_get_smid()`, `mpt3sas_base_get_smid_scsiio()`, `mpt3sas_base_get_smid_hpr()`, `mpt3sas_base_free_smid()`.
- Submission functions installed as adapter function pointers: `_base_put_smid_default()`, `_base_put_smid_scsi_io()`, `_base_put_smid_mpi_ep_scsi_io()`, `_base_put_smid_fast_path()`, `_base_put_smid_hi_priority()`, `mpt3sas_base_put_smid_nvme_encap()`, and atomic-descriptor variants for capable Aero devices.
- SG builders: `_base_build_sg()`, `_base_build_sg_ieee()`, `_base_build_sg_scmd()`, `_base_build_sg_scmd_ieee()`, `_base_build_nvme_prp()`, `base_make_prp_nvme()`, and `_base_check_pcie_native_sgl()`. They translate Linux SCSI SG lists into MPI simple SGEs, IEEE SGEs, chains, or NVMe PRP lists.
- Completion/interrupt APIs: `_base_process_reply_queue()`, `_base_interrupt()`, `_base_irqpoll()`, `mpt3sas_blk_mq_poll()`, `mpt3sas_base_sync_reply_irqs()`, `mpt3sas_base_done()`, and `_base_async_event()`.
- Firmware command APIs: `_base_handshake_req_reply_wait()`, `_base_get_ioc_facts()`, `_base_get_port_facts()`, `_base_send_ioc_init()`, `_base_event_notification()`, `_base_send_port_enable()`, `mpt3sas_port_enable()`, `mpt3sas_base_sas_iounit_control()`, and `mpt3sas_base_scsi_enclosure_processor()`.
- Reset/fault APIs: `mpt3sas_base_start_watchdog()`, `mpt3sas_base_stop_watchdog()`, `_base_fault_reset_work()`, `mpt3sas_base_check_for_fault_and_issue_reset()`, `_base_diag_reset()`, `mpt3sas_base_make_ioc_ready()`, `_base_make_ioc_operational()`, and `mpt3sas_base_hard_reset_handler()`.

## Control Flow

Attach starts in `mpt3sas_base_attach()`. It sizes CPU/MSI-X lookup tables, chooses register read helpers, maps PCI MMIO resources via `mpt3sas_base_map_resources()`, reads IOC facts, installs SG builders and request descriptor writers based on MPI version and atomic-descriptor capability, moves the IOC to READY, reads per-port facts, allocates all DMA pools, initializes interrupt polling, allocates handle bitmaps and internal command reply buffers, initializes event masks, then calls `_base_make_ioc_operational()`.

Resource mapping enables the PCI memory device, requests BARs, sets bus mastering, chooses 32/63/64-bit DMA masks, ioremaps the first memory BAR, masks interrupts, reads IOC facts, enables MSI-X or falls back to INTx, sets io_uring poll queue state, builds combined reply queue register pointers, and saves PCI config state for AER/EEH recovery.

Operational bring-up in `_base_make_ioc_operational()` clears delayed reset/event lists, rebuilds hi-priority and internal SMID free lists, initializes reply-free entries and reply-post descriptors, sends `IOC_INIT` through the doorbell handshake, writes reply host indexes, unmasks interrupts, optionally reads firmware package version, reads static config pages, programs performance/diagnostic settings, subscribes event notification, and either returns for async scan-start handling or synchronously sends port enable during host recovery.

Normal I/O submission uses a SCSI-layer path outside this file to acquire an SMID with `mpt3sas_base_get_smid_scsiio()`, populate an MPI request frame, build SG/PRP data with the function pointers selected during attach, and post a request descriptor with one of the `put_smid_*` functions. The descriptor write is the MMIO doorbell into firmware's request descriptor post register.

Completion flow is interrupt, irq-poll, or blk-mq poll driven. `_base_process_reply_queue()` walks reply descriptors, detects fast-path success or address replies, extracts the SMID, resolves a callback index with `_base_get_cb_idx()`, calls the registered callback, displays reply/log info when appropriate, recycles reply frames through the reply-free queue, marks reply descriptors unused, updates reply-post host indexes, and frees the SMID when the callback asks it to. Asynchronous events have `smid == 0` and are routed through `_base_async_event()`, which may send or queue an event ACK and then notifies SCSI host and control callbacks.

Reset flow begins with `mpt3sas_base_hard_reset_handler()` or watchdog-triggered `_base_fault_reset_work()`. The handler serializes with `reset_in_progress_mutex`, marks `shost_recovery`, calls pre-reset callbacks, waits briefly for in-flight SCSI commands, masks interrupts, pauses io_uring poll queues, moves the IOC to READY through message-unit reset or diagnostic reset, marks outstanding internal commands as reset, refreshes IOC facts, adjusts handle bitmaps for online firmware changes, calls `_base_make_ioc_operational()`, runs reset-done callbacks, clears recovery state, resumes polling, and may fire diagnostic triggers.

## State and Persistence Behavior

Most state is volatile per-adapter kernel memory. Persistent device state is read or modified through MPI config pages stored by firmware/NVDATA. `_base_static_config_pages()` reads manufacturing pages, BIOS pages, IOC/IOUnit pages, firmware-reported queue depths, ATTO NVRAM-derived SAS addresses, diagnostic trigger pages, and time-sync settings. It also updates IOUnit Page 1 task-set-full handling, may correct non-gen35 EEDP tag mode in Manufacturing Page 11, updates IOC Page 1 performance/coalescing settings, and may rewrite driver trigger pages after online firmware updates.

The driver persists no files of its own. Runtime state includes DMA pools, SMID trackers, reply queues, event masks, command-state blocks, delayed ACK/reset lists, handle bitmaps, and counters such as `ioc_reset_count`, `timestamp_update_count`, `non_operational_loop`, and `ioc_coredump_loop`. PCI config state is saved for recovery. Firmware-visible persistent behavior includes event subscriptions, IOUnit/IOC config page writes, ATTO BIOS Page 4 SAS address reassignment, time-sync IOC parameter writes, and optional diagnostic trigger page updates.

## Dependencies and Integration Points

- Linux kernel subsystems: PCI, DMA API, IRQ/MSI-X, blk-mq polling, SCSI midlayer, SCSI command private data, wait queues, workqueues, kthreads, completions, mutexes/spinlocks, and `irq_poll`.
- MPI headers and firmware protocol types from `mpi/` provide IOC facts, IOC init, config page, SAS, PCIe/NVMe, firmware upload, event, and diagnostic structures.
- Sibling mpt3sas modules supply callbacks and helpers: SCSI host logic (`mpt3sas_scsih_*`), control/ioctl logic (`mpt3sas_ctl_*`), config page helpers (`mpt3sas_config_*`), diagnostic trigger logic (`mpt3sas_trigger_*`), logging/debug macros, and device-specific helpers such as `mpt3sas_scsih_scsi_lookup_get()` and `mpt3sas_scsih_is_pcie_scsi_device()`.
- Firmware integration is through MMIO registers in the mapped chip BAR, request descriptor post writes, reply descriptor post queues, reply-free queues, doorbell handshakes, IOC state polling, and host diagnostic register reset sequences.
- User/admin integration is through module parameters and kernel logs. Some behavior is visible through SCSI device enumeration, host reset behavior, io_uring poll support, IRQ affinity, and firmware diagnostic output.

## Risks and Edge Cases

- DMA allocation is constrained by controller generation and 4GB-region requirements. Several pools return `-EAGAIN` to retry with 32-bit coherent DMA or reduced queue depth; partial allocation cleanup must remain correct to avoid leaks or dangling DMA mappings.
- Reply queue processing is highly concurrent. `reply_q->busy`, irq-poll scheduling, IRQ disable/enable, and blk-mq poll pause/busy flags prevent duplicate completion, but races here can double-complete commands or lose replies.
- SMID ownership is split across SCSI I/O, hi-priority, and internal queues. Incorrect callback index, SMID boundary, or free-list handling can leak requests, complete the wrong subsystem, or corrupt chain lookup state.
- Doorbell and diagnostic reset paths are hardware-sensitive. Timeouts, `0xffffffff` register reads, coredump state, PCI error recovery, and active doorbell ownership all alter reset decisions.
- Firmware fault debug can intentionally halt or panic the kernel. `mpt3sas_fwfault_debug` is powerful and should not be enabled in normal production paths.
- NVMe PRP/native SGL code depends on page-size arithmetic, DMA segment lengths, and PRP-list boundary insertion. Bugs can produce invalid PRP lists, IOMMU faults, or data corruption.
- mCPU endpoint BAR0 cloning assumes strict BAR0 layout and contains a comment noting reliance on a zero PCI memory offset. Changes to endpoint layout or address assumptions are high risk.
- Some functions mutate firmware config pages during attach. Regressions can change queueing, time sync, task-set-full handling, or OEM SAS address assignment persistently.
- `mpt3sas_base_scsi_enclosure_processor()` copies `sizeof(Mpi2SepReply_t)` bytes from request input into the request frame, which is suspicious because the request object type is `Mpi2SepRequest_t`; this deserves focused review before modification.
- Error recovery during online firmware update is delicate. `_base_check_ioc_facts_changes()` only resizes handle bitmaps for increased `MaxDevHandle`; other changed facts may require reboot or panic paths.

## Test Signals

- Driver attach logs should show successful PCI mapping, DMA address width, MSI-X or IO-APIC enablement, queue depth, SG/chain sizing, allocated physical memory, IOC capabilities, firmware package version for SAS3+, event notification completion, and port enable success.
- Interrupt/completion tests should include fast-path SCSI success replies, address replies with nonzero reply frames, asynchronous events needing ACK, reply-free recycling, irq-poll threshold scheduling, MSI-X affinity, legacy INTx fallback, and blk-mq/io_uring polling with pause/resume during reset.
- Storage I/O tests should cover no-data commands, read/write/bidirectional SG lists, chained SG lists, REPORT ZONES bidirectional mapping, NVMe/PCIe PRP construction, large SG counts near `sg_tablesize`, and reset while I/O is outstanding.
- Fault injection should cover firmware FAULT, COREDUMP wait and timeout, non-operational doorbell reads, doorbell-in-use during handshake, IOC init timeout, port enable timeout, diagnostic reset failure, PCI error recovery, and dead IOC removal.
- Config and persistence tests should validate Manufacturing/Bios/IOC/IOUnit page reads, performance-mode IOC Page 1 writes, missing-delay updates, diagnostic trigger page support transitions, ATTO NVRAM validation, and time-sync IOC parameter updates.
- Resource teardown tests should verify detach after partial attach failure, normal detach, watchdog stop, IRQ free, DMA pool release, enclosure list release, and no stale `pci_set_drvdata()` pointer.
