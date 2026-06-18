# sources/distributed-fs/ceph-client/lib/string_helpers.c

## Purpose
Implements higher-level string utilities that do not belong in low-level `string.c`: size formatting, integer-array parsing, escape/unescape transformations, quotable string allocation, managed string arrays, whitespace/sysfs matching helpers, replacement/padding, and FORTIFY reporting.

## APIs, Control Flow, and State
Important exports include `string_get_size()`, `parse_int_array()`, `parse_int_array_user()`, `string_unescape()`, `string_escape_mem()`, `kstrdup_quotable()`, `kstrdup_quotable_cmdline()`, `kstrdup_quotable_file()`, `kstrdup_and_replace()`, `kasprintf_strarray()`, `kfree_strarray()`, `devm_kasprintf_strarray()`, `skip_spaces()`, `strim()`, `sysfs_streq()`, `match_string()`, `__sysfs_match_string()`, `strreplace()`, `memcpy_and_pad()`, and, under FORTIFY, overflow-reporting functions. `string_get_size()` scales block counts into SI or IEC units with three significant figures. Unescape control flow recognizes selected backslash classes in priority order. Escape control flow applies `only`, printable/ascii filters, and class-specific escaping, returning the output size that would have been generated even when truncated. Allocation helpers build escaped copies for logging command lines and file paths. Devres helpers attach string-array cleanup to a device.

Persistent state is limited to devres-managed allocations owned by devices; otherwise allocations are caller-owned and freed with `kfree()`/`kfree_strarray()`.

## Dependencies, Integration, Risks, and Tests
Depends on slab, usercopy, ctype, hex helpers, get_options, task command-line access, file path rendering, devres, KUnit bug support, and optional FORTIFY metadata. Integration points include sysfs parsers, logging/audit paths, device drivers, proc/debug output, and fortified string/memory wrappers. Risks include escape flag priority surprises, non-NUL-terminated `string_escape_mem()` output, allocation leaks on partial string-array failure, sysfs newline matching assumptions, unsynchronized task command-line reads, and FORTIFY panic paths intentionally crashing after reporting. Test signals include string_helpers KUnit tests, sysfs input tests, escape/unescape round trips, usercopy fault injection for `parse_int_array_user()`, devres teardown tests, and FORTIFY overflow tests.
