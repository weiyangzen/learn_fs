# sources/cloud-native/containers-storage/pkg/system/meminfo_unix_test.go

Purpose: tests Linux `/proc/meminfo` parsing.

Important APIs, types, and functions: `TestMemInfo`.

Control flow: feeds a static multiline meminfo string with four valid kB entries and several malformed entries into `parseMemInfo`, then checks byte conversion using `units.KiB`.

State and persistence: no persistence; parser consumes an in-memory string reader.

Dependencies and integration points: depends on `strings`, `testing`, and `docker/go-units`. It validates the Linux parser without requiring host `/proc`.

Risks and edge cases: does not test scanner errors, missing keys, very large values, or actual `ReadMemInfo` file open.

Test signals: confirms known fields are parsed, units converted to bytes, and malformed lines ignored.
