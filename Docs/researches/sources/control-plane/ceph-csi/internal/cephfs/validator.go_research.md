# sources/control-plane/ceph-csi/internal/cephfs/validator.go

Purpose: validates CephFS controller CSI requests before backend work begins, ensuring requests match advertised capabilities and CephFS feature support.

Important APIs/types/functions: methods on `ControllerServer` are `validateCreateVolumeRequest()`, `validateDeleteVolumeRequest()`, and `validateExpandVolumeRequest()`.

Control flow: create validation checks `CREATE_DELETE_VOLUME` capability, non-empty name, non-empty capabilities, rejects block volumes, calls `util.CheckReadOnlyManyIsSupported()`, then validates content source shape. Snapshot sources require a non-empty snapshot ID and return `NotFound` for missing/empty snapshot details per CSI semantics. Volume sources require a valid volume ID. Delete and expand validate controller capability and volume ID; expand also requires `CapacityRange`.

State and persistence: stateless validation only. It reads `cs.Driver` capability state and returns gRPC status errors.

Dependencies and integration points: uses common CSI driver capability validation, common volume-ID validation, read-only support checks, CSI protobufs, and gRPC status codes. It gates CephFS controller create/delete/expand operations.

Risks: subtle CSI code semantics matter: missing source objects intentionally map to `NotFound`, while unsupported data source maps to `InvalidArgument`. The block-volume rejection is a hard CephFS limitation. Capability checks depend on driver initialization being correct.

Test signals: no direct tests in this item. Useful tests would cover all status codes, nil capability entries, unsupported content source types, block rejection, volume clone ID validation, and missing capacity range.
