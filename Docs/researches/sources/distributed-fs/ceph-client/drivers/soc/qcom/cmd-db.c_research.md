# sources/distributed-fs/ceph-client/drivers/soc/qcom/cmd-db.c

## Purpose
Maps Qualcomm Command DB reserved memory and exports lookup helpers so other drivers can translate resource key strings into RPMh/shared-resource addresses, slave IDs, and auxiliary data.

## Important APIs, Types, And Functions
Exports `cmd_db_ready()`, `cmd_db_read_addr()`, `cmd_db_read_aux_data()`, `cmd_db_match_resource_addr()`, and `cmd_db_read_slave_id()`. Database layout types are `struct cmd_db_header`, `struct rsc_hdr`, and `struct entry_header`. Internal helpers include `cmd_db_magic_matches()`, `rsc_to_entry_header()`, `rsc_offset()`, and `cmd_db_get_header()`.

## Control Flow
The core initcall registers a platform driver for `qcom,cmd-db`. Probe looks up the reserved memory attached to the DT node, maps it write-combining with `devm_memremap()`, validates the magic bytes, creates a debugfs dump file, and marks PM as not required. Query APIs first call `cmd_db_ready()`, pad the requested ID to the fixed 8-byte entry ID field, scan each populated resource header and its entry array, then return the requested address, aux data pointer/length, or decoded slave ID.

## State And Persistence
Global `cmd_db_header` points at reserved memory owned by firmware/bootloader. The data is read-only from this driver’s perspective after mapping. Debugfs exposes a live dump; no data is persisted by Linux.

## Dependencies And Integration Points
Depends on OF reserved memory, platform bus, debugfs, little-endian layout conversion, and `soc/qcom/cmd-db.h`. RPMh, interconnect, regulator, clock, and other Qualcomm resource drivers consume the exported lookup helpers.

## Risks
There is a single global database pointer, so multiple instances are not modeled. The scanner trusts offsets and counts after magic validation; malformed firmware data could point entries outside the reserved memory. Query IDs are fixed-width and padded, so longer logical names would not match. Debugfs file operations are partially conditional on `CONFIG_DEBUG_FS`, but the file operations object exists either way.

## Test Signals
`cmd_db_ready()` should return `-EPROBE_DEFER` before probe, zero after valid probe, and `-EINVAL` on bad magic. Known resource IDs should produce expected addresses and aux blobs. Debugfs `cmd-db` should list ARC/VRM/BCM entries when enabled.
