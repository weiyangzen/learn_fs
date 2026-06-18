# sources/control-plane/ceph-csi/internal/csi-addons/rbd/volumegroup.go

Purpose: CSI-addons RBD volume group controller implementation for create, delete, membership modification, and get operations.

Important APIs/types/functions: `VolumeGroupServer` stores driver instance and implements `NewVolumeGroupServer()`, `RegisterService()`, `CreateVolumeGroup()`, `DeleteVolumeGroup()`, `ModifyVolumeGroupMembership()`, and `ControllerGetVolumeGroup()`.

Control flow: create resolves all requested volume IDs, reuses an existing group from the first volume if present, validates all volumes are in the same group, creates or resolves the backend group, verifies existing group membership, optionally flattens parent images using `getFlattenMode()`, adds volumes when the group is empty, converts the group to CSI form, and copies request parameters into the volume group context. Delete resolves the group, treats not-found as idempotent success, refuses non-empty groups with `FailedPrecondition`, and deletes empty groups. Modify resolves the group, lists current volumes, computes remove/add sets by CSI ID, removes absent volumes, resolves and flattens new volumes, adds them, and returns CSI group state. Get resolves and converts the group, returning `NotFound` for missing groups.

State and persistence: mutates RBD volume group membership and group existence. It may flatten parent images before adding to groups. No local locks are present in this file, so concurrency control depends on backend idempotency and higher layers.

Dependencies and integration points: uses CSI-addons volumegroup protobufs, RBD manager/types/errors, shared replication helper `getFlattenMode()`, shared `getGRPCError()`, and gRPC status codes. Identity advertises the related volume group capabilities.

Risks: create only adds volumes when the group currently lists zero volumes; if a partially populated group exists, mismatch is detected for reused groups but new groups with unexpected existing members depend on backend behavior. No explicit per-group lock may allow concurrent membership races. Delete refuses non-empty groups because advertised capability says volume group deletion must not delete member volumes. Parameter copying into group context can expose backend parameters to callers.

Test signals: no direct tests in this item. Useful coverage would mock RBD manager/group/volume interfaces for idempotency, partial membership mismatch, delete non-empty behavior, modify diffing, flatten failures, and get missing-group mapping.
