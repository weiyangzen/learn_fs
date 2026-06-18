## sources/control-plane/ceph-csi/internal/cephfs/core/filesystem.go

Purpose: Small abstraction over CephFS filesystem discovery APIs used by volume and group snapshot option construction.

Important types/functions: `FileSystem` interface, `fileSystem` implementation, `NewFileSystem`, `GetFscID`, `GetMetadataPool`, and `GetFsName`.

Control flow: Each method obtains `FSAdmin` from the cluster connection, enumerates volumes or file systems, scans for the requested name or ID, and returns the matching filesystem ID, metadata pool, or name. Missing entries map to Ceph CSI `ErrVolumeNotFound` or `util.ErrPoolNotFound` wrapping.

State and persistence: Reads Ceph cluster filesystem metadata only; no writes or local state. Callers use returned FscID and metadata pool to generate CSI IDs and journal locations.

Dependencies and risks: Depends on go-ceph FSAdmin and internal logging/errors. Linear scans are simple but assume filesystem names/IDs are available and stable. Tests in this subset do not cover this file directly; integration tests should validate behavior with missing filesystem, missing metadata pool, and multiple filesystems.
