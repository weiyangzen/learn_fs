# sources/cloud-native/cri-o/internal/oci/container_freebsd.go

## Purpose
Provides FreeBSD+cgo process start-time lookup for container PID identity checks. This keeps `Container.verifyPid` useful on FreeBSD without requiring `/proc`.

## Important APIs, Control Flow, and Dependencies
`getPidStartTime` delegates to `getPidStatDataFromSysctl`; `getPidStatData` returns only start time and an empty process state. `getPidStatDataFromSysctl` calls `unix.SysctlRaw("kern.proc.pid", pid)`, checks the returned byte length against `C.sizeof_struct_kinfo_proc`, casts to `struct kinfo_proc`, and formats `ki_start` seconds/microseconds. `SetRuntimeUser` is a no-op on this platform.

## State, Integration, Risks, and Tests
This file feeds `ContainerState.InitStartTime` and PID-wrap protection. It does not report process state, so zombie/defunct filtering in `container.go` cannot work on this path. The cgo unsafe cast and FreeBSD kernel structure size are the main portability risks; no dedicated FreeBSD test appears in this subset.
