# sources/distributed-fs/ceph-client/drivers/crypto/ccp/Kconfig

## Purpose

`Kconfig` defines build-time options for the AMD Secure Processor/CCP driver family: the base Secure Processor device driver, the CCP cryptographic coprocessor device, the Crypto API offload module, the Platform Security Processor, and optional CCP debugfs exposure.

## Important APIs, Types, And Functions

- `CRYPTO_DEV_CCP_DD` builds the base `ccp` module and depends on AMD CPU support or ARM64.
- `CRYPTO_DEV_SP_CCP` enables the CCP device under the base driver, depends on `CRYPTO_DEV_CCP_DD && DMADEVICES`, and selects RNG, DMA engine, SHA1, and SHA256 support.
- `CRYPTO_DEV_CCP_CRYPTO` builds the `ccp_crypto` module, depends on the base and CCP device options, and selects hash/skcipher/authenc/RSA/AES library support.
- `CRYPTO_DEV_SP_PSP` enables PSP support on x86_64 with AMD IOMMU and selects `PCI_TSM` when PCI is enabled.
- `CRYPTO_DEV_CCP_DEBUGFS` gates debugfs internals and depends on CCP device support.

## Control Flow

There is no runtime control flow. Kconfig dependencies decide which objects are compiled by the Makefile and which kernel subsystems are selected automatically.

## State And Persistence Behavior

The file contributes persistent kernel configuration state through `.config` symbols. Those symbols determine compiled modules and runtime availability of CCP, PSP, crypto offload, DMAengine, hwrng, and debugfs functionality.

## Dependencies And Integration Points

This file integrates with `drivers/crypto/ccp/Makefile`, kernel Crypto API configuration, DMAengine, hwrng, AMD IOMMU, PCI TSM, and debugfs. Its selected symbols ensure core algorithms needed by CCP wrappers are available.

## Risks And Edge Cases

- `CRYPTO_DEV_SP_CCP` defaults to `y` once the base driver and DMA devices are enabled, so platform builds can include hardware code by default.
- `CRYPTO_DEV_CCP_CRYPTO` depends on CCP device support; disabling the device disables Crypto API offload even if the base Secure Processor module remains.
- Debugfs exposure is optional and should remain off by default for minimal introspection surface.

## Test Signals

Build matrix signals include `ccp.o` without crypto offload, `ccp_crypto.o` with offload, debugfs-enabled builds, PSP-only/base-only combinations, ARM64 platform builds, x86_64 PSP builds, and module load ordering under `m` defaults.
