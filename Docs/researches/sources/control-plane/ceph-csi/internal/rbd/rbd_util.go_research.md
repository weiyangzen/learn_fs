<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_util.go -->
# sources/control-plane/ceph-csi/internal/rbd/rbd_util.go

## Purpose
`rbd_util.go` defines the core RBD domain model and most shared operations for RBD images, volumes, snapshots, feature validation, cluster connections, image creation/deletion, clone flattening, ID decoding, metadata stash management, resizing, QoS dispatch, log strategy, and utility interfaces.

## Important APIs, Types, And Functions
Primary types are `rbdImage`, `rbdVolume`, `rbdSnapshot`, `imageFeature`, `migrationVolID`, `rbdImageMetadataStash`, and `snapAndChildrenInfo`. Important constants define mounters, migration keys, metadata keys, stash filename, and krbd support file paths.

Major functions include `GetClientAddressKey`, `GetUserIDMappingKey`, `prepareKrbdFeatureAttrs`, `GetKrbdSupportedFeatures`, `HexStringToInteger`, `isKrbdFeatureSupported`, `Connect`, `Destroy`, `String`, `createImage`, `openIoctx`, `open`, `openReadOnly`, `isInUse`, `Delete`, `trashRemoveImage`, `DeleteTempImage`, `getCloneDepth`, `flattenRbdImage`, `checkImageChainHasFeature`, `GenVolFromVolID`, `generateVolumeFromVolumeID`, `generateVolumeFromMapping`, `genVolFromVolumeOptions`, `validateImageFeatures`, `genSnapFromSnapID`, `createSnapshot`, `deleteSnapshot`, `cloneRbdImageFromSnapshot`, `constructImageOptions`, `getImageInfo`, `stashRBDImageMetadata`, `lookupRBDImageMetadataStash`, `updateRBDImageMetadataStash`, `cleanupRBDImageMetadataStash`, `resize`, metadata getters/setters, `DeepCopy`, `DisableDeepFlatten`, `listSnapAndChildren`, `PrepareVolumeForSnapshot`, `getUsedBytes`, `UsesNBDMounter`, and `modifyVolumeAttributes`.

## Control Flow
Volume generation decomposes CSI IDs, resolves monitors, pools, namespace, journal attributes, encryption config, image info, data pool, and optional cluster/pool mappings. Image creation builds `librbd.ImageOptions`, creates the RBD image, and prepares encryption metadata. Deletion obtains the image ID, removes encryption DEKs, trashes the image, then queues or performs trash removal. Clone/snapshot helpers open IO contexts, set clone options, clean up failed clones, and repair image IDs. Metadata stash helpers write and read node-local JSON used by node unstage/expand. `modifyVolumeAttributes` selects cgroup or NBD QoS handlers and clears all handlers when no QoS parameters are supplied.

## State And Persistence
Persistent state includes RBD images and snapshots, RBD trash, RBD image metadata, Ceph-CSI OMAP journal attributes, encryption DEKs, local `image-meta.json`, and optional NBD client log files. Runtime state includes cluster connections, RADOS IO contexts, cached image fields, encryption helper objects, and QoS maps. Several methods lazily open and cache IO contexts or connections and require `Destroy` for cleanup.

## Dependencies And Integration Points
This file depends heavily on go-ceph `rados`, `rbd`, and `rbd/admin`, CSI types, Kubernetes volume helpers, Ceph-CSI util packages, kernel feature helpers, encryption helpers, journal code, and QoS handlers. It is used by controller, node, snapshot, replication, migration, and manager code.

## Risks
The file is a broad shared surface, so small behavior changes have high blast radius. IO context lifecycle has FIXME comments in clone-chain traversal. Image deletion relies on Ceph manager task support with fallback and can leave trash entries if both paths fail. Feature validation is string-driven and mounter-dependent. Local stash cleanup returns errors on missing files. `modifyVolumeAttributes` clears both QoS strategies when no QoS params are supplied, which must stay aligned with controller validation. Metadata writes and OMAP updates are not atomic with image changes.

## Test Signals
`rbd_util_test.go` covers snapshot feature detection, image feature validation and dependencies, client log filename formatting, log strategy actions, krbd feature bit checks, image feature empty validation, and retryable volume-generation errors. It does not cover real RADOS/RBD operations, OMAP interactions, stash JSON behavior, deletion fallback, clone flattening, or QoS handler dispatch.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_util.go -->
