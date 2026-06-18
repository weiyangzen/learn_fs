# sources/cloud-native/cri-o/internal/factory/container/device_linux.go

## Purpose
Implements Linux OCI device setup for containers, including configured CRI-O devices, annotation devices, privileged host-device exposure, CRI container device requests, directory-of-devices expansion, device ownership from security context, and CDI injection.

## Important APIs, Types, And Functions
- `SpecAddDevices` clears existing Linux devices, adds configured and annotation devices plus resource cgroup permissions, optionally adds all host devices for privileged containers, then applies CRI container `Devices`.
- `specAddHostDevicesIfPrivileged` imports `devices.HostDevices()` and grants blanket `rwm` cgroup access for privileged containers unless `privilegedWithoutHostDevices` is set.
- `specAddContainerConfigDevices` resolves host paths securely, calls `devices.DeviceFromPath`, maps to container paths, appends matching `LinuxDeviceCgroup` entries, and recursively walks directories containing device nodes.
- `SpecInjectCDIDevices` merges CRI `CDIDevices` and CDI annotation requests, skips duplicates from annotations, refreshes the CDI registry, and calls `cdi.InjectDevices`.
- `getDeviceUserGroupID` optionally replaces host UID/GID with non-root `RunAsUser`/`RunAsGroup`.

## Control Flow
Device addition starts by resetting `Spec().Config.Linux.Devices`, so each call reconstructs the device list. Static configured and annotation devices are added first. Privileged containers then receive host devices and a broad resources device allow rule. Finally CRI devices are validated: privileged containers using a different container path must not collide with an existing host path, host paths are secure-joined under `/`, device nodes are added directly, and non-device directories are walked for child device nodes. CDI injection separately gathers device names from the structured CRI field and legacy annotations, refreshes registry state best-effort, then injects CDI-provided spec edits.

## State And Persistence
Mutates the in-memory OCI spec generator: `Linux.Devices`, `Linux.Resources.Devices`, environment, mounts, hooks, and other CDI edits may be changed. No durable state is written here. CDI registry state is refreshed through the external CDI library, and later factory call ordering must preserve the edits made by CDI.

## Dependencies And Integration Points
Depends on runc/libcontainer device discovery, OCI runtime-spec types, CRI API security context, CRI-O device config, `securejoin`, CRI-O `utils.IsDirectory`, CRI-O logging, and the CNCF CDI library. It integrates with kubelet CRI device requests and runtime-spec cgroup device controls.

## Risks And Edge Cases
Resetting `Linux.Devices` discards previous device edits. Privileged host-device import can expose broad host device access. Directory walking ignores errors and silently skips non-device children. `strings.Replace` assumes child paths are under the source directory. Device ownership override applies only for non-root IDs and only when enabled. CDI refresh errors are only logged, so invalid spec files may surface later during injection. CDI edits may be lost if callers reset OCI spec fields after injection.

## Test Signals
`device_test.go` covers privileged host devices, `privilegedWithoutHostDevices`, security-context device ownership, invalid CDI references, missing CDI devices, valid CDI injection through CRI fields and annotations, and expected injected env/device nodes.
