# sources/cloud-native/containers-storage/pkg/system/chtimes.go

Purpose: safely changes file access and modification times while clamping values outside supported Unix time bounds.

Important APIs, types, and functions: `Chtimes(name string, atime time.Time, mtime time.Time) error`.

Control flow: computes Unix epoch and platform `maxTime`; if atime or mtime is before epoch or after max, replaces it with epoch. Calls `os.Chtimes`, then invokes platform `setCTime` to adjust create time where needed.

State and persistence: mutates filesystem timestamps. No package-level state beyond `maxTime` initialized in `init.go`.

Dependencies and integration points: depends on `os` and `time`; platform-specific `setCTime` files handle Unix no-op and Windows creation time.

Risks and edge cases: out-of-range times are silently coerced to epoch. On Unix, ctime cannot be directly set and changes as a side effect. Nanosecond precision depends on filesystem/platform.

Test signals: `chtimes_test.go`, Linux atime test, and Windows atime/create-time tests cover boundary clamping and valid time setting.
