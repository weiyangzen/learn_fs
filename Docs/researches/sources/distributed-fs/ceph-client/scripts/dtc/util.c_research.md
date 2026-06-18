# sources/distributed-fs/ceph-client/scripts/dtc/util.c

Purpose: Implements shared dtc utility functions for allocation-backed strings, path printing, device-tree blob file I/O, escape decoding, data formatting, type option decoding, version output, and standardized usage output.

Important APIs/functions: `fprint_path_escaped()`, `xstrdup()`, `xstrndup()`, `xasprintf()`, `xasprintf_append()`, `join_path()`, `util_is_printable_string()`, `get_escape_char()`, `utilfdt_read_err()`, `utilfdt_read()`, `utilfdt_write_err()`, `utilfdt_write()`, `utilfdt_decode_type()`, `utilfdt_print_data()`, `util_version()`, and `util_usage()`.

Control flow: File reads grow a buffer by doubling until `read()` returns zero; writes use `fdt_totalsize()` and loop until all bytes are written. Escape decoding dispatches C-style escapes, octal, and hex. `util_usage()` aligns long options before printing help and exits success or failure depending on `errmsg`.

State/persistence: No long-lived mutable module state. Functions allocate caller-owned buffers and write to stdin/stdout/stderr or named files. `util_version()` and `util_usage()` terminate the process.

Dependencies/integration: Depends on libc/POSIX, `libfdt.h`, `version_gen.h`, and declarations from `util.h`. Used broadly by dtc and libfdt command-line utilities.

Risks: `utilfdt_read_err()` stores the buffer capacity in `*len`, not the final bytes read, which callers must understand. It closes fd 0 when reading `-`. `xavsprintf_append()` returns `strlen(p)`, which can truncate conceptual length for embedded NUL text. `utilfdt_decode_type()` has documented TODOs for 8-byte and octal formats.

Test signals: Cover escaped characters, invalid `\x`, printable string lists, binary data formatting, stdin/stdout I/O, partial writes, invalid format strings, help alignment, and version output.
