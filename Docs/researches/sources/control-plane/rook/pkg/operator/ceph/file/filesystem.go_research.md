# sources/control-plane/rook/pkg/operator/ceph/file/filesystem.go

## Purpose
This file contains the CephFS creation, update, deletion, validation, and pool-naming logic used by the `CephFilesystem` reconciler. It bridges the CR spec to Ceph pools, Ceph filesystem commands, MDS daemons, standby replay settings, and the default CSI subvolume group.

## Important APIs, Types, and Functions
`Filesystem` stores filesystem name and namespace. `createFilesystem` starts the MDS cluster, creates or updates CephFS/pools when data pools are specified, configures standby replay and active MDS ranks, and creates the default `csi` subvolume group. `deleteFilesystem` removes MDS CephX/config objects, downs the filesystem, and optionally removes the CephFS and pools. `validateFilesystem`, `hasDuplicatePoolNames`, `createOrUpdatePools`, `updateFilesystem`, `doFilesystemCreate`, `downFilesystem`, `generateDataPoolNames`, `GenerateMetaDataPoolName`, and `generateMetaDataPoolName` implement validation and Ceph object naming.

## Control Flow, State, and Persistence
Creation starts MDS deployments first through `mds.NewCluster(...).Start()`. If `Spec.DataPools` is non-empty, it creates or updates Ceph pools and the Ceph filesystem. Existing filesystems are updated by setting `max_mds`, creating/updating pools, and adding data pools to the filesystem. New filesystems check existing pool names to avoid recreating pools, create metadata and data pools with the `cephfs` application, enable `allow_ec_overwrites` for erasure-coded data pools, and call `ceph fs new`. Afterward, standby replay, active rank count, and the `csi` subvolume group are reconciled.

Deletion builds the same MDS cluster object, deletes MDS daemon config and CephX objects for twice the active count, attempts to fail/down the filesystem, and permanently removes it only when Rook-created data pools exist and `PreserveFilesystemOnDelete` is false. Pool names are persisted in Ceph using either generated names (`<fs>-metadata`, `<fs>-dataN`, `<fs>-<named>`) or raw spec names when `PreservePoolNames` is true.

## Dependencies and Integration Points
The file integrates with `mds` daemon management, `cephclient` filesystem/pool/subvolume commands, pool validation, cluster specs, owner references, Rook logging, and Kubernetes resource sizing through the MDS package. CSI depends on the automatically created `csi` subvolume group for CephFS PVC provisioning.

## Risks
Starting MDS before creating a new filesystem means deployment success can precede CephFS creation failure. `SetNumMDSRanks` failures in update paths are logged and tolerated, potentially leaving lower availability than requested. Deletion logs and continues after down/remove failures, which may leave Ceph-side filesystem or pool state behind while the CR finalizer is removed by the caller. Duplicate pool-name validation ignores unnamed generated names that could still collide through spec changes.

## Test Signals
Signals include validation failures for missing required fields, duplicate named-pool detection, expected generated/preserved pool names, creation of metadata/data pools, adding new pools to existing filesystems, MDS deployment creation/update, successful no-pool external-filesystem MDS startup, EC overwrite setting attempts, standby replay and active-rank commands, and cleanup behavior on deletion.
