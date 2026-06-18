# sources/cloud-native/moby/daemon/pkg/oci/devices_linux.go

## Purpose
This file converts Linux host device paths into OCI device entries and device-cgroup permissions for container specs.

## Important APIs, Types, And Functions
`deviceCgroup` builds a `specs.LinuxDeviceCgroup` from a device and permission string. `DevicesFromPath(pathOnHost, pathInContainer, cgroupPermissions)` resolves devices, symlinks, and directories into `[]specs.LinuxDevice` and matching cgroup rules.

## Control Flow
`DevicesFromPath` resolves symlinks when possible, calls containerd `DeviceFromPath`, and on success rewrites the device path to the container path. If the path is not a device but is a directory, it walks the directory recursively, ignores non-device entries, converts found devices, and maps child paths from host directory prefix to container directory prefix. If no devices are found, it returns a contextual error.

## State, Persistence, And Dependencies
There is no persistent state. The function reads filesystem metadata and device nodes. Dependencies include containerd OCI device detection, runtime-spec types, `os`, `filepath`, `strings`, `errors`, and `fmt`.

## Integration Points
`oci_linux.go` calls this for `HostConfig.Devices` in privileged and non-privileged containers, feeding results into spec devices and cgroup permissions.

## Risks And Edge Cases
Directory walking ignores errors and non-device entries, which is permissive but can hide inaccessible devices. Symlink resolution failure falls back to the original path. String prefix replacement maps host child paths to container paths and assumes the walked path is under the resolved host directory.

## Test Signals
No direct tests in this subset; device mapping behavior is covered by OCI/device integration tests elsewhere.
