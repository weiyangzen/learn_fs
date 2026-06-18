<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/getsecret_test.go -->
## sources/control-plane/ceph-csi/internal/util/getsecret_test.go

**Purpose:** Validates that KMS test providers used by Ceph-CSI can return secrets needed by fscrypt-style integrations when applicable.

**Important APIs and functions:** `TestGetPassphraseFromKMS` iterates KMS test providers, creates dummy providers, calls `NewVolumeEncryption`, skips unsupported `GetSecret` paths when `ErrDEKStoreNeeded` and `ErrGetSecretUnsupported` apply, skips integrated DEK stores, and verifies metadata-style KMS returns a non-empty secret.

**Control flow, state, and persistence:** Pure test provider workflow with no real external KMS or filesystem state. It uses parallel execution and provider-specific dummy instances.

**Dependencies and integration points:** Depends on internal KMS test provider registry and `VolumeEncryption`. It connects KMS provider behavior to file encryption requirements.

**Risks and test signals:** Good signal for provider contract compatibility. It does not assert exact secret content, real KMS configuration, fscrypt unlock behavior, or `VolumeEncryption` DEK store operations.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/getsecret_test.go -->
