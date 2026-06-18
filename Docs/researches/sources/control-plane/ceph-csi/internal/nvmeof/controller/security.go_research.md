# sources/control-plane/ceph-csi/internal/nvmeof/controller/security.go

Purpose: Supplies controller-side DH-CHAP key setup and cleanup for NVMe-oF host publication. It bridges CSI secrets, KMS-backed key management, optional RBD metadata DEK storage, and gateway `AddHost` key parameters.

Important APIs/types/functions: `getOrInitSecurityKeys` lazily initializes/caches `nvmeof.SecurityKeyManager`. `setupDHCHAPKeys` returns `nvmeof.DHCHAPKeys` for unidirectional or bidirectional authentication. `cleanupDHCHAPKeys` removes stored host/subsystem keys after unpublish.

Control flow: Disabled modes return empty keys. Enabled modes read `authenticationKMSID` from volume context, initialize a KMS manager, and if `ErrDEKStoreNeeded` is returned, open the RBD volume and attach an `RBDVolumeDEKStore`. Host keys are always retrieved or created; subsystem keys are included only for bidirectional mode. Cleanup follows the same KMS/DEK setup path and attempts both removals, logging but not returning individual removal failures.

State and persistence behavior: Integrated-storage KMS managers may be cached on the controller. Metadata KMS managers are not cached because each call needs a fresh volume-specific DEKStore. Keys are persisted through the configured KMS/DEKStore; for metadata KMS that means RBD image metadata.

Dependencies and integration points: Depends on `internal/nvmeof` crypto/DH-CHAP helpers, RBD manager lookup by volume ID, CSI publish request secrets and volume context, and controller `backendServer.Driver.GetInstanceID()`.

Risks: The cache key is not scoped by KMS ID or secret set; once a cacheable manager exists, later volumes with different KMS IDs would reuse it. Metadata DEKStore removal currently delegates to a no-op store implementation, so cleanup may not actually delete metadata-backed keys. Comments mark metadata KMS as test-oriented, but code defaults to it when DH-CHAP lacks an explicit KMS.

Test signals: No direct tests in this file. DH-CHAP helper tests are absent, so KMS error handling, cache semantics, and RBD metadata fallback rely on integration coverage.
