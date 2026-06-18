<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/crypto/Makefile

## Purpose
Kbuild manifest for ARM architecture-specific CryptoAPI modules.

## Important APIs/types/functions
- `aes-arm-bs-y := aes-neonbs-core.o aes-neonbs-glue.o`
- `aes-arm-ce-y := aes-ce-core.o aes-ce-glue.o`
- `ghash-arm-ce-y := ghash-ce-core.o ghash-ce-glue.o`
- Module objects gated by `CONFIG_CRYPTO_AES_ARM_BS`, `CONFIG_CRYPTO_AES_ARM_CE`, and `CONFIG_CRYPTO_GHASH_ARM_CE`.

## Control flow
Kbuild links assembly cores with C glue into CryptoAPI modules or built-ins according to config.

## State and persistence behavior
No runtime state. It controls which algorithm providers are linked and named.

## Dependencies and integration points
Depends on C glue symbols matching assembly exports and CryptoAPI Kconfig symbols.

## Risks and edge cases
Mismatched object lists or symbol names produce link failures. Assembly cores require appropriate toolchain/architecture flags from the ARM build system.

## Test signals
Run ARM crypto builds with each algorithm enabled as module and built-in; confirm module names and CryptoAPI registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/Makefile -->
