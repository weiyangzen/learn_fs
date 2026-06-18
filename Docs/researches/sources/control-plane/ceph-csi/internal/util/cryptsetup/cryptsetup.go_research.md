<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cryptsetup/cryptsetup.go -->
## sources/control-plane/ceph-csi/internal/util/cryptsetup/cryptsetup.go

**Purpose:** Wraps Linux `cryptsetup` for LUKS2 volume operations and centralizes encryption option validation, recommendation scoring, LUKS status parsing, and key-slot management.

**Important APIs and types:** Constants define timeouts, PBKDF resource limits, LUKS2 header sizing, status field names, and recommendation levels. `LuksStatus` parses cipher, keysize, integrity mode/key size, and sector size. `EncryptionOptions` validates cipher/integrity allowlists and compares desired options to status. `GetRecommendation` scores cipher/key/integrity tuples. `LUKSWrapper` exposes `Format`, `Open`, `Resize`, `Close`, `Status`, `AddKey`, `RemoveKey`, `VerifyKey`, and `IsIntegrityProtected`.

**Control flow, state, and persistence:** `Format` constructs `cryptsetup luksFormat` arguments for LUKS2, optional cipher/integrity/key/sector options, reduced PBKDF resources, and custom LUKS2 metadata/keyslot sizes. `AddKey` writes current and new passphrases to temp files, handles full slots by verifying whether the new key already exists, removes the old slot if necessary, and retries recursively. `RemoveKey` tolerates inactive slots. `VerifyKey` uses read-only `open --test-passphrase`. `ParseLuksStatus` scans colon-separated fields and translates LUKS integrity names. `execCryptsetupCommand` runs the binary with optional stdin, sanitized args, stdout/stderr capture, and context-deadline handling.

**Dependencies and integration points:** Depends on `os/exec`, context, temp file helper, Kubernetes volume size constants, logging, and secret stripping. It integrates with `util/crypto.go`, block device staging, resize, and encryption key rotation.

**Risks and test signals:** `NewLUKSWrapper` accepts a context but does not create the documented `ExecutionTimeout`; callers must supply a deadline if desired. Key-slot replacement depends on stderr string matching from cryptsetup. Temp key files must be removed even on failure. Parser errors have a few typo-prone messages and one branch wraps the wrong variable for key size parse. Tests cover validation and parser logic but not live command execution or key-slot mutation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cryptsetup/cryptsetup.go -->
