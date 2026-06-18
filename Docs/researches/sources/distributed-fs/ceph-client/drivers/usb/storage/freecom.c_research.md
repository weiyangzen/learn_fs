# sources/distributed-fs/ceph-client/drivers/usb/storage/freecom.c

## Purpose

`freecom.c` implements the usb-storage subdriver for Freecom USB/IDE and USB/ATAPI adapters. It wraps SCSI/ATAPI commands in Freecom 64-byte command packets and performs the adapter-specific status and data phases.

## Important APIs, Types, and Functions

Packet layouts include `struct freecom_cb_wrap`, `struct freecom_xfer_wrap`, `struct freecom_ide_out`, `struct freecom_ide_in`, and `struct freecom_status`. `freecom_transport()` is the main transport handler. `freecom_readdata()` and `freecom_writedata()` issue Freecom input/output transfer commands before bulk data movement through `usb_stor_bulk_srb()`. `init_freecom()` performs the vendor reset/activation sequence. `usb_stor_freecom_reset()` is a placeholder reset hook returning `FAILED`. `freecom_probe()` installs the Freecom transport and limits max LUN to zero.

## Control Flow

Probe initializes usb-storage with the Freecom unusual-device table, sets transport name and reset hooks, then completes normal usb-storage setup. For each SCSI command, `freecom_transport()` sends a 64-byte ATAPI packet, reads a 4-byte status packet, loops with status-only packets while the adapter reports busy, checks failure/status bits, determines the data length, and performs an optional data-in or data-out phase based on SCSI direction. After data transfer it reads final status and validates status/reason fields.

## State and Persistence Behavior

The driver stores no private per-device state. It reuses `us->iobuf` for command/status wrappers. Persistent effects are limited to commands sent to the attached IDE/ATAPI device and the adapter reset sequence in `init_freecom()`.

## Dependencies and Integration Points

It depends on usb-storage core, unusual Freecom IDs, SCSI/ATAPI command buffers, bulk transfer helpers, and Freecom's packet protocol. It integrates with the SCSI layer as a custom transport and with the generic usb-storage reset/suspend/disconnect framework through `struct usb_driver`.

## Risks and Test Signals

Risks include no real transport reset support, long busy loops relying on device status without a host-side timeout beyond USB transfers, data length truncation for selected commands, incomplete write-direction status validation, and debug hexdump code using static shared storage. Test signals include initialization control-message sequence, INQUIRY/REQUEST_SENSE/MODE_SENSE length handling, long-running ATAPI commands that require repeated status packets, read and write data phases, failed status bit mapping to transport failed, and reset path behavior under SCSI error recovery.
