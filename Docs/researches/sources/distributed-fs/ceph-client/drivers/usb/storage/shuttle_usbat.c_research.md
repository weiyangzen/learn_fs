<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/shuttle_usbat.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/shuttle_usbat.c

## Purpose

`shuttle_usbat.c` supports SCM Microsystems/Shuttle USBAT bridges used for ATAPI CD drives such as HP 8200e and USBAT02 CompactFlash readers. It initializes the bridge, identifies the attached device type, and installs either an ATAPI packet transport or a flash ATA-sector transport.

## Important APIs, Types, and Functions

`struct usbat_info` stores device type, flash capacity/sector size, and cached sense data. Common bridge helpers include `usbat_read()`, `usbat_write()`, `usbat_execute_command()`, `usbat_multiple_write()`, `usbat_set_shuttle_features()`, `usbat_wait_not_busy()`, `usbat_read_block()`, `usbat_write_block()`, `usbat_read_blocks()`, and `usbat_write_blocks()`. Flash helpers include `usbat_flash_check_media()`, `usbat_flash_get_sector_count()`, `usbat_flash_read_data()`, `usbat_flash_write_data()`, and `usbat_flash_transport()`. CD/ATAPI helpers include `usbat_hp8200e_transport()` and `usbat_hp8200e_handle_read10()`.

## Control Flow

Probe installs placeholder transport and lets unusual-device init call `init_usbat_cd()` or `init_usbat_flash()`. Initialization allocates state, toggles user I/O reset/card-detect lines, tests ATA registers, detects device type with IDENTIFY PACKET DEVICE if needed, sets the final transport, and programs Shuttle feature registers. Flash transport fakes INQUIRY, checks media through UIO pins, returns IDENTIFY-derived capacity, chunks READ/WRITE through 64 KiB bounce buffers, and returns cached sense on REQUEST_SENSE. HP8200e transport wraps ATAPI packet commands by writing ATA packet registers and command bytes, handles large READ_10/READ_CD by splitting into sub-64 KiB reads, and waits for long operations such as BLANK.

## State and Persistence Behavior

Per-device state lives in `us->extra`; the global `transferred` counter tracks HP8200e transfer progress across calls. Flash writes persist to media. UIO resets and feature programming alter bridge/device state but are not host-persistent.

## Dependencies and Integration Points

The driver depends on usb-storage control/bulk helpers, SCSI and CD-ROM opcodes, scatterlist utilities, `unusual_usbat.h`, and CB reset handling. It integrates both as a SCSI disk-like flash transport and as an ATAPI packet bridge.

## Risks and Test Signals

Risks include global `transferred`, long busy waits, many magic register sequences, 28-bit LBA limits, media-change races, len truncation above 64 KiB, and device-type misidentification. Tests should cover HP8200e packet commands, blank/synchronize long waits, large READ_10 splitting, flash media absent/changed/present states, READ/WRITE_10 and _12 chunking, unknown commands with REQUEST_SENSE, and init failures at each UIO/register-test step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/shuttle_usbat.c -->
