# sources/cloud-native/moby/daemon/update_linux.go

## Purpose
Linux implementation of `toContainerdResources`, translating Docker API `container.Resources` into the daemon's containerd resource struct backed by OCI runtime-spec Linux resource types.

## Important APIs, Types, And Functions
The single exported-in-package function is `toContainerdResources(resources container.Resources) (*libcontainerdtypes.Resources, error)`. It populates `specs.LinuxBlockIO`, `specs.LinuxCPU`, `specs.LinuxMemory`, and pids via helpers such as `getBlkioWeightDevices`, `getBlkioThrottleDevices`, and `getPidsLimit`.

## Control Flow
The function lazily allocates `BlockIO` only when a blkio field is explicitly present. It converts weight, read/write BPS, and read/write IOPS devices, returning early on conversion errors. CPU cpuset fields are always copied into a temporary `LinuxCPU`; shares, period, and quota are pointer-populated only when non-zero. `NanoCPUs` derives quota from a 100ms period unless explicit quota/period values fill missing values. Memory limit, reservation, and positive swap values are similarly pointer-populated. Empty CPU or memory structs are omitted.

## State And Persistence
No persistent state is modified. The result is an update payload consumed by containerd/runc integration, with nil substructures intentionally representing "unset" resources.

## Dependencies And Integration Points
Depends on Docker API container resources, internal libcontainerd types, OCI runtime-spec structs, and blkio/pids helper functions in the daemon package. It is used by container update flows that need Linux cgroup resource mutation through containerd.

## Risks
Pointer-versus-zero semantics are critical: accidentally allocating a subresource or setting a zero pointer can change containerd update behavior. `NanoCPUs` precedence over explicit quota/period must remain compatible with Docker API behavior. Blkio helpers can fail on invalid device specs, so callers must preserve errors.

## Test Signals
`update_linux_test.go` validates that an empty `container.Resources{}` produces a resource object whose nested fields are unset, guarding against default updates that would mutate existing container limits.
