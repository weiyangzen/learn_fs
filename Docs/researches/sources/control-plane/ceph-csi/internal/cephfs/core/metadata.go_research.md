## sources/control-plane/ceph-csi/internal/cephfs/core/metadata.go

Purpose: Provides CephFS subvolume metadata helpers for Kubernetes metadata, cluster name, node client address, user ID mapping, and service-account restrictions.

Important constants/functions: `clusterNameKey`, `clientAddressKey`, `userIdMappingKey`, exported `ServiceAccountKey`, `ErrSubVolMetadataNotSupported`, `GetClientAddressKey`, `GetUserIDMappingKey`, `SetAllMetadata`, `UnsetAllMetadata`, and `ListMetadata`.

Control flow: Per-cluster metadata support is cached in `clusterAdditionalInfo`. `setMetadata`, `removeMetadata`, and `listMetadata` call FSAdmin metadata APIs and convert `NotImplementedError` into a soft unsupported state. Bulk set/unset/list methods ignore unsupported clusters but wrap other errors with key/value context.

State and persistence: Metadata is stored on CephFS subvolumes. Keys starting with `.` are intended to avoid copying to mirrored subvolumes. Global in-memory support cache influences later calls per cluster ID.

Dependencies and risks: Depends on go-ceph cephfs/admin metadata APIs and libcephfs not-exist errors. The global cache is protected during initialization but subsequent state mutation is not separately locked, so concurrent unsupported detection may race. Tests are not present here; integration should cover unsupported Ceph versions and metadata cleanup on unpublish/delete.
