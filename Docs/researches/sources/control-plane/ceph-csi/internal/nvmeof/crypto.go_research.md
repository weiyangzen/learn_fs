# sources/control-plane/ceph-csi/internal/nvmeof/crypto.go

Purpose: Defines the KMS-backed abstraction for storing and retrieving NVMe-oF security keys, especially DH-CHAP secrets.

Important APIs/types/functions: Exports sentinel errors `ErrDEKStoreNotSet`, `ErrDEKStoreNeeded`, `ErrKeyNotFound`, owner constant `NVMeOFSecurityOwner`, interface `SecurityKeyManager`, `InitSecurityKeyManager`, and concrete `securityKeyManager` methods `StoreKey`, `GetKey`, `RemoveKey`, `SetDEKStore`, `GetID`, and `Destroy`.

Control flow: Initialization chooses `"metadata"` KMS when no ID is supplied, obtains a KMS through `kms.GetKMS`, then calls `newSecurityKeyManager`. Integrated KMS backends are expected to implement `kms.DEKStore` directly. Non-integrated backends return a usable manager plus `ErrDEKStoreNeeded`, requiring the caller to attach a DEKStore before key operations. Store encrypts plaintext via KMS then writes encrypted data to the DEKStore. Get fetches encrypted data then decrypts it. Remove delegates to the DEKStore.

State and persistence behavior: The manager holds a KMS instance and optional DEKStore. Persistence location depends on backend: integrated KMS, external storage, or caller-provided RBD metadata store. No in-memory key cache is kept.

Dependencies and integration points: Depends on Ceph-CSI `internal/kms` interfaces. Used by controller and node security helpers plus DH-CHAP key creation functions.

Risks: Error normalization assumes DEKStore implementations return `ErrKeyNotFound`; generic KMS stores may not. `Destroy` assumes `skm.kms` is non-nil. Callers must correctly handle the non-nil manager plus `ErrDEKStoreNeeded` pattern or all key operations fail with `ErrDEKStoreNotSet`.

Test signals: No direct tests. Behavior is indirectly exercised only through higher-level security paths if integration tests cover KMS.
