<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/scsiglue.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/scsiglue.c

## Purpose

`scsiglue.c` connects usb-storage devices to the Linux SCSI midlayer. It defines the default `scsi_host_template`, command queueing, device configuration quirks, error handlers, reset reporting, proc output, and a per-device `max_sectors` sysfs attribute.

## Important APIs, Types, and Functions

Key callbacks are `host_info()`, `sdev_init()`, `sdev_configure()`, `target_alloc()`, `queuecommand_lck()`, `command_abort()`, `device_reset()`, `bus_reset()`, `show_info()`, and the `max_sectors` show/store pair. Exported helpers are `usb_stor_report_device_reset()`, `usb_stor_report_bus_reset()`, `usb_stor_host_template_init()`, and `usb_stor_sense_invalidCDB`.

## Control Flow

`sdev_init()` forces 36-byte INQUIRY, marks multi-LUN Bulk devices, and skips problematic mode pages. `sdev_configure()` applies transfer-size limits, DMA mapping caps, disk and non-disk SCSI quirk flags, capacity heuristics, MODE_SENSE behavior, VPD/opcode suppression, cache/FUA flags, last-sector hacks, and lockability. `queuecommand_lck()` admits only one active command, rejects commands during disconnect, synthesizes invalid-CDB sense for blocked ATA pass-through, stores `us->srb`, and wakes the usb-storage control thread. Error handlers abort active transport, wait for completion, and invoke device or port reset paths.

## State and Persistence Behavior

The file mutates per-host `struct us_data` fields such as `srb`, `fflags`, `max_lun`, and `use_last_sector_hacks`; per-device SCSI flags; and request queue limits. The sysfs `max_sectors` store changes queue limits at runtime but not persistently across reprobe/reboot.

## Dependencies and Integration Points

It depends on the SCSI midlayer, block queue limits, DMA mapping limits, usb-storage transport and reset helpers, unusual-device flags, proc/scsi, and sysfs. Subdrivers clone the default template via `usb_stor_host_template_init()`.

## Risks and Test Signals

Risks include broad quirk interactions, one-command-at-a-time assumptions, abort/reset lock ordering, queue-limit changes during active I/O, and device-specific flags masking real capabilities. Tests should cover disconnect during queued command, abort vs reset races, disk and non-disk configuration, vendor capacity heuristics, max-sector sysfs updates, blocked ATA_12/ATA_16 sense, and reset reporting on multi-target SCM devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/scsiglue.c -->
