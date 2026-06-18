
# sources/distributed-fs/ceph-client/drivers/crypto/xilinx/Makefile

Purpose: Kbuild rules for Xilinx/AMD crypto drivers.

Important APIs, types, and functions: maps `CONFIG_CRYPTO_DEV_XILINX_TRNG` to `xilinx-trng.o`, `CONFIG_CRYPTO_DEV_ZYNQMP_AES` to `zynqmp-aes-gcm.o`, and `CONFIG_CRYPTO_DEV_ZYNQMP_SHA3` to `zynqmp-sha.o`.

Control flow: no runtime flow. The file determines which driver objects are compiled and linked based on kernel configuration.

State and persistence: no runtime state.

Dependencies and integration points: integrates with the parent crypto Kbuild and the corresponding Kconfig options outside this subset.

Risks and test signals: build coverage should verify each config can be built independently and together. Missing Kconfig dependencies would surface as unresolved firmware, crypto, or hwrng symbols.
