# sources/cloud-native/containers-storage/pkg/system/chtimes_linux_test.go

Purpose: validates Linux access-time behavior for `Chtimes`.

Important APIs, types, and functions: helper `atime` and `TestChtimesLinux`.

Control flow: creates a temp file, sets atime/mtime to epoch, before-epoch, after-epoch, and max-time combinations, then stats the file and compares Linux `Atim`.

State and persistence: mutates timestamps on a temporary file.

Dependencies and integration points: depends on `os`, `syscall`, `testing`, and `time`; uses shared `prepareTempFile` from `chtimes_test.go`.

Risks and edge cases: filesystem timestamp precision may require truncation for max-time checks. It is Linux-only and does not test ctime directly.

Test signals: confirms atime clamping to epoch for invalid values and correct atime for valid/max values on Linux.
