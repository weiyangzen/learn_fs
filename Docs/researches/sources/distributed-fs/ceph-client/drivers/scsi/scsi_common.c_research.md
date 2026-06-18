# sources/distributed-fs/ceph-client/drivers/scsi/scsi_common.c

## Purpose
`scsi_common.c` contains SCSI helper routines shared by initiator and target code. It provides command-size lookup, device-type names, persistent-reservation type conversion, LUN packing/unpacking, and sense-buffer parsing/building helpers.

## Important APIs, Types, And Functions
Exports include `scsi_command_size_tbl`, `scsi_device_type()`, `scsi_pr_type_to_block()`, `block_pr_type_to_scsi()`, `scsilun_to_int()`, `int_to_scsilun()`, `scsi_normalize_sense()`, `scsi_sense_desc_find()`, `scsi_build_sense_buffer()`, `scsi_set_sense_information()`, and `scsi_set_sense_field_pointer()`. These functions operate on UAPI PR enums, `struct scsi_lun`, raw sense buffers, and `struct scsi_sense_hdr`.

## Control Flow
Lookup helpers are table or switch based. LUN conversion packs/unpacks the 8-byte SCSI LUN representation two bytes at a time into host-endian `u64`. Sense normalization clears the destination header, validates the response code, then extracts sense key/ASC/ASCQ/additional length from descriptor or fixed sense format. Descriptor search walks descriptor-format sense data from byte 8 using each descriptor's length. Sense builders initialize fixed or descriptor sense formats and optionally append or update information and field-pointer descriptors.

## State And Persistence
The only static state is immutable lookup tables for command sizes and device type names. All other state is caller-provided buffers. No persistent system or device state is changed.

## Dependencies And Integration Points
This file depends on generic kernel helpers, unaligned big-endian accessors, SCSI common headers, and block persistent-reservation UAPI enums. It is used broadly by SCSI initiator, target, error handling, passthrough, and diagnostics code that needs common SCSI data-format handling.

## Risks And Edge Cases
Device type strings are ABI-visible through `/proc/scsi/scsi`, so existing entries must not change. `scsi_set_sense_information()` and `scsi_set_sense_field_pointer()` grow descriptor sense data but rely on caller-provided `buf_len`; boundary checks are critical. Fixed-format information can only mark VALID for 32-bit values. Descriptor parsing must tolerate short or malformed descriptors. Unknown PR type mappings return zero, so callers must treat zero as invalid/unsupported where appropriate.

## Test Signals
Signals include command-size results for all opcode groups, stable device type strings including well-known LUN and no-device values, PR type round trips, LUN conversion round trips for single- and multi-level LUNs, normalization of fixed and descriptor sense buffers, malformed/short sense rejection, descriptor lookup with multiple descriptors, building fixed and descriptor sense data, setting 32-bit and 64-bit information fields, and field-pointer sense-key-specific data with command/data and bit-pointer variants.
