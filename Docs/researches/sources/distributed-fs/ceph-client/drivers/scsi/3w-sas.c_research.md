# sources/distributed-fs/ceph-client/drivers/scsi/3w-sas.c

## Purpose

`3w-sas.c` is the SCSI low-level driver for LSI 3ware 9750 SAS/SATA RAID controllers. It shares the broad 3ware SCSI-host model with `3w-9xxx.c`, but uses the 9750 "Liberator" register interface: inbound host queues, outbound response queues, doorbell interrupts, and pre-posted sense buffers. It registers a PCI driver named `3w-sas`, exposes a `twl` management character device for firmware passthrough, and adds sysfs binary files for AEN and compatibility data.

## Important APIs, Types, and Functions

Module and PCI entry points are `twl_init()`, `twl_exit()`, `twl_probe()`, `twl_remove()`, `twl_shutdown()`, `twl_suspend()`, and `twl_resume()`. SCSI integration is through `driver_template`, with `queuecommand = twl_scsi_queue`, `eh_host_reset_handler = twl_scsi_eh_reset`, `bios_param = twl_scsi_biosparam`, `sdev_configure = twl_sdev_configure`, and `twl_host_groups`.

I/O path functions are `twl_scsi_queue_lck()`, `twl_scsiop_execute_scsi()`, `twl_post_command_packet()`, and `twl_interrupt()`. Request allocation uses `twl_get_request_id()` and `twl_free_request_id()`. AEN and controller management flows use `twl_handle_attention_interrupt()`, `twl_aen_read_queue()`, `twl_aen_complete()`, `twl_aen_drain_queue()`, `twl_aen_queue_event()`, `twl_aen_sync_time()`, `twl_get_param()`, `twl_initconnection()`, and `twl_reset_sequence()`.

User-visible management surfaces are `twl_chrdev_open()`, `twl_chrdev_ioctl()`, the `twl_fops` char-device operations, `twl_sysfs_aen_read()`, `twl_sysfs_compat_info()`, and `twl_show_stats()`. Error handling uses `twl_fill_sense()` with the separately posted sense buffers defined in `3w-sas.h`.

## Control Flow

Probe enables the PCI device, sets bus mastering/MWI, requires a 64-bit coherent DMA mask, allocates a SCSI host and private device extension, allocates coherent command packets, generic buffers, and sense buffers, requests PCI regions, maps BAR 1, masks interrupts, and calls `twl_reset_sequence()`. Reset optionally soft-resets the controller, waits for scratchpad readiness transitions, performs extended `InitConnection`, posts every sense buffer address to the firmware, checks controller status, drains AENs, and records compatibility metadata. Probe then configures host limits, adds the SCSI host, prints model/firmware/BIOS/PHY data from parameter tables, optionally enables MSI, requests the shared IRQ, registers the adapter in `twl_device_extension_list`, unmasks interrupts, scans the host, creates `3ware_aen_read` and `3ware_compat_info` binary sysfs files, and registers `/dev/twl` if needed.

Normal SCSI I/O allocates a request ID, saves `SCpnt`, builds an Apache execute-SCSI packet, maps all scatterlist entries with `scsi_dma_map()`, writes SGL entries through `TW_CPU_TO_SGL()`, updates sector/SGL stats, and posts the command DMA address by writing high then low queue registers with `TWL_PULL_MODE`. The Liberator path does not maintain a pending queue for command-queue-full retry in the way the older drivers do; it assumes the host queue post succeeds once the packet is written.

Interrupt handling reads `TWL_HISTAT`. Attention interrupts call `twl_handle_attention_interrupt()`, which reads the outbound doorbell, detects controller errors, starts AEN REQUEST_SENSE polling if not already in the attention loop, and clears the doorbell. Response interrupts read an outbound MFA from high/low queue registers. If `TW_NOTMFA_OUT()` indicates the value is a sense-buffer address rather than a normal response, the ISR finds the matching sense buffer, extracts the request ID from its header, copies or prints sense data, and reposts that sense buffer to firmware. Normal responses get the request ID from `TW_RESID_OUT()`. Internal AEN/ioctl completions wake or continue their state machines; SCSI completions set result, report residual bytes for single-SG commands, unmap DMA, complete the command, free the request, and decrement posted counts.

The char-device ioctl path supports `TW_IOCTL_FIRMWARE_PASS_THROUGH` only. It is serialized by `twl_chrdev_mutex` and `ioctl_lock`, copies the user ioctl into coherent memory, patches request ID and SGL fields for old or new command packets with `twl_load_sgl()`, posts the command, waits for `chrdev_request_id` to become free, resets on timeout, copies the response back, and frees the coherent ioctl buffer.

## State and Persistence Behavior

Runtime state is stored in `TW_Device_Extension`: MMIO base, command/generic/sense coherent buffers and DMA addresses, SCSI command pointers, request free queue and states, counters, AEN event queue, compatibility info, char-device wait state, MSI/reset/attention flags, and an `online` flag used by shutdown/remove guards. Sysfs binary files expose in-memory AEN and compatibility buffers directly through `memory_read_from_buffer()` under `host_lock`; they do not persist events beyond the in-memory ring. The controller is notified on suspend/shutdown through `InitConnection` with one credit and no features.

## Dependencies and Integration Points

The driver depends on Linux PCI, coherent DMA, SCSI midlayer, interrupts, sysfs binary attributes, block queue timeout APIs, waitqueues, mutexes, and uaccess. Firmware integration is through Liberator registers, inbound/outbound queue MFAs, sense-buffer posting, parameter tables, and 3ware ioctl-compatible command packets. User-space integration includes `/dev/twl`, `3ware_aen_read`, `3ware_compat_info`, and host stats `3ware_stats`. The management interface is described as used by smartmontools.

## Risks and Edge Cases

`twl_probe()` requires a 64-bit DMA mask and does not fall back to 32-bit DMA, so older or constrained platforms fail probe. `twl_scsiop_execute_scsi()` treats `scsi_dma_map()` returning zero as failure, which may matter for valid zero-data commands if they ever reach this path. Residual calculation compares firmware SGL length in command storage without endian conversion and can be suspicious on big-endian platforms. The char-device minor lookup has the same global-array/remove shape as the 9xxx driver, but without an explicit race comment. Sense-buffer matching is a linear scan over `TW_Q_LENGTH` entries per sense response; correctness depends on the firmware returning exact DMA addresses and on reposting every buffer after use. The `online` guard avoids double shutdown but must be set and cleared consistently across partial probe and remove paths.

## Test Signals

Validation should cover 9750 PCI probe, 64-bit DMA setup, sense-buffer posting without `TWL_STATUS_OVERRUN_SUBMIT`, sysfs binary reads gated by `CAP_SYS_ADMIN`, firmware passthrough via `/dev/twl`, AEN generation and time-sync handling, reset after SCSI EH timeout and ioctl timeout, suspend/resume with MSI enabled and disabled, and I/O stress with multi-SG reads/writes while injecting firmware sense responses and doorbell attention interrupts.
