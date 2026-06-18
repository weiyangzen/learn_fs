# sources/cloud-native/containerd/pkg/oci/utils_unix.go

Purpose: Unix device discovery and conversion helpers used by OCI device-related spec options.

Important APIs/types/functions: `ErrNotADevice`; package-level `osReadDir` and `deviceFromPath` variables for test injection; `HostDevices` discovers host devices under `/dev`; `getDevices(path, containerPath)` recursively walks a device path, preserving container-relative path mapping; `DeviceFromPath(path)` stats a node and returns an OCI `LinuxDevice` with type, path, major/minor, file mode, uid, and gid.

Control flow: `getDevices` stats the path; non-directory device nodes are converted directly, directories are read and recursed. `DeviceFromPath` rejects non-device modes and maps char, block, fifo, and regular device-ish modes to OCI types where supported.

State/persistence: reads host filesystem metadata only; outputs spec device entries.

Dependencies/integration: uses `os`, `path/filepath`, `syscall`, and runtime-spec. Linux options add returned devices to specs and cgroup rules.

Risks: traversing `/dev` can hit permissions, broken entries, or namespace-specific views. Device major/minor extraction is platform-specific. Test injection globals must be restored.

Test signals: `utils_unix_test.go` covers read-dir failures, user namespace behavior, conversion failures, and all-valid discovery.
