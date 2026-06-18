# sources/distributed-fs/ceph-client/kernel/trace/trace_seq.c

## Purpose

`trace_seq.c` implements `struct trace_seq`, the tracing-specific formatting buffer used before data is copied into seq_file or user buffers. It wraps `seq_buf` with no-partial-write semantics and exported helpers. The complete 457-line file was read.

## Important APIs, Types, and Functions

Exports include `trace_print_seq()`, `trace_seq_printf()`, `trace_seq_bitmask()`, `trace_seq_bitmask_list()`, `trace_seq_vprintf()`, `trace_seq_bprintf()`, `trace_seq_puts()`, `trace_seq_putc()`, `trace_seq_putmem()`, `trace_seq_putmem_hex()`, `trace_seq_path()`, `trace_seq_to_user()`, `trace_seq_hex_dump()`, and `trace_seq_acquire()`. `__trace_seq_init()` lazily initializes zeroed objects.

## Control Flow

Write helpers exit if `full`, initialize lazily, save old length, attempt a `seq_buf` operation, and restore old length plus mark `full` on overflow. `trace_print_seq()` moves contents to seq_file and resets only on success. `trace_seq_to_user()` copies from `readpos` and advances it on success.

## State and Persistence Behavior

State is caller-owned: underlying `seq_buf`, sticky `full` flag, and read position. No global state is owned by this file.

## Dependencies and Integration Points

It depends on `linux/trace_seq.h`, `seq_buf`, seq_file, uaccess, path formatting, bitmap formatting, binary printf, and trace event printers throughout ftrace.

## Risks and Edge Cases

The central contract is all-or-nothing visible writes. Any missed rollback exposes partial output. `trace_seq_acquire()` assumes callers checked space. `trace_seq_to_user()` returns `-EBUSY` when drained, which readers use as a refill signal.

## Test Signals

Cover overflow rollback, printf/bprintf/bitmask/path/hex helpers, boundary puts/putc/mem, repeated user reads, zero-initialized sequences, and `trace_print_seq()` reset behavior.
