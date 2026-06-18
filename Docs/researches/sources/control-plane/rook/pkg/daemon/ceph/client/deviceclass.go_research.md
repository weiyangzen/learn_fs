# sources/control-plane/rook/pkg/daemon/ceph/client/deviceclass.go

Purpose: wraps Ceph commands for discovering CRUSH device classes and the OSD IDs assigned to a class.

Important APIs: `GetDeviceClasses()` runs `ceph osd crush class ls` and returns `[]string`. `GetDeviceClassOSDs()` runs `ceph osd crush class ls-osd <class>` and returns `[]int`.

Control flow and state: both functions are read-only cluster queries through `NewCephCommand()`. They request JSON output by default and unmarshal directly into simple slices. No local state or persistence is involved.

Dependencies and integration: used by OSD and pool placement reconciliation where device classes such as `ssd` or `hdd` determine CRUSH rules and pool placement. It depends on `encoding/json`, command execution, and `ClusterInfo`. Risks include Ceph command schema changes or command errors due to unsupported device-class operations in older clusters. `GetDeviceClassOSDs()` has explicit test coverage for non-empty and empty class membership; `GetDeviceClasses()` lacks a direct unit test.
