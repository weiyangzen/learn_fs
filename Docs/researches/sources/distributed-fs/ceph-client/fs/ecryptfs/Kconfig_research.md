# sources/distributed-fs/ceph-client/fs/ecryptfs/Kconfig

## Purpose
This Kconfig file defines build-time configuration for the eCryptfs filesystem layer and optional userspace key wrap/unwrap messaging support.

## Important APIs, Types, And Functions
It defines `CONFIG_ECRYPT_FS` as a tristate depending on `KEYS`, `CRYPTO`, and either `ENCRYPTED_KEYS` enabled or absent. It selects ECB, CBC, MD5 library crypto support. It also defines boolean `CONFIG_ECRYPT_FS_MESSAGING`, dependent on `ECRYPT_FS`.

## Control Flow
At kernel configuration time, enabling `ECRYPT_FS` builds the eCryptfs filesystem built-in or as module `ecryptfs`. Enabling messaging adds `/dev/ecryptfs` support for the ecryptfs daemon to wrap or unwrap file encryption keys via userspace backends.

## State And Persistence
Kconfig symbols persist in the kernel build configuration, not at runtime. They control which object files and runtime interfaces exist.

## Dependencies And Integration Points
Integrated with the crypto subsystem, key management, encrypted keys, documentation, and the eCryptfs Makefile. `ECRYPT_FS_MESSAGING` controls compilation of `messaging.o` and `miscdev.o`.

## Risks
Selecting legacy crypto modes such as ECB/CBC and MD5 reflects eCryptfs format needs; disabling dependencies removes the filesystem option. Messaging support creates a userspace device surface and depends on an external daemon.

## Test Signals
Configuration tests should cover built-in, module, disabled, and messaging-enabled builds. Runtime smoke tests should mount eCryptfs and, with messaging enabled, verify `/dev/ecryptfs` userspace interaction.
