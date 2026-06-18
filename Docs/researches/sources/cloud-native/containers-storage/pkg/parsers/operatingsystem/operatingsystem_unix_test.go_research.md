# sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_unix_test.go

Purpose: tests Linux operating system name parsing, os-release fallback, and container detection heuristics.

Important APIs, types, and functions: `TestGetOperatingSystem`, `TestIsContainerized`, and `TestOsReleaseFallback`.

Control flow: tests override `etcOsRelease`, `altOsRelease`, and `proc1Cgroup` to temporary files. They write invalid and valid os-release content, verify exact outputs/errors, and exercise cgroup layouts for host, systemd init.scope host, and Docker-like container paths.

State and persistence: writes temporary files under `os.TempDir` and restores package variables in defers.

Dependencies and integration points: depends on `os`, `filepath`, and `testing`. It validates `operatingsystem_linux.go`.

Risks and edge cases: using shared `os.TempDir` filenames can conflict if tests run in parallel, though these tests do not call `t.Parallel`. Cleanup defers include `os.Remove(dir)` on a system temp directory in fallback test, which is risky but likely harmless if the directory is not empty.

Test signals: strong parser signals for quoting requirements, duplicate PRETTY_NAME where later wins, default Linux fallback, alt release fallback, and cgroup container heuristics.
