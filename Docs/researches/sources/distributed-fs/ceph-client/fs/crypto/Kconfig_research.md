# sources/distributed-fs/ceph-client/fs/crypto/Kconfig

Purpose: declares fscrypt build options for per-file encryption.

Important entries: `FS_ENCRYPTION` enables the framework and selects crypto, skcipher, AES/SHA helper libraries, and key support. `FS_ENCRYPTION_ALGS` pulls in default AES-CBC/CTS/XTS algorithms as a tristate for filesystems that need encryption algorithms. `FS_ENCRYPTION_INLINE_CRYPT` enables blk-crypto inline hardware support when block inline encryption is available.

Control flow: no runtime logic. Options determine whether fscrypt core, algorithm modules, block bio helpers, and inline crypto support are built.

State and persistence: no direct state; selected options affect availability of encryption policies and key setup at runtime.

Dependencies/integration: used by filesystems such as ext4, f2fs, ubifs, and CephFS. The help text notes that non-default modes such as Adiantum require explicit crypto API configuration.

Risks: enabling fscrypt without needed optimized algorithms can produce poor performance. Inline crypt depends on block-layer support and filesystem device constraints. Filesystems must select `FS_ENCRYPTION_ALGS` appropriately.

Test signals: build core only, default algorithm module combinations, inline-crypt enabled/disabled, and filesystem encryption mount/key tests across supported filesystems.
