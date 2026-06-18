# sources/control-plane/rook/pkg/daemon/ceph/client/image.go

Purpose: manages RBD image and snapshot listing/deletion/status operations for pools and RADOS namespaces.

Important APIs/types: `CephBlockImage` and `CephBlockImageSnapshot` model RBD JSON. `ListImagesInPool()` delegates to `ListImagesInRadosNamespace()`. Other APIs include `ListSnapshotsInRadosNamespace()`, `DeleteSnapshotInRadosNamespace()`, `MoveImageToTrashInRadosNamespace()`, `DeleteImageFromTrashInRadosNamespace()`, `DeleteImageInPool()`, `DeleteImageInRadosNamespace()`, spec helpers, `RBDStatus.GetWatchers()`, and `GetRBDImageStatus()`.

Control flow and state: image list uses `rbd ls -l <pool> [--namespace ns]` with JSON output. Because librados debug logging can prefix output, it extracts the first line beginning with `[` before unmarshalling. Snapshot listing/deletion and image deletion use RBD commands with optional namespace. Trash removal uses `ceph rbd task add trash remove <pool[/namespace]/imageID>`, not the RBD CLI directly. Status returns watcher addresses from `rbd status`.

Dependencies and integration: used by pool cleanup, CSI/image cleanup, and block mirroring operations. It depends on `regexp`, `encoding/json`, shared RBD/Ceph command wrappers, and namespace conventions. Risks include the regex capturing the first bracketed line rather than necessarily the JSON payload if debug logs contain bracketed text, namespace path formatting inconsistencies between commands, and destructive deletion operations. Tests cover list parsing with and without debug logs and watcher extraction; many mutation APIs are untested.
