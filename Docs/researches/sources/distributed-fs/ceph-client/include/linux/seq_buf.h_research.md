# sources/distributed-fs/ceph-client/include/linux/seq_buf.h

Purpose: `seq_buf.h` defines a fixed-size string/binary formatting buffer used by tracing and other code that wants seq-file-like formatting without a file. It tracks overflow explicitly and offers print, append, hex, path, user-copy, and printk helpers.

Important APIs/types/functions: `struct seq_buf` stores `buffer`, `size`, and `len`. Helpers include `DECLARE_SEQ_BUF()`, `seq_buf_clear()`, `seq_buf_init()`, `seq_buf_has_overflowed()`, `seq_buf_set_overflow()`, `seq_buf_buffer_left()`, `seq_buf_used()`, `seq_buf_str()`, `seq_buf_get_buf()`, `seq_buf_commit()`, and `seq_buf_pop()`. External APIs include `seq_buf_printf()`, `seq_buf_vprintf()`, `seq_buf_print_seq()`, `seq_buf_to_user()`, `seq_buf_puts()`, `seq_buf_putc()`, `seq_buf_putmem()`, `seq_buf_putmem_hex()`, `seq_buf_path()`, `seq_buf_hex_dump()`, optional `seq_buf_bprintf()`, and `seq_buf_do_printk()`.

Control flow: Callers initialize a buffer, append through typed helpers or reserve/commit raw bytes, detect overflow when `len > size`, and call `seq_buf_str()` before treating the storage as a NUL-terminated string. Negative `seq_buf_commit()` marks overflow.

State and persistence behavior: State is caller-owned memory plus the current length. Overflow is sticky until `seq_buf_clear()` resets length. No allocation is performed by the inline helpers.

Dependencies and integration points: It depends on `seq_file` for printing into seq files, bug/minmax helpers, path formatting, user copy, binary printf, and tracing/logging paths.

Risks: `seq_buf_str()` warns and returns an empty string for zero-sized buffers. `seq_buf_commit()` BUGs if callers commit more bytes than reserved unless they signal overflow with a negative value. `len > size` is the overflow sentinel and must be preserved.

Test signals: Zero-sized buffers, exact-fit and overflow appends, reserve/commit API, negative commit, NUL termination after overflow, user copy offsets, path escaping, hex dumps, and binary printf builds.
