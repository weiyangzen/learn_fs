# sources/distributed-fs/ceph-client/security/keys/Kconfig

Purpose: Configures Linux key retention support and optional key types/features used by filesystems, crypto, and integrity subsystems.

Important APIs/types/functions: `KEYS` enables core keyrings. Options include request-key caching, persistent per-UID keyrings, `BIG_KEYS`, trusted keys, encrypted keys, user-decrypted encrypted-key data, Diffie-Hellman key operations, and key notifications.

Control flow: Kconfig symbols select required crypto and subsystem dependencies, such as associative arrays, tmpfs for big keys, ChaCha20-Poly1305, AES/CBC/SHA256/RNG for encrypted keys, crypto DH/KDF for DH operations, and watch queues for notifications.

State and persistence: No runtime state. Options determine which kernel key types and syscalls are built.

Dependencies and integration: Network filesystems, eCryptfs/encrypted keys, IMA/EVM, request_key(), and userspace keyctl depend on these capabilities.

Risks and test signals: Build-matrix risk is high because many files are config-gated. Test with minimal KEYS off/on, BIG_KEYS, ENCRYPTED_KEYS, TRUSTED_KEYS, DH operations, and notifications.
