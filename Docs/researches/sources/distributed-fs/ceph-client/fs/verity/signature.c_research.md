<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/signature.c -->
# sources/distributed-fs/ceph-client/fs/verity/signature.c

Purpose: Implements optional fs-verity builtin signature verification against the kernel `.fs-verity` keyring.

Important APIs, types, and functions: Defines global `fsverity_require_signatures`, static `fsverity_keyring`, `fsverity_verify_signature()`, and `fsverity_init_signature()`.

Control flow: If no signature is present, verification succeeds unless `require_signatures` is set, in which case the file is rejected. If a signature is present but the keyring is empty, it returns `-ENOKEY` without invoking the PKCS#7 parser. Otherwise it builds a `fsverity_formatted_digest` containing magic, algorithm id, digest size, and cached file digest, calls `verify_pkcs7_signature()` against the fs-verity keyring, logs specific failures, and exposes valid signatures to LSMs with `security_inode_setintegrity()`.

State and persistence: Maintains the `.fs-verity` keyring and runtime sysctl-backed `fsverity_require_signatures` policy. It does not persist signatures; signatures are stored in filesystem verity descriptors.

Dependencies and integration points: Depends on keyrings, PKCS#7/system data verification, credentials, LSM integrity hooks, hash algorithm ids, and `fsverity_info` file digests. Initialized from `init.c` when builtin signatures are configured.

Risks and test signals: Risks include trusting empty keyrings, malformed PKCS#7 attack surface, algorithm-id mismatch, LSM notification failures, and policy surprises when signatures are verified even if not required. Test unsigned files with policy off/on, signed files with empty keyring, wrong certificate, malformed signatures, valid signatures, keyring restriction, and LSM integrity hook behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/signature.c -->
