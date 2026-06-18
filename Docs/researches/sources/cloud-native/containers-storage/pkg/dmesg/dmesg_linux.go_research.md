## sources/cloud-native/containers-storage/pkg/dmesg/dmesg_linux.go

Purpose: Linux helper to read recent kernel log messages.

Important APIs/types/functions: `Dmesg(size int) []byte`.

Control flow: allocates a byte slice of requested size and calls `SYS_SYSLOG` with action `3` (`SYSLOG_ACTION_READ_ALL`), returning bytes read or an empty slice on syscall error.

State and persistence: read-only kernel log access; no package state.

Dependencies and integration points: useful for diagnostics in storage/kernel error paths. Depends on `golang.org/x/sys/unix` and unsafe pointer syscall usage.

Risks: calling with `size == 0` would take `&b[0]` and panic; permissions or kernel restrictions often make syslog reads fail, returning empty bytes without error detail.

Test signals: `dmesg_linux_test.go` only logs output and has no assertions.
