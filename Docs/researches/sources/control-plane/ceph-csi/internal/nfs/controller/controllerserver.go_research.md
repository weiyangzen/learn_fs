# sources/control-plane/ceph-csi/internal/nfs/controller/controllerserver.go

## Purpose
`controllerserver.go` implements the NFS CSI controller by delegating storage operations to CephFS and adding NFS export creation, deletion, and mutable server metadata.

## Important APIs, Types, And Functions
`Server` embeds `csi.UnimplementedControllerServer` and stores a CephFS backend controller. `NewControllerServer()` initializes global CephFS volume/snapshot journals and the backend controller. Controller methods include capability validation, `CreateVolume`, `DeleteVolume`, publish/unpublish, expand, snapshot create/delete, and `ControllerModifyVolume`.

## Control Flow And State
`CreateVolume()` forces `backingSnapshot=false`, creates the CephFS backend volume, builds admin credentials, opens an `NFSVolume`, connects to Ceph, creates an NFS export, adds `share` to the volume context, and optionally applies mutable parameters. `DeleteVolume()` validates the ID, connects an `NFSVolume`, deletes the export while tolerating not-found, then delegates backend volume deletion. Most other CSI methods delegate directly to CephFS or return no-op success.

## State And Persistence Behavior
Persistent state includes the CephFS backing volume, NFS-Ganesha export, and journal attributes such as NFS cluster/server metadata. The controller updates global `store.VolJournal` and `store.SnapJournal` for CephFS RADOS namespace.

## Dependencies And Integration Points
The server integrates CSI protobufs, CephFS controller, CephFS store/journal utilities, NFS type helpers, Ceph-CSI credentials, and gRPC status codes. It bridges CephFS subvolume creation with NFS export publication.

## Risks And Edge Cases
`CreateVolume()` mutates `req.Parameters` directly and assumes the map is non-nil. If export creation succeeds but later `ControllerModifyVolume()` fails, cleanup is not performed in this method. Delete maps most NFS export errors to `InvalidArgument`, which may obscure backend or transient failures. Global journal assignment can affect tests or multiple driver instances.

## Test Signals
No controller tests are included in this subset. Desired coverage includes nil parameter maps, backend create cleanup, export already-exists/not-found behavior, mutable server update failure after export creation, and delegation status mapping.
