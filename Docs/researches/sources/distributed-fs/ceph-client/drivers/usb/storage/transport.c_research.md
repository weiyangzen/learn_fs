# sources/distributed-fs/ceph-client/drivers/usb/storage/transport.c

## Purpose

`transport.c` implements the low-level USB Mass Storage transport engine for classic `usb-storage`. It translates SCSI commands into Control/Bulk/Interrupt or Bulk-Only USB transactions, manages URB and scatter-gather transfer lifetimes, performs automatic REQUEST SENSE, and drives reset recovery when a transport or device phase fails.

## Important APIs, Types, and Functions

Transfer helpers include `usb_stor_control_msg()`, `usb_stor_ctrl_transfer()`, `usb_stor_bulk_transfer_buf()`, `usb_stor_bulk_srb()`, `usb_stor_bulk_transfer_sg()`, `usb_stor_clear_halt()`, and `usb_stor_stop_transport()`. `usb_stor_msg_common()` is the shared URB submission/wait path and is the center of the abort/disconnect race contract. `interpret_urb_result()` maps USB status values into `USB_STOR_XFER_*` results.

Transport entry points are `usb_stor_CB_transport()` for Control/Bulk and Control/Bulk/Interrupt devices, `usb_stor_Bulk_transport()` for Bulk-Only Transport, `usb_stor_Bulk_max_lun()` for discovery, and reset helpers `usb_stor_CB_reset()`, `usb_stor_Bulk_reset()`, and `usb_stor_port_reset()`. `usb_stor_invoke_transport()` is the SCSI-facing orchestration layer that calls the selected transport and then handles autosense, capacity hacks, underflow checks, and reset recovery.

## Control Flow

Queued SCSI commands enter through the protocol layer and call `usb_stor_invoke_transport()`. That clears residual data, invokes the device-specific transport function pointer, and short-circuits if the command timed out or the transport reported a fatal error. Command failures trigger autosense unless the transport supplied sense data itself. Autosense temporarily rewrites the SCSI command with `scsi_eh_prep_cmnd()`, selects 6- or 12-byte REQUEST SENSE based on subclass, retries with a smaller sense buffer if a device rejects large sense, then restores the original command and updates `srb->result`.

Bulk-Only transport sends a CBW over bulk-out, optionally transfers data over bulk-in or bulk-out, then reads a CSW. It handles delayed devices (`US_FL_GO_SLOW`), long reads by returning fake invalid-CDB sense data, skipped data phases where the CSW appears in the data buffer, zero-length CSWs that need a retry, bad tags optionally masked by `US_FL_BULK_IGNORE_TAG`, learned nonstandard CSW signatures, and unreliable residues via `US_FL_IGNORE_RESIDUE`. CBI transport sends the command over control, transfers any data over bulk, then reads a two-byte interrupt status for CBI devices and clears the data pipe after reported failures.

## State and Persistence Behavior

There is no file-backed persistence. State is per-device in `struct us_data`: `current_urb`, `current_sg`, `iobuf`, DMA address, dynamic flags, current SCSI command, learned CSW signature, tag counter, max LUN, and last-sector retry state. Hardware and device state changes include endpoint halt clearing, bulk/class resets, and port resets. The last-sector hack mutates in-memory retry counters and may rewrite a command result/sense buffer to stop repeated end-of-disk retries.

## Dependencies and Integration Points

The file depends on USB core URBs, scatter-gather helpers, endpoint halt/reset APIs, SCSI command and error-handling helpers, block disk capacity data, and usb-storage protocol glue. It exports many functions for usb-storage subdrivers and depends on `usb.h`, `transport.h`, `protocol.h`, `scsiglue.h`, and `debug.h`.

## Risks and Edge Cases

Abort and disconnect races are the dominant risk. The code relies on precise ordering around `US_FLIDX_URB_ACTIVE`, `US_FLIDX_SG_ACTIVE`, `US_FLIDX_ABORTING`, and `US_FLIDX_DISCONNECTING` so an active transfer is cancelled exactly once and never during `usb_submit_urb()`. Autosense rewrites live SCSI command fields and must restore them on every path. Device compatibility handling is deliberately permissive, so incorrect residues, signatures, tags, or skipped phases can mask real device faults. Reset recovery drops `dev_mutex` for port reset and then reacquires it, so call sites must follow the locking contract.

## Test Signals

Useful validation includes BOT and CBI devices, short/long/stalled transfers, SG and non-SG buffers, timeout/abort/disconnect during URB submission and wait, GetMaxLUN failures, bad CSW signature/tag/residue cases, skipped data phases, autosense success/failure/large-sense fallback, last-sector capacity quirks, class reset fallback after port reset failure, and endpoint halt clearing after STALL.
