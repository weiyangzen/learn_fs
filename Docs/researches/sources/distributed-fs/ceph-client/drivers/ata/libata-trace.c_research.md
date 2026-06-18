# sources/distributed-fs/ceph-client/drivers/ata/libata-trace.c

## Purpose
`libata-trace.c` supplies trace-event formatting helpers for libata. It turns status bytes, BMDMA status bytes, EH action/error masks, queued-command flags, taskfile flags, and selected ATA subcommands into readable strings consumed by `trace/events/libata.h`.

## Important APIs, Types, And Functions
The exported formatting helpers are `libata_trace_parse_status`, `libata_trace_parse_host_stat`, `libata_trace_parse_eh_action`, `libata_trace_parse_eh_err_mask`, `libata_trace_parse_qc_flags`, `libata_trace_parse_tf_flags`, and `libata_trace_parse_subcmd`. They all write into a `struct trace_seq` and return the pointer obtained from `trace_seq_buffer_ptr`.

## Control Flow
Each parser records the current trace-sequence buffer pointer, appends fixed tokens for every set bit or recognized subcommand, emits a trailing NUL, and returns the original pointer. Bitmask parsers first print a raw hex value for masks where that matters, then append symbolic names inside braces. `libata_trace_parse_subcmd` dispatches by ATA command and then by feature or `hob_nsect` subcommand fields for FPDMA receive/send, NCQ non-data, and ZAC management commands.

## State And Persistence
The file is stateless. It only appends to the caller-provided trace buffer; no global data or hardware state is changed.

## Dependencies And Integration Points
It depends on ATA constants from libata headers, Linux trace sequence helpers, and the tracepoint definitions in `trace/events/libata.h`. SFF/BMDMA and libata core paths use these helpers indirectly when tracepoints such as taskfile load, command issue, BMDMA status, HSM state, and error handling are enabled.

## Risks And Edge Cases
Trace text must stay aligned with current libata flag definitions. Missing bits are silently omitted, which can hide newer flags in traces. The EH action parser checks combined reset bits before individual soft/hard reset branches, making the individual branches unreachable when either reset bit is set through the combined expression; this is trace-only behavior but affects diagnostic clarity. Formatting relies on trace-sequence capacity handling by the tracing core.

## Test Signals
Enable libata tracepoints through ftrace/perf and issue commands that cover normal status bits, BMDMA interrupts/errors, EH reset/park/revalidate actions, NCQ and non-NCQ queued commands, pass-through commands, and ZAC/DSM/NCQ subcommands. Verify rendered trace text includes expected symbolic tokens and remains NUL-terminated.
