# sources/distributed-fs/ceph-client/drivers/scsi/3w-9xxx.c

## Purpose

`3w-9xxx.c` is the Linux SCSI low-level driver for 3ware 9000-family storage controllers. It registers a PCI driver named `3w-9xxx`, exposes a SCSI host template, translates kernel SCSI commands into firmware `TW_OP_EXECUTE_SCSI` command packets, handles controller interrupts and asynchronous event notifications, and provides a privileged management character device named `twa`. It supports the 9000, 9550SX, 9650SE, and 9690SA device IDs, including different register offsets and large command queue posting for later adapters.

## Important APIs, Types, and Functions

The module entry points are `twa_init()` and `twa_exit()`, which register and unregister the `pci_driver`. PCI lifecycle is handled by `twa_probe()`, `twa_remove()`, `twa_shutdown()`, and power-management callbacks `twa_suspend()` and `twa_resume()`. The SCSI integration surface is `driver_template`, with `queuecommand = twa_scsi_queue`, `eh_host_reset_handler = twa_scsi_eh_reset`, `bios_param = twa_scsi_biosparam`, `sdev_configure = twa_sdev_configure`, and the `twa_host_groups` sysfs attribute group.

Request execution runs through `twa_scsi_queue_lck()`, `twa_scsiop_execute_scsi()`, `twa_post_command_packet()`, `twa_interrupt()`, and `twa_scsiop_execute_scsi_complete()`. Request IDs are managed with `twa_get_request_id()` and `twa_free_request_id()` against the `free_queue`, `pending_queue`, and `state[]` arrays in `TW_Device_Extension`. Management I/O uses `twa_chrdev_open()` and `twa_chrdev_ioctl()`, with the ioctl ABI defined in `3w-9xxx.h`.

Controller initialization and recovery are concentrated in `twa_reset_sequence()`, `twa_reset_device_extension()`, `twa_initconnection()`, `twa_check_srl()`, `twa_get_param()`, `twa_poll_status()`, `twa_poll_status_gone()`, `twa_empty_response_queue()`, and `twa_empty_response_queue_large()`. AEN handling uses `twa_aen_read_queue()`, `twa_aen_complete()`, `twa_aen_drain_queue()`, `twa_aen_queue_event()`, `twa_aen_sync_time()`, and `twa_aen_severity_lookup()`.

## Control Flow

Probe enables the PCI device, sets bus mastering/MWI, tries a 64-bit coherent DMA mask with 32-bit fallback, allocates a `Scsi_Host`, initializes DMA command and generic buffers, requests PCI regions, maps the controller BAR, disables interrupts, and runs `twa_reset_sequence()` in non-soft-reset mode. The reset sequence waits for controller readiness, drains stale responses, checks firmware/driver SRL compatibility with `InitConnection`, drains AENs, and records compatibility metadata. Probe then configures SCSI host limits, adds the host, prints firmware/BIOS/port data via firmware parameter reads, optionally enables MSI for non-9000 devices, requests the shared IRQ, publishes the adapter in `twa_device_extension_list`, enables interrupts, scans devices, and registers the `twa` char device if it is not already registered.

Normal I/O starts when the SCSI midlayer calls `twa_scsi_queue()`. The driver refuses new work while `TW_IN_RESET` is set, rejects nonzero LUNs if firmware SRL is too old, allocates a request ID, stores the `scsi_cmnd` in `srb[]`, and builds a 16-byte CDB `TW_Command_Apache` packet. Small single-entry transfers below `TW_MIN_SGL_LENGTH` are copied through a per-request coherent generic buffer; larger or multi-entry transfers use `scsi_dma_map()` and firmware SGL entries. `twa_post_command_packet()` either writes the command-packet DMA address to the appropriate command queue register or queues the request in `pending_queue` and unmasks command interrupts when the hardware queue is full.

`twa_interrupt()` serializes completions under `host_lock`. It validates interrupt status, ignores interrupts during reset, decodes clearable PCI/controller errors, clears host/attention interrupts, drains pending posts on command interrupts, and drains response queue entries on response interrupts. For firmware command errors, `twa_fill_sense()` prints or copies sense data from the command header. Internal AEN and char-device requests are completed without calling `scsi_done()`. SCSI requests run copy-back for small read buffers, set result status, optionally report residual bytes, unmap DMA, call `scsi_done()`, free the request ID, and decrement posted counts.

Management ioctl flow is serialized by a global `twa_chrdev_mutex` plus per-controller `ioctl_lock`. `TW_IOCTL_FIRMWARE_PASS_THROUGH` copies a user command into coherent memory, patches request IDs and SGLs with `twa_load_sgl()`, posts it as an internal command, waits up to `TW_IOCTL_CHRDEV_TIMEOUT`, resets the controller on timeout, and copies the firmware response back. Other ioctls expose compatibility info, walk the AEN event ring, or implement an advisory lock with an expiration time.

## State and Persistence Behavior

All persistent runtime state is in memory. `TW_Device_Extension` stores MMIO base address, coherent command/generic buffers, command states, queue heads/tails, per-request `srb[]` pointers, stats counters, reset flags, the AEN event ring, compatibility info, and char-device wait/lock state. The driver does not persist metadata to disk; firmware state is queried or updated through controller parameter tables and `InitConnection`. Shutdown/suspend notify the controller by sending `InitConnection` with one message credit and feature zero, then clear interrupts.

## Dependencies and Integration Points

The file depends on the kernel PCI, DMA, SCSI midlayer, block timeout, sysfs host attributes, interrupt, waitqueue, mutex, uaccess, and time APIs. Hardware integration is through MMIO register macros from `3w-9xxx.h`; firmware integration is through 3ware command packets, SRL compatibility negotiation, parameter table reads, REQUEST_SENSE AEN polling, and management passthrough. User-space integration is through `/dev/twa` and a `stats` host sysfs attribute. The driver also relies on the global `sys_tz` timezone when converting host time for AEN timestamps and time synchronization.

## Risks and Edge Cases

The char-device minor lookup races with remove; the source explicitly notes this in `twa_chrdev_open()`, and the global device-extension list is compacted by decrementing a count without clearing or reindexing removed slots. The ioctl passthrough path trusts the user-supplied firmware command shape after size checks and must correctly patch SGL positions for both old and Apache command formats, including PAE and 9690SA-specific layout. Request state transitions are split across queueing, ISR, reset, and ioctl timeout paths; missing a posted-count decrement or DMA unmap can corrupt later completions. Small-buffer copy-through depends on `twa_command_mapped()` and must stay in sync with completion copy-back. Firmware error strings are parsed from adjacent strings in `err_specific_desc`, so malformed firmware buffers could affect printed/logged parameter text if not NUL-terminated; the driver clamps one terminator before copying. Suspend/resume has ordering risk around MSI re-enable: resume requests the IRQ before re-enabling MSI if `TW_USING_MSI` was set.

## Test Signals

Useful validation signals include successful PCI probe with firmware/BIOS/port printk lines, SCSI scan discovering the expected units and LUN behavior by firmware SRL, `/sys/class/scsi_host/host*/stats` showing posted/pending/SG/reset/AEN counters, passthrough ioctl completion and timeout reset behavior, AEN generation and retrieval through the event ioctls, reset recovery from SCSI EH timeouts, suspend/resume with and without `use_msi=1`, and stress I/O with small single-SGL buffers, large multi-SG DMA, command-queue-full pending reposts, and controller error injection.
