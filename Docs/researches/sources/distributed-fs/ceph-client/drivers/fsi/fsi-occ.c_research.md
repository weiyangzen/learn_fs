<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-occ.c -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-occ.c

## Purpose
`fsi-occ.c` implements the FSI/SBEFIFO-backed On-Chip Controller interface for POWER systems. It exposes an `occN` miscdevice, submits OCC commands through SBEFIFO SRAM get/put commands, validates OCC responses and checksums, saves FFDC on failures, and creates an `occ-hwmon` child device.

## Important APIs, types, and functions
`struct occ` stores the parent devices, index/name, version, sequence number, shared buffers, miscdevice, and `occ_lock`. `struct occ_client` stores per-open buffers and read offsets. The exported command API is `fsi_occ_submit()`. SRAM helpers are `occ_getsram()`, `occ_putsram()`, and `occ_trigger_attn()`. Userspace file ops are `occ_open()`, `occ_write()`, `occ_read()`, and `occ_release()`.

## Control flow
Probe allocates a shared SBE response buffer, determines P9/P10 mode from OF match data, seeds a nonzero sequence number, allocates an OCC index, registers `/dev/occN`, and creates an OF or platform `occ-hwmon` child. A userspace write copies an OCC-format command into the per-client buffer, computes the command data length, and calls `fsi_occ_submit()`. Submission serializes on `occ_lock`, overwrites the request sequence number, computes checksum, writes the command to OCC SRAM through SBEFIFO, triggers OCC attention, polls the response header until status/sequence/cmd match or timeout, fetches the full response, validates response size and checksum, stores final response length, and returns it for later reads.

## State and persistence behavior
Runtime state includes the OCC sequence counter, per-device shared SBE buffer, per-client buffers/read offsets, and temporary FFDC copies into the caller's response buffer. No persistent state exists. Remove deregisters the miscdevice, nulls/frees the shared buffer under lock, removes child hwmon devices, and frees the IDA index.

## Dependencies and integration points
It depends on platform devices, OF matching `ibm,p9-occ` and `ibm,p10-occ`, miscdevice/fs/uaccess APIs, SBEFIFO exported APIs `sbefifo_submit()` and `sbefifo_parse_status()`, OCC UAPI constants, IDA allocation, and optional hwmon child creation.

## Risks and edge cases
Sequence-number uniqueness is critical because stale OCC responses can otherwise be accepted. Request/response length checks must account for OCC headers and two-byte checksums. P9 and P10 SRAM command formats differ by mode/address fields. Timeouts and command-in-progress statuses require careful polling without holding user locks incorrectly. Remove must prevent use after free by setting `occ->buffer = NULL` under `occ_lock`.

## Test signals
Signals include miscdevice open/write/read/release, P9 and P10 SRAM command formatting, checksum mismatch rejection, response timeout, stale sequence/cmd filtering, FFDC capture on SBE status errors, response-size overflow, hwmon child creation/removal, and concurrent clients serialized through `occ_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-occ.c -->
