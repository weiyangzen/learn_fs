# sources/control-plane/ceph-csi/internal/rbd/mirror.go

## Purpose
Wraps librbd image mirroring operations and status parsing behind RBD `types.Mirror`, `types.GlobalStatus`, `types.SiteStatus`, and `types.SyncInfo` interfaces used by replication and controller cleanup flows.

## Important APIs, Types, And Functions
`HandleParentImageExistence` validates or flattens parent images before enabling mirroring. `rbdMirror` wraps `rbdImage`; `ToMirror` constructs it. Mirror operations include `EnableMirroring`, `DisableMirroring`, `GetMirroringInfo`, `Promote`, `Demote`, `Resync`, and `GetGlobalMirroringStatus`. Status wrappers include `ImageStatus`, `GlobalMirrorStatus`, `SiteMirrorImageStatus`, and `syncInfo`; `newSyncInfo` parses librbd status descriptions.

## Control Flow
Each mirror operation opens the image, defers close, invokes the corresponding librbd method, and wraps errors with image context. `HandleParentImageExistence` optionally force-flattens, rejects parents in trash, and requires existing parents to have mirroring enabled. `Resync` issues `MirrorResync`, then sleeps with exponential backoff while checking global status until the local site reports syncing or returns `ErrUnavailable` for retry. `newSyncInfo` splits a status description at the first comma, unmarshals JSON details, and requires a nonzero local snapshot timestamp.

## State And Persistence
Mirroring operations mutate persistent RBD mirror state: enabled/disabled flags, primary/secondary role, resync state, and image flattening. Status wrappers are read-only views over librbd structs. No journal state is written here.

## Dependencies And Integration Points
Depends on go-ceph/librbd, RBD image helpers, replication `types` interfaces, RBD error sentinels, and logging. `controllerserver.go` uses mirror status during delete to avoid deleting healthy secondary images, while CSI-Addons replication servers use these methods for failover/failback workflows.

## Risks And Test Signals
Risks include force-flatten side effects, parent mirroring precondition accuracy, open/close resource handling, parsing unstructured status descriptions, and resync timing/backoff behavior. `mirror_test.go` covers `newSyncInfo` parsing but not live librbd mirror operations.
