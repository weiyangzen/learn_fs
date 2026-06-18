# sources/distributed-fs/ceph-client/lib/seq_buf.c

## Purpose
Provides bounded formatting helpers for `struct seq_buf`, a small reusable descriptor for writing text or raw bytes into a fixed buffer. It bridges formatted printing, binary printf replay, path rendering, hex dumps, printk emission, and userspace copying without requiring a live `seq_file`.

## APIs, Control Flow, and State
Important APIs are `seq_buf_print_seq()`, `seq_buf_vprintf()`, `seq_buf_printf()`, `seq_buf_do_printk()`, optional `seq_buf_bprintf()`, `seq_buf_puts()`, `seq_buf_putc()`, `seq_buf_putmem()`, `seq_buf_putmem_hex()`, `seq_buf_path()`, `seq_buf_to_user()`, and `seq_buf_hex_dump()`. All writers check available capacity through `s->len` and `s->size`, advance `s->len` on success, and set the seq_buf overflow state on truncation. `seq_buf_do_printk()` turns the buffer into a NUL-terminated string and prints it line by line with a caller-supplied log level. `seq_buf_path()` borrows writable space with `seq_buf_get_buf()`, renders a dentry path with `d_path()`, escapes via `mangle_path()`, then commits the actual byte count. `seq_buf_to_user()` copies a requested subrange and returns `-EBUSY` when the requested start is already past the buffer.

The only persistent state is the caller-owned `struct seq_buf`: buffer pointer, size, current length, and overflow marker. No global state is created.

## Dependencies, Integration, Risks, and Tests
Depends on printk, seq_file, vsnprintf/bstr_printf, string/hex helpers, dcache path rendering, and uaccess. Integration points include tracing, debugfs/procfs emitters, diagnostics that collect output before printing, and sysfs-style buffered output. Risks include off-by-one capacity handling, assuming all functions NUL-terminate raw `putmem()` content, failing to inspect overflow, using `seq_buf_to_user()` as if short copies are impossible, and path rendering with too-small buffers. Test signals include seq_buf KUnit coverage, trace output tests, hex dump comparisons, path escaping tests, copy_to_user fault injection, and boundary cases where `s->len == s->size - 1` or `s->size == 0`.
