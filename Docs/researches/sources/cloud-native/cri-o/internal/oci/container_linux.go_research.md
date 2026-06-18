# sources/cloud-native/cri-o/internal/oci/container_linux.go

## Purpose
Implements Linux-specific container helpers: conmon cgroup cleanup, seccomp profile path storage, `/proc/<pid>/stat` PID identity parsing, and CRI runtime-user projection from the OCI process spec.

## Important APIs and Control Flow
`CleanupConmonCgroup` loads and deletes the recorded conmon cgroupfs path unless the container is spoofed or no path was recorded. `SetSeccompProfilePath`/`SeccompProfilePath` store seccomp path metadata. `GetPidStartTimeFromFile`, `getPidStartTime`, `getPidStatData`, and `getPidStatDataFromFile` parse `/proc/<pid>/stat` by finding the last `)` to safely skip command names containing spaces, then reading state and start-time fields. `SetRuntimeUser` converts OCI UID/GID/additional groups into CRI `ContainerUser`.

## Dependencies, Integration, Risks, and Tests
Depends on Podman cgroups, OCI spec, CRI types, and CRI-O logging. It is directly used by `Container.SetSpec`, `ContainerState.SetInitPid`, `Container.verifyPid`, and cgroup cleanup paths. Risks include proc stat format assumptions and 4 KiB read limit. Tests cover malformed stat files, missing files, successful start time extraction, and runtime-user/resource-adjacent behavior.
