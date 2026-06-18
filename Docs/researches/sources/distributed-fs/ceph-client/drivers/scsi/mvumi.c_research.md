# sources/distributed-fs/ceph-client/drivers/scsi/mvumi.c

## Purpose

`mvumi.c` is the Marvell UMI PCI SCSI host driver for MV9143 and MV9580 storage controllers. It performs PCI setup, firmware handshake, DMA communication-list allocation, SCSI command framing, interrupt-driven completion, hotplug/event processing, timeout/reset handling, suspend/resume, shutdown cache flushes, and SCSI host attachment.

## Important APIs, Types, and Functions

- PCI/module entry points are `mvumi_probe_one()`, `mvumi_detach_one()`, `mvumi_shutdown()`, `mvumi_suspend()`, `mvumi_resume()`, and `module_pci_driver(mvumi_pci_driver)`.
- SCSI host operations are declared in `mvumi_template`: `mvumi_queue_command()`, `mvumi_timed_out()`, `mvumi_host_reset()`, `mvumi_sdev_configure()`, and `mvumi_bios_param()`.
- Firmware setup flows through `mvumi_init_fw()`, `mvumi_cfg_hw_reg()`, `mvumi_start()`, `mvumi_check_handshake()`, `mvumi_handshake_event()`, `mvumi_handshake()`, `mvumi_hs_process_page()`, `mvumi_hs_build_page()`, and `mvumi_init_data()`.
- Command allocation and tag handling are in `mvumi_alloc_cmds()`, `mvumi_free_cmds()`, `mvumi_get_cmd()`, `mvumi_return_cmd()`, `tag_init()`, `tag_get_one()`, and `tag_release_one()`.
- I/O preparation and issue are in `mvumi_build_frame()`, `mvumi_make_sgl()`, `mvumi_fire_cmd()`, `mvumi_send_command()`, and per-chip inbound-list availability hooks.
- Completion runs through `mvumi_isr_handler()`, `mvumi_clear_intr()`, `mvumi_receive_ob_list_entry()`, `mvumi_handle_clob()`, `mvumi_complete_cmd()`, and `mvumi_complete_internal_cmd()`.
- Internal synchronous commands use `mvumi_create_internal_cmd()`, `mvumi_issue_blocked_cmd()`, `mvumi_delete_internal_cmd()`, with users such as inquiry, event fetch, and cache flush.
- Hotplug and discovery are handled by `mvumi_probe_devices()`, `mvumi_inquiry()`, `mvumi_rescan_bus()`, `mvumi_handle_hotplug()`, `mvumi_launch_events()`, `mvumi_get_event()`, and notification parsers.

## Control Flow

Probe enables the PCI device, sets DMA mask, allocates a `Scsi_Host`, initializes lists/mutexes/wait queues, maps BARs, selects a device template for MV9143 or MV9580, configures MMIO register pointers, allocates a handshake page, and drives the firmware handshake. During handshake, firmware capability page 1 is queried, host/list pages are sent, communication-list memory is allocated, and inbound/outbound ring parameters are committed to MMIO registers. After command objects are allocated, the driver requests IRQs, enables interrupts, attaches to the SCSI midlayer, optionally adds a MV9580 virtual device, and starts a kernel thread for rescan work.

Normal SCSI I/O enters `mvumi_queue_command()` under `host_lock`, obtains a command from `cmd_pool`, builds a message frame from the CDB and DMA-mapped SGL, stores it in `scsi_cmd_priv`, and calls `fire_cmd`. `mvumi_fire_cmd()` queues the command, checks firmware inbound capacity, assigns a tag and request ID, either writes a dynamic-list entry pointing to a host frame or copies the frame into the inbound list, and rings the inbound write pointer.

Interrupt handling first clears and classifies interrupt sources. Doorbell events may schedule event work or continue handshaking. Communication-list output interrupts copy outbound frames into a driver-owned pool, and `mvumi_handle_clob()` returns the outbound buffers, releases tags, decrements firmware outstanding count, completes either SCSI or internal waiters, and tries to send queued commands. SCSI completion maps firmware request status to host result, copies sense payloads when present, unmaps DMA, calls `scsi_done()`, and returns the command to the pool.

Hotplug is split between firmware events and a rescan thread. Bus-change interrupts increment `pnp_count` and wake `mvumi_rescan_bus()`, which probes target IDs with internal INQUIRY commands, compares WWIDs, removes missing devices, and calls `scsi_add_device()` for new devices. Event notifications are fetched by scheduled work and logged or converted to add/remove operations.

## State and Persistence Behavior

`struct mvumi_hba` stores all runtime state: BAR mappings, register table, SCSI host, firmware state, communication-list addresses, list slots, tag stack, tag-to-command table, target bitmap, outstanding count, waiting request list, device lists, hotplug thread, and event/discovery synchronization. State is not persisted by this driver. The only durable interaction is sending firmware SCSI commands such as cache flush/shutdown and controller reset/handshake commands through MMIO doorbells.

Internal commands allocate coherent frame/data buffers on demand and wait on `int_cmd_wait_q`. Normal I/O command frames are preallocated either dynamically in a coherent inbound-frame area or as per-command cached allocations depending on firmware capability. The target map is updated during `sdev_configure()` and later drives shutdown cache flushing.

## Dependencies and Integration Points

The driver integrates with the PCI core, SCSI midlayer, DMA API, kthreads, workqueues, wait queues, interrupt handling, and MMIO accessors. It uses constants and ABI structures from `mvumi.h`, including handshake pages, SGL formats, command/response frames, and register templates. Device behavior depends on firmware protocol support flags such as compact SGL, PRD host mode, dynamic source mode, and new IO depth encoding.

MV9143 and MV9580 differ in BAR selection, register offsets, inbound/outbound ring accounting, request ID checking, reset behavior, and virtual-device handling. Those differences are captured by `mvumi_instance_template` and `mvumi_cfg_hw_reg()`.

## Risks and Edge Cases

- Tag and outbound-frame validation is critical. A bad tag or stale request ID can miscomplete commands; the code logs and skips suspect frames.
- Timeout handling manually removes `tag_cmd`, releases tags, unmaps DMA, and returns the command while firmware may still complete later; late completions must be safely rejected.
- `mvumi_issue_blocked_cmd()` can time out and manipulate queues under `host_lock`; internal command lifecycle bugs can leak coherent buffers or corrupt the tag stack.
- Handshake and reset paths reuse existing HBA state. Failure during resume or reset may leave firmware and host rings out of sync.
- Hotplug WWID matching can reject duplicate WWIDs or ID changes; MV9143 uses a synthetic WWID of `id + 1`, which is weaker than firmware UUIDs.
- `mvumi_resume()` maps BARs and calls `pci_release_regions()` on some failure paths even though resume did not request regions, so PM error unwinding deserves scrutiny.
- Several allocations use `GFP_ATOMIC` outside hard IRQ paths; memory pressure can cause command/event drops.

## Test Signals

Important tests include probe/remove on both PCI IDs, firmware handshake page negotiation, compact and non-compact SGLs, dynamic-source and copied inbound frame modes, SCSI read/write with many SG entries, CHECK CONDITION sense propagation, command timeout followed by late completion, host reset, shutdown/suspend cache flush, hotplug add/remove/rescan, event notification logging, MV9580 virtual-device attach, and DMA API/debug checks for map/unmap balance.
