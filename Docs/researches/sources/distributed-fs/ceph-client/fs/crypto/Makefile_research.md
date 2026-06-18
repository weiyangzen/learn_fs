# sources/distributed-fs/ceph-client/fs/crypto/Makefile

Purpose: defines the fscrypt composite object and conditional helpers.

Important entries: `obj-$(CONFIG_FS_ENCRYPTION) += fscrypto.o`. Core objects are `crypto.o`, `fname.o`, `hkdf.o`, `hooks.o`, `keyring.o`, `keysetup.o`, `keysetup_v1.o`, and `policy.o`. `bio.o` is included when `CONFIG_BLOCK` is enabled, and `inline_crypt.o` when `CONFIG_FS_ENCRYPTION_INLINE_CRYPT` is enabled.

Control flow: no runtime logic. Kbuild composes the framework according to block and inline-crypto availability.

State and persistence: no state.

Dependencies/integration: ties Kconfig selections to exported fscrypt APIs used by filesystems. Conditional inclusion avoids block-only helpers on non-block builds.

Risks: source-level references must stay protected by matching Kconfig guards, especially for bio and inline crypto exports. Omitting key/policy objects would break public fscrypt operations.

Test signals: compile with block disabled/enabled, inline crypto disabled/enabled, and run modpost for exported symbols consumed by filesystem modules.
