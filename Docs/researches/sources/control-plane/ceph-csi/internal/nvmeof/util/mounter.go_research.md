# sources/control-plane/ceph-csi/internal/nvmeof/util/mounter.go

Purpose: Discovers NVMe device paths from mount points and builds an initial set of mounted NVMe-oF CSI staging devices.

Important APIs/types/functions: `FindmntResult`, `FindmntFilesystem`, `FindmntSource`, `FindmntSource.UnmarshalText`, `parseNVMEDeviceFromRawSource`, `GetDeviceFromMountpoint`, and `GetAllNVMeMountedDevices`.

Control flow: `findmnt -J` output is decoded into structs. Source parsing handles direct `/dev/nvme...` filesystem mounts and block-volume `devtmpfs[/nvmeXnY]` syntax. `GetDeviceFromMountpoint` queries one mountpoint and returns the parsed device or empty. `GetAllNVMeMountedDevices` lists all mounts and filters to Ceph NVMe-oF CSI staging paths for filesystem and block volumes.

State and persistence behavior: Reads live mount table through `findmnt`; no persistent writes. Results seed/update the node server mount cache.

Dependencies and integration points: Depends on `util.ExecCommandWithTimeout`, `findmnt`, JSON output stability, and Ceph-CSI logging. Directly supports node unstage disconnect safety.

Risks: Path filtering is string-based and Kubernetes path layout dependent. Device parser only recognizes `nvme\d+n\d+` and direct `/dev/nvme` prefixes, not partition suffixes or alternate symlink paths. Errors from `findmnt` are surfaced, which can block node server startup when cache initialization fails.

Test signals: `mounter_test.go` covers raw source parsing. No tests mock full `findmnt -J` output for `GetAllNVMeMountedDevices`.
