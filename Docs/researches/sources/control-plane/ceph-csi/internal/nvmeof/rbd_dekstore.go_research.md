# sources/control-plane/ceph-csi/internal/nvmeof/rbd_dekstore.go

Purpose: Implements `kms.DEKStore` over RBD image metadata for NVMe-oF DH-CHAP keys, mainly used by metadata KMS flows.

Important APIs/types/functions: `rbdVolumeDEKStore`, `NewRBDVolumeDEKStore`, `StoreDEK`, `FetchDEK`, and `RemoveDEK`.

Control flow: Store prefixes the key ID with `nvmeof.csi.ceph.com/` and writes encrypted data through `SetMetadata`. Fetch reads the same key and maps librbd not-found to `ErrKeyNotFound`. Remove is currently a no-op.

State and persistence behavior: Encrypted keys are persisted as RBD image metadata. Because `RemoveDEK` does nothing, metadata-backed keys remain until volume deletion or future explicit metadata removal support.

Dependencies and integration points: Depends on RBD volume interface from `internal/rbd/types`, `go-ceph/rbd` not-found errors, and `internal/kms` DEKStore contract. Used by controller and node security helpers when `InitSecurityKeyManager` returns `ErrDEKStoreNeeded`.

Risks: Key cleanup is incomplete by design. Stored metadata keys do not use the `.rbd.` non-copy prefix used for NVMe-oF volume metadata, so clone/snapshot propagation behavior should be reviewed if DH-CHAP metadata must not be copied. Error matching uses `librbd.ErrNotFound`, while other RBD paths use both NotFound and NotExist variants.

Test signals: No direct tests for store/fetch/remove behavior or metadata key naming.
