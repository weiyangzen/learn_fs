<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/fscrypt/fscrypt.go -->
## sources/control-plane/ceph-csi/internal/util/fscrypt/fscrypt.go

**Purpose:** Implements Ceph-CSI file-encryption support using the `google/fscrypt` library, KMS-backed keys, and filesystem/kernel checks.

**Important APIs and functions:** Constants define hashing target, protector prefix, encrypted subdir name, and passphrase size. `AppendEncyptedSubdirectory`, `getPassphrase`, `createKeyFuncFromVolumeEncryption`, `fsyncEncryptedDirectory`, `unlockExisting`, `initializeAndUnlock`, `getInodeEncryptedAttribute`, `IsDirectoryUnlocked`, `getBestPolicyVersion`, `InitializeNode`, and `Unlock` make up the flow.

**Control flow, state, and persistence:** `InitializeNode` writes `/etc/fscrypt.conf` with policy v2 on supported kernels, tolerating existing config. `Unlock` obtains a KMS key function, refreshes mount info, creates an fscrypt context, verifies support, sets up `.fscrypt` metadata, detects whether kernel policy and metadata already exist, chooses custom passphrase or raw key source based on KMS DEK-store mode, stores a new passphrase for integrated stores when initializing, creates/provisions/protects a policy for new encrypted directories, or unlocks existing ones. It fsyncs the encrypted directory after applying a policy and locks policies after use.

**Dependencies and integration points:** Depends on cgo `linux/fs.h`, fscrypt actions/crypto/filesystem/metadata packages, xattrs, unix ioctl, kernel version helpers, KMS, volume encryption, and logging. It integrates with node staging for file-encrypted volumes and `getsecret_test.go` KMS expectations.

**Risks and test signals:** The function handles sensitive partially initialized states: metadata without kernel policy or vice versa is rejected. Unlock falls back to an older null-padded passphrase length for backward compatibility. `initializeAndUnlock` calls `protector.Revert()` after create failure even if protector may be nil depending on library behavior. The misspelled `AppendEncyptedSubdirectory` is API-visible. There are no direct tests in this file; coverage is mostly KMS secret tests and integration environments with fscrypt-capable filesystems.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/fscrypt/fscrypt.go -->
