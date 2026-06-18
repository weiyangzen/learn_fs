# sources/distributed-fs/ceph-client/drivers/scsi/scsi_trace.c

## Purpose

`scsi_trace.c` formats SCSI command descriptor blocks for tracepoints. It turns common CDB opcodes into compact human-readable strings containing LBA, transfer length, protection, allocation length, zone, service action, and related command fields.

## Important APIs, types, and functions

The exported parser is `scsi_trace_parse_cdb(struct trace_seq *p, unsigned char *cdb, int len)`. It dispatches to helpers for READ/WRITE 6, 10, 12, 16, and 32 byte commands; UNMAP; SERVICE ACTION IN(16); MAINTENANCE IN/OUT; ZBC IN/OUT; WRITE ATOMIC(16); variable-length commands; and a miscellaneous fallback. `SERVICE_ACTION16()` and `SERVICE_ACTION32()` decode service-action fields. Helpers use `trace_seq_buffer_ptr()`, `trace_seq_printf()`, `trace_seq_puts()`, `trace_seq_putc()`, and unaligned big-endian accessors.

## Control flow

Tracepoint code calls `scsi_trace_parse_cdb()` with a CDB. The top-level switch uses `cdb[0]` to pick a formatter. READ/WRITE helpers decode command-specific LBA and transfer length widths. Variable-length commands dispatch by 32-byte service action. Service-action and maintenance helpers map known service actions to command names and print `UNKNOWN` for unsupported actions. All helpers terminate the trace string with a NUL in the trace sequence; unsupported opcodes print `-`.

## State and persistence behavior

The file owns no persistent state. It only appends transient formatted text to the supplied `trace_seq`. It does not issue commands, mutate devices, or store decoded data.

## Dependencies and integration points

It depends on kernel trace sequence APIs, unaligned big-endian helpers, SCSI opcode definitions, and `trace/events/scsi.h`. It integrates with SCSI trace events that need CDB decoding for diagnostics and performance analysis.

## Risks and edge cases

The helpers assume the passed CDB has enough bytes for the opcode-specific fields; the `len` parameter is accepted but not used for bounds checks. Callers must therefore provide valid CDB storage. UNMAP computes `(regions - 8) / 16` on an unsigned value, so malformed region lengths below eight can produce a large decoded count. Opcode/service-action coverage is partial, so many valid SCSI commands intentionally fall back to `-` or `UNKNOWN`. Formatters must stay synchronized with SCSI opcode constants and command layouts.

## Test signals

Trace tests should feed representative CDBs for all handled opcodes and assert formatted strings, including WRITE SAME unmap bits, protection fields, 32-byte service actions, maintenance service actions, ZBC options, and WRITE ATOMIC boundary size. Negative tests should cover unknown opcodes and unknown service actions. Fuzz or KUnit tests with short CDB buffers would highlight the current lack of `len` validation.
