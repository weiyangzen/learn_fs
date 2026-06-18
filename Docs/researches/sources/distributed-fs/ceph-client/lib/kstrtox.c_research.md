# sources/distributed-fs/ceph-client/lib/kstrtox.c

Purpose: implements strict string-to-integer and string-to-boolean conversion helpers with overflow detection, base autodetection, and user-copy wrappers.

Important APIs: `_parse_integer_fixup_radix`, `_parse_integer_limit`, `_parse_integer`, `kstrtoull`, `kstrtoll`, `_kstrtoul`, `_kstrtol`, `kstrtouint`, `kstrtoint`, `kstrtou16/s16/u8/s8`, `kstrtobool`, `kstrtobool_from_user`, and macro-generated `*_from_user` integer wrappers.

Control flow: radix fixup chooses 16 for `0x`, 8 for leading zero, or 10 otherwise, then skips the hex prefix. `_parse_integer_limit()` consumes valid digits up to `max_chars`, sets an overflow bit on range overflow, and returns consumed length. Typed wrappers reject no digits, trailing junk except one newline, overflow, sign/type mismatch, and out-of-range narrowing. Boolean parsing accepts common one-character true/false prefixes and `on`/`off`.

State and persistence: no persistent state. Results are only written on successful conversion, preserving caller output on errors.

Dependencies and integration: depends on ctype, errno, math64 division, user access, and exported symbols. Widely used for sysfs, procfs, module parameters, and kernel parsers.

Risks: base support is documented up to 16; unsigned helpers reject minus signs; bool parsing checks only enough characters to distinguish accepted prefixes; from-user wrappers truncate input to fixed local buffers sized for binary representation; callers must check return codes.

Test signals: parser unit tests for base autodetection, signs, newline allowance, overflow boundaries for every type, invalid trailing bytes, user-copy faults, and bool synonyms.
