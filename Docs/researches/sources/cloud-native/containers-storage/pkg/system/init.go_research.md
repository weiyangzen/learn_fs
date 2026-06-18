# sources/cloud-native/containers-storage/pkg/system/init.go

Purpose: initializes the platform maximum time supported by `Chtimes`.

Important APIs, types, and functions: package variable `maxTime` and `init`.

Control flow: checks the size of `syscall.Timespec{}.Nsec`; if 64-bit, sets `maxTime` to the maximum int64 nanosecond time, otherwise to the maximum 32-bit Unix seconds time.

State and persistence: initializes package-global in-memory state. No persistence.

Dependencies and integration points: depends on `syscall`, `time`, and `unsafe`. `chtimes.go` uses `maxTime` to clamp timestamps.

Risks and edge cases: heuristic is based on `Timespec.Nsec` size, which is a proxy for supported time range. Filesystem-specific timestamp limits may be narrower.

Test signals: `Chtimes` tests use `maxTime` and verify it can be set/truncated on supported filesystems.
