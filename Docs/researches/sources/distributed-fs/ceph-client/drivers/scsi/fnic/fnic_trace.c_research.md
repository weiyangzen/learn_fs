# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_trace.c

## Purpose

`fnic_trace.c` implements Cisco FNIC diagnostic trace support. It owns two global circular buffers: a generic FNIC event trace with fixed 64-byte records and an FC control-frame trace with fixed 256-byte records. It also formats driver statistics and live FNIC/iport/tport state into debugfs buffers.

## Important APIs, types, and functions

- `fnic_role_to_str()` converts supported FNIC roles to debug text.
- `fnic_trace_get_buf()` reserves the next generic trace slot under `fnic_trace_lock`.
- `fnic_get_trace_data()` formats generic trace entries, resolving function addresses with `sprint_symbol()` and jiffies timestamps with `jiffies_to_timespec64()`.
- `fnic_get_stats_data()` emits atomic counters from `struct fnic_stats`, including IO, abort, terminate, reset, firmware, VLAN, and miscellaneous counters.
- `fnic_get_debug_info()` prints current adapter, iport, fabric, and tport-list state.
- `fnic_trace_buf_init()`/`fnic_trace_free()` allocate and release the generic trace ring and debugfs hooks.
- `fnic_fc_trace_init()`/`fnic_fc_trace_free()` allocate and release the FC control trace ring.
- `fnic_fc_trace_set_data()` records transmit, receive, and link-event frames.
- `fnic_fc_trace_get_data()` and `copy_and_format_trace_data()` dump FC traces in formatted or raw hex form.

## Control flow

Initialization computes entry counts from module-controlled page counts, allocates one contiguous vmalloc-backed data area plus an array of per-entry offsets, initializes read/write indexes to zero, and registers debugfs files. Producers call `FNIC_TRACE()` or `fnic_fc_trace_set_data()` from driver paths; both advance a write index and, on overlap, advance the read index to preserve ring semantics. Readers snapshot the current read/write indexes while holding the relevant lock and append formatted text into a caller-provided debugfs buffer.

FC receive traces add synthetic Ethernet and FCoE header bytes filled with `0xff` because receive tracepoints do not have those headers available. Formatted FC output prints a timestamp, host number, frame type, length, and frame bytes with line breaks at Ethernet, FCoE, and FC header boundaries.

## State and persistence behavior

All trace state is process-lifetime kernel memory. Generic trace state is `fnic_trace_entries`, `fnic_trace_buf_p`, `fnic_max_trace_entries`, `trace_max_pages`, and `fnic_tracing_enabled`. FC trace state is `fc_trace_entries`, `fnic_fc_ctlr_trace_buf_p`, `fc_trace_max_entries`, `fnic_fc_tracing_enabled`, and `fnic_fc_trace_cleared`. Trace contents persist only until module teardown, explicit clear, wraparound overwrite, or reboot. Stats formatting mutates `stats->stats_timestamps.last_read_time`.

## Dependencies and integration points

The file depends on FNIC private headers `fnic_io.h` and `fnic.h`, trace types from `fnic_trace.h`, debugfs setup/teardown functions implemented elsewhere, SCSI FC transport definitions, vmalloc allocation, spinlocks, kernel time helpers, and kallsyms symbol formatting. It is consumed by FNIC IO, FC control, debugfs, and stats paths.

## Risks and edge cases

- The debugfs buffer size estimate uses `trace_max_pages * PAGE_SIZE * 3`; callers must allocate matching buffers or formatting truncates.
- Trace read formatting holds spinlocks while doing repeated `scnprintf()` and symbol lookup, which can be expensive for large rings.
- `min_t(u8, fc_trc_frame_len, ...)` truncates lengths through an 8-bit type; values above 255 are bounded by the 256-byte record design but must be understood as intentionally clipped.
- `fnic_fc_trace_cleared` causes the FC trace setter to zero the whole buffer under the trace lock on the next write.
- Generic trace stores function addresses differently for 32-bit and 64-bit builds, so mixed assumptions in consumers would corrupt output.

## Test signals

Useful checks include enabling/disabling trace module parameters, reading generic and FC debugfs files after IO, forcing ring wraparound, verifying FC receive traces include synthetic headers, checking formatted and raw FC dump modes, and validating teardown paths with module unload. KASAN/KCSAN coverage around concurrent trace writes and debugfs reads would be valuable.
