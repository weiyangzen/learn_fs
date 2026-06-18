# sources/cloud-native/nydus-snapshotter/pkg/cgroup/cgroup.go

Purpose: provides shared cgroup configuration, support detection, mode display, and version-specific factory logic for placing daemon processes in memory-limited cgroups.

Important APIs and functions: `defaultSlice` is `system.slice`; `ErrCgroupNotSupported`; `Config` with `MemoryLimitInBytes`; `DaemonCgroup` interface with `Delete` and `AddProc`; `createCgroup`, `supported`, and `displayMode`.

Control flow: `createCgroup` checks `cgroups.Mode()` and uses v2 implementation for unified mode, otherwise v1 implementation. `supported` rejects only unavailable mode. `displayMode` maps containerd cgroups mode enum to strings.

State and persistence: no mutable state here; actual cgroups are managed by v1/v2 packages under system cgroup filesystem.

Dependencies and integration points: wraps `github.com/containerd/cgroups/v3` and local `pkg/cgroup/v1`/`v2` packages. Used by `manager.go` to create a process manager.

Risks: hybrid mode falls through to v1, which is probably intentional but worth noting. Memory limit semantics differ between v1 and v2; config has only one field. The default slice is hard-coded.

Test signals: no listed tests directly cover cgroup mode selection or display.
