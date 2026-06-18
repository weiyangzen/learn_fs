<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/crypto.go -->
## sources/control-plane/ceph-csi/internal/util/crypto.go

**Purpose:** Provides volume encryption orchestration for Ceph-CSI, including KMS-backed passphrase storage, passphrase generation, LUKS device mapping helpers, and calls into the cryptsetup wrapper.

**Important APIs and types:** `VolumeEncryption` stores a KMS, optional DEK store, ID, and cipher options. Important functions include `FetchEncryptionKMSID`, `FetchEncryptionType`, `NewVolumeEncryption`, `SetDEKStore`, `RemoveDEK`, `StoreCryptoPassphrase`, `StoreNewCryptoPassphrase`, `GetCryptoPassphrase`, `generateNewEncryptionPassphrase`, `VolumeMapper`, `EncryptVolume`, `OpenEncryptedVolume`, `ResizeEncryptedVolume`, `CloseEncryptedVolume`, `IsDeviceOpen`, and `DeviceEncryptionStatus`.

**Control flow, state, and persistence:** KMS flow chooses a default KMS ID when encryption is true and ID is empty, configures integrated DEK stores automatically, or returns `ErrDEKStoreNeeded` for metadata-style stores. Passphrases are generated from `crypto/rand`, base64 URL encoded, encrypted through KMS, and stored in the DEK store. LUKS flow delegates to a package-level wrapper, logs stderr/errors, blocks resize when integrity mode is detected, and parses `cryptsetup status` output for mapper-to-device resolution.

**Dependencies and integration points:** Depends on internal KMS interfaces, `cryptsetup`, logging, and package crypto enum parsing. It integrates with RBD/CephFS volume staging, encryption key rotation, and KMS provider plugins.

**Risks and test signals:** `StoreCryptoPassphrase` and `GetCryptoPassphrase` assume `dekStore` is set; callers must handle `ErrDEKStoreNeeded`. `DeviceEncryptionStatus` treats cryptsetup status errors as non-LUKS and can hide real command failures. Integrity-protected volumes cannot be resized. Tests cover passphrase length, a default SecretsKMS workflow, and encryption type parsing; LUKS command behavior needs wrapper/integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/crypto.go -->
