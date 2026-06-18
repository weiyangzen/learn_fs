# sources/distributed-fs/ceph-client/drivers/crypto/starfive/Kconfig

## Purpose
This Kconfig file defines `CRYPTO_DEV_JH7110`, the build option for the StarFive JH7110 cryptographic engine driver. It gates compilation of the StarFive crypto module and declares the Crypto API algorithm dependencies needed by the AES, hash, and RSA implementation files.

## Important configuration behavior
`CRYPTO_DEV_JH7110` is a tristate option named "StarFive JH7110 cryptographic engine driver". It depends on either `SOC_STARFIVE && AMBA_PL08X` or `COMPILE_TEST`, and also on `HAS_DMA`. It selects `CRYPTO_ENGINE`, HMAC, SHA256, SHA512, SM3, RSA, AES, CCM, GCM, ECB, CBC, and CTR support. The help text states that the module accelerates public key algorithms, skciphers, AEAD, and hash functions, and that the module name is `jh7110-crypto`.

## Integration points
The selected symbols align with the source files listed in the local Makefile: `jh7110-cryp.o` for the platform/engine, `jh7110-hash.o` for hash/HMAC/SM3/SHA, `jh7110-rsa.o` for RSA, and `jh7110-aes.o` for AES skcipher/AEAD. The `AMBA_PL08X` dependency reflects the DMA controller expected by the driver.

## Risks
Because the option selects several crypto algorithms, enabling it can pull in more Crypto API code than only the hardware driver. `COMPILE_TEST` permits builds outside StarFive SoCs, so compile coverage should catch missing architecture assumptions. Runtime still requires DMA channels, clocks, reset, and a matching device tree node.

## Test signals
Build-test as built-in and module, with and without `COMPILE_TEST`, and verify that selecting the option brings in the required crypto helpers. Runtime tests should confirm that the module registers only when the `starfive,jh7110-crypto` platform device and DMA resources are present.
