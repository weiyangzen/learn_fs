# sources/cloud-native/containers-storage/pkg/loopback/loopback_unsupported.go

Purpose: declares the `loopback` package for unsupported builds.

Important APIs, types, and functions: no functions or types are defined in this file.

Control flow: none.

State and persistence: none.

Dependencies and integration points: package declaration only. Because the Linux files carry explicit build tags, this file allows the package to exist on other platforms without loopback APIs.

Risks and edge cases: callers expecting loopback functions on non-Linux platforms will not compile unless guarded by build tags or platform-specific files.

Test signals: no tests; the signal is successful non-Linux package compilation where no loopback implementation is intended.
