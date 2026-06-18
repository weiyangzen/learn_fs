# sources/cloud-native/containers-storage/pkg/system/meminfo_unsupported.go

Purpose: provides unsupported memory-info implementation for platforms without a concrete reader.

Important APIs, types, and functions: `ReadMemInfo`.

Control flow: returns nil and `ErrNotSupportedPlatform`.

State and persistence: no state and no OS reads.

Dependencies and integration points: selected for platforms other than Linux, Windows, Solaris, and FreeBSD+cgo. Keeps callers compiling while requiring unsupported handling.

Risks and edge cases: comment mentions Linux and Windows even though this build tag also excludes Solaris and FreeBSD+cgo; wording is stale. Callers must handle unsupported errors.

Test signals: no direct tests in requested files.
