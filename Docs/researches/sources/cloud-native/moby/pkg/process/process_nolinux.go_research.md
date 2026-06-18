# sources/cloud-native/moby/pkg/process/process_nolinux.go

Purpose: non-Linux stub for zombie detection.

APIs and flow: build-tagged `!linux` implementation of `zombie(pid)` always returns `(false, nil)`.

State and dependencies: no imports, no filesystem reads, no persistence.

Integration points: keeps the common `Zombie` API buildable on Unix platforms where `/proc/<pid>/stat` state parsing is not implemented.

Risks and tests: callers must not assume `Zombie` gives meaningful zombie detection outside Linux. Existing tests focus on `Alive`, not this stub.
