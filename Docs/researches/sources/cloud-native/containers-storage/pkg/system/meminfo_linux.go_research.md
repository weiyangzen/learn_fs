# sources/cloud-native/containers-storage/pkg/system/meminfo_linux.go

Purpose: implements Linux memory/swap statistics retrieval from `/proc/meminfo`.

Important APIs, types, and functions: `ReadMemInfo` and private `parseMemInfo`.

Control flow: `ReadMemInfo` opens `/proc/meminfo`, defers close, and calls `parseMemInfo`. The parser scans lines, expects at least three fields with `kB`, parses the numeric field, converts KiB to bytes, and records four known keys.

State and persistence: reads procfs snapshot only.

Dependencies and integration points: depends on `bufio`, `io`, `os`, `strconv`, `strings`, and `docker/go-units`. Used by host system reporting and resource calculations.

Risks and edge cases: malformed or unsupported lines are silently skipped. Missing keys leave zero values. Scanner token limits are not customized but proc meminfo lines are small.

Test signals: `meminfo_unix_test.go` verifies correct conversion and skipping malformed lines.
