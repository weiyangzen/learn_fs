# sources/distributed-fs/ceph-client/drivers/crypto/ccp/Makefile

## Purpose

The CCP `Makefile` maps Kconfig symbols to object composition for the AMD Secure Processor/CCP driver. It builds the base `ccp` module from SP bus/platform code plus optional CCP, PCI, PSP, debugfs, and TSM pieces, and builds the separate `ccp-crypto` module from Crypto API algorithm providers.

## Important APIs, Types, And Functions

- `obj-$(CONFIG_CRYPTO_DEV_CCP_DD) += ccp.o` creates the base module.
- `ccp-objs := sp-dev.o sp-platform.o` are always part of the base module.
- `ccp-$(CONFIG_CRYPTO_DEV_SP_CCP)` adds CCP device, operation, v3/v5, and DMAengine files.
- `ccp-$(CONFIG_CRYPTO_DEV_CCP_DEBUGFS)` adds `ccp-debugfs.o`.
- `ccp-$(CONFIG_PCI)` adds `sp-pci.o`.
- `ccp-$(CONFIG_CRYPTO_DEV_SP_PSP)` adds PSP/SEV/TEE/platform-access/DBC/HSTI/SFS objects.
- `ccp-$(CONFIG_CRYPTO_DEV_SP_PSP)` additionally adds SEV TSM/TIO files when `CONFIG_PCI_TSM=y`.
- `obj-$(CONFIG_CRYPTO_DEV_CCP_CRYPTO) += ccp-crypto.o` creates the Crypto API module.
- `ccp-crypto-objs` lists AES, CMAC, XTS, GCM, DES3, RSA, and SHA providers plus the crypto main queue.

## Control Flow

There is no runtime control flow. Kbuild evaluates configuration symbols and composes linked modules from the selected object lists.

## State And Persistence Behavior

Build output state is the generated `ccp.ko` and `ccp_crypto.ko` modules or built-in objects. The split means hardware device support can exist independently from Crypto API offload registration.

## Dependencies And Integration Points

The file integrates Kconfig with Kbuild and ensures `ccp-crypto-main.c` is linked with all algorithm provider implementations. It also keeps PSP and CCP device code in one base module, sharing SP bus infrastructure.

## Risks And Edge Cases

- The base module can grow substantially when PSP and CCP are both enabled; object-level dependencies must avoid unresolved symbols for disabled features.
- `ccp-crypto` assumes exported core APIs such as `ccp_present()`, `ccp_version()`, and `ccp_enqueue_cmd()` are available from the base driver.
- Conditional TSM objects are tied to both PSP and `PCI_TSM=y`; module/built-in combinations need build coverage.

## Test Signals

Signals include `make M=drivers/crypto/ccp` for combinations of CCP, PSP, PCI, debugfs, and crypto offload; module dependency checks showing `ccp_crypto` depending on `ccp`; and boot/module-load tests for each built object set.
