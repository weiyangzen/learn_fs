# sources/distributed-fs/ceph-client/include/linux/trace_seq.h

## Purpose
Defines `struct trace_seq`, the fixed-size formatting buffer used by tracing print paths to build lines and binary-derived text safely.

## Important APIs, Types, And Functions
Exports `TRACE_SEQ_SIZE`, `TRACE_SEQ_BUFFER_SIZE`, `trace_seq_init()`, `trace_seq_used()`, `trace_seq_buffer_ptr()`, `trace_seq_has_overflowed()`, `trace_seq_pop()`, and tracing-enabled formatting/copy helpers such as `trace_seq_printf()`, `trace_seq_bprintf()`, `trace_print_seq()`, `trace_seq_to_user()`, `trace_seq_puts()`, `trace_seq_putmem_hex()`, `trace_seq_path()`, `trace_seq_bitmask()`, `trace_seq_hex_dump()`, and `trace_seq_acquire()`.

## Control Flow
Callers initialize a `trace_seq`, append formatted fragments, inspect overflow, and flush to `seq_file` or userspace. The inline `trace_seq_used()` deliberately uses `seq_buf_used()` rather than raw length so overflowed buffers do not expose undefined memory lengths.

## State, Persistence, And Dependencies
State is per `trace_seq`: embedded `seq_buf`, read position, full flag, and roughly 8 KiB backing buffer. It depends on `seq_buf` and page-size constants.

## Integration Points
Used by trace event output, flag/symbol printers, bitmask/hex dump renderers, tracefs reads, and dynamic event formatting.

## Risks And Test Signals
Risks include treating overflowed `seq.len` as valid, failing to check `full`, and returning pointers after further appends move the write position. Test signals include long-format overflow tests, user-copy length tests, hex dump output, and disabled-config no-op builds.
