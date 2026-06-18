# sources/cloud-native/cri-o/internal/config/device/device_linux.go

Purpose: parses configured and annotation-provided Linux device mappings into OCI runtime-spec device and cgroup resource entries.

Important APIs/types/functions: `Config` stores parsed `[]Device`; `Device` wraps `rspec.LinuxDevice` and `rspec.LinuxDeviceCgroup`; `New`, `LoadDevices`, `Devices`, and `DevicesFromAnnotation` are public. Internal helpers are `devicesFromStrings`, `parseDevice`, and `isValidDeviceMode`. `DeviceAnnotationDelim` is the comma delimiter for `io.kubernetes.cri-o.Devices`.

Control flow: `LoadDevices` parses admin-configured entries with no allow-list. `DevicesFromAnnotation` builds an allow map from configured allowed devices and parses comma-separated annotation entries. Each non-empty entry becomes `src`, `dst`, and permissions, must have an allowed source if an allow map is supplied, must map into `/dev/`, and must resolve through `devices.DeviceFromPath`. Parsed libcontainer device metadata is copied into OCI device and cgroup structures.

State and persistence behavior: parsed devices are cached in memory on `Config` so CRI-O validates configuration early and reuses normalized structures. It reads host device metadata through `DeviceFromPath`; it does not persist data.

Dependencies/integration points: depends on opencontainers runtime spec and runc/libcontainer devices. The container factory later consumes `device.Device` values to add devices and cgroup permissions to generated specs.

Risks: `parseDevice` uses colon splitting, so paths containing colons are unsupported. Destination validation only checks `/dev/` prefix, and source authorization checks only the source string. Device existence/type validation is host-dependent, making behavior vary across platforms and test environments.

Test signals: `device_test.go` covers malformed mappings, nonexistent devices, valid `/dev/null`, empty entries, annotation allow-list enforcement, and mixed invalid annotation inputs.
