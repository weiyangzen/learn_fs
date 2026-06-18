# sources/cloud-native/cri-o/internal/oci/container_freebsd_nocgo.go

## Purpose
Provides the FreeBSD non-cgo fallback for process start-time lookup using procfs.

## Important APIs, Control Flow, and Dependencies
`getPidStartTime` formats `/proc/<pid>/status` and delegates to `getPidStatDataFromFile`. That parser reads the file, splits by whitespace, and returns field index 7 as the start time. `getPidStatData` returns an empty process state plus start time. `SetRuntimeUser` is a no-op.

## State, Integration, Risks, and Tests
The code supports PID identity tracking for `ContainerState.InitStartTime`, but requires FreeBSD procfs to be mounted and does not bounds-check the split before indexing. Missing process-state support limits zombie detection. Tests in this subset exercise Linux parsing only, not this FreeBSD fallback.
