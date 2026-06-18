# sources/cloud-native/nydus-snapshotter/pkg/cgroup/manager.go

Purpose: exposes a small manager object around a version-specific daemon cgroup.

Important APIs and functions: `Manager` stores name/config/cgroup; `Opt` carries name and config; `NewManager`, `AddProc`, and `Delete`.

Control flow: `NewManager` checks support, logs cgroup mode, creates a v1 or v2 cgroup through `createCgroup`, and returns a manager. `AddProc` and `Delete` forward to the underlying `DaemonCgroup`.

State and persistence: manager holds the created cgroup handle in memory; cgroup state persists in the kernel cgroup filesystem until deleted.

Dependencies and integration points: uses containerd logging and version-specific cgroup packages. Intended callers add daemon PIDs and clean up on shutdown.

Risks: comments require callers to ensure `*Manager` is non-nil; methods will panic on nil receiver or nil `cgroup`. No recovery path exists if cgroup creation partially succeeds.

Test signals: no listed tests for manager construction or process addition/deletion.
