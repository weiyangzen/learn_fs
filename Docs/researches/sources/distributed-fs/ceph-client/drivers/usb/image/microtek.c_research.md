# sources/distributed-fs/ceph-client/drivers/usb/image/microtek.c

## Purpose
`microtek.c` implements a USB-to-SCSI bridge for Microtek Scanmaker X6 USB scanners and related devices. It registers both as a USB interface driver and as a SCSI host adapter, translating SCSI commands from the scanner stack into a private USB protocol with command, data, and one-byte status phases.

## Important APIs, Types, And Functions
The driver uses `struct mts_desc` and `struct mts_transfer_context` from `microtek.h`. `mts_usb_driver` binds supported USB IDs, while `mts_scsi_host_template` exposes one emulated SCSI host with `queuecommand`, abort, reset, `sdev_init`, `can_queue = 1`, `SG_ALL`, and 511-byte DMA alignment.

Core functions are `mts_usb_probe()`, `mts_usb_disconnect()`, `mts_scsi_queuecommand_lck()`, `mts_build_transfer_context()`, `mts_command_done()`, `mts_data_done()`, `mts_get_status()`, `mts_transfer_done()`, `mts_do_sg()`, `mts_scsi_abort()`, and `mts_scsi_host_reset()`. The command direction table `mts_direction[]` and special `mts_read_image_sig[]` select response versus image endpoints.

## Control Flow
Probe verifies exactly three endpoints, finds one bulk-out and two bulk-in endpoints, allocates the descriptor, URB, and status byte, then allocates/adds a SCSI host and scans it. SCSI queueing rejects nonzero channel/id/lun as `DID_BAD_TARGET`; otherwise it submits the raw SCSI CDB to the command endpoint. The command completion callback handles command URB errors, then either reads request-sense data into `sense_buffer`, transfers SCSI data through the selected pipe, or reads status directly. Data completion updates residuals and host status, then requests the final one-byte SCSI status. Final completion merges scanner status into `srb->result` and calls `scsi_done()`.

## State And Persistence
State is per USB interface in `struct mts_desc`: endpoint numbers, one shared URB, SCSI host pointer, status byte storage, and current transfer context. There is no durable state. Only one command can be active because the host template sets `can_queue = 1` and the descriptor owns a single URB/context pair. Scatter/gather progress is stored in `context.curr_sg`.

## Dependencies And Integration Points
The driver integrates with USB core, SCSI midlayer, SCSI error handling, and scatterlist helpers. It reuses usb-storage style direction inference instead of trusting `sc_data_direction`. User-visible scanner access is through the SCSI scanner path, not a custom char device. USB IDs cover Microtek and related vendor/product pairs.

## Risks
Endpoint role assignment assumes the first discovered bulk-in endpoint is response and the second is image data; unusual descriptor ordering can be warned about but still used incorrectly. `mts_do_sg()` advances to `sg_next()` before checking whether the current segment was the last, so scatter/gather edge cases depend on the callback choice made during submission. Short transfers set residuals but still proceed to status. Abort kills the single URB and returns `FAILED`, leaving recovery to the SCSI layer. The protocol was reverse-engineered and comments mark big-endian and multi-scanner behavior as historically untested.

## Test Signals
Exercise SCSI INQUIRY/REQUEST_SENSE, image READ commands that must use `ep_image`, normal response reads via `ep_response`, write-like commands via `ep_out`, scatter/gather requests with multiple segments, nonzero LUN/ID/channel rejection, USB reset through SCSI host reset, disconnect during active command, and URB status paths for abort and hard errors. Scanner-specific tests should validate final status-byte propagation into `srb->result`.
