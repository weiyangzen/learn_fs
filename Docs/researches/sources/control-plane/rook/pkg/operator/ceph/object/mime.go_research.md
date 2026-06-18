# sources/control-plane/rook/pkg/operator/ceph/object/mime.go

## Purpose
`mime.go` manages the RGW `mime.types` file that Rook mounts into object-store pods so RGW can infer object content types for common file extensions.

## Important APIs, Types, and Functions
`clusterConfig.mimeTypesConfigMapName()` derives an object-store-specific ConfigMap name from the RGW instance name. `mimeTypesMountPath()` returns `/etc/ceph/rgw/mime.types`. `generateMimeTypes()` creates the ConfigMap key `mime.types` with the bundled `mimeTypes` constant unless the key already exists. `mimeTypesVolume()` and `mimeTypesVolumeMount()` build the ConfigMap volume and read-only mount at `/etc/ceph/rgw`. The `mimeTypes` constant is a large static MIME database covering application, audio, chemical, image, text, video, and other media types.

## Control Flow, State, and Persistence
On reconcile, `generateMimeTypes()` reads the ConfigMap key. If it exists, it deliberately avoids overwriting user/admin changes. If it is not found, it creates the key with the bundled content. Persistence is a Kubernetes ConfigMap owned by the object store.

## Dependencies and Integration Points
It integrates `clusterConfig`, Kubernetes ConfigMaps via `k8sutil.NewConfigMapKVStore`, owner references, RGW pod volume generation, and object-store deployment code that mounts the file.

## Risks and Test Signals
Risks include stale MIME definitions because existing ConfigMaps are never updated, user edits persisting across operator upgrades, large inline data increasing source size, mount-path assumptions, and ConfigMap ownership/deletion coupling. Useful tests would cover create, no-overwrite, ConfigMap get errors, volume naming, mount path, read-only mount, and deployment integration.
