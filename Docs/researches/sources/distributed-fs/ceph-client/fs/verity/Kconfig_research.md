<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/Kconfig -->
# sources/distributed-fs/ceph-client/fs/verity/Kconfig

Purpose: Defines configuration options for fs-verity and optional in-kernel builtin signature verification.

Important APIs, types, and functions: Defines `CONFIG_FS_VERITY`, depending on `PAGE_SHIFT <= 16` and selecting `CRYPTO_HASH_INFO`, `CRYPTO_LIB_SHA256`, and `CRYPTO_LIB_SHA512`. Defines `CONFIG_FS_VERITY_BUILTIN_SIGNATURES`, depending on `FS_VERITY` and selecting `SYSTEM_DATA_VERIFICATION`.

Control flow: Enabling `FS_VERITY` builds the core file-based Merkle tree verification code. Enabling builtin signatures adds keyring and PKCS#7 verification support compiled from `signature.c`.

State and persistence: No runtime state. The configuration determines whether filesystems can expose fs-verity ioctls and whether the `.fs-verity` keyring and signature sysctl exist.

Dependencies and integration points: Integrates with supported filesystems through `struct fsverity_operations`, with crypto library implementations for SHA-256/SHA-512, and with system data verification when builtin signatures are selected.

Risks and test signals: Risks include enabling on unsupported page sizes or omitting crypto dependencies. Test configs with and without builtin signatures, page-size constraints, and supported filesystems that select or call fs-verity helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/Kconfig -->
