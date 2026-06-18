# sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/Makefile

Purpose: builds the Marvell CESA crypto engine module.

Important declarations: `marvell-cesa.o` is built when `CONFIG_CRYPTO_DEV_MARVELL_CESA` is enabled and is composed of `cesa.o`, `cipher.o`, `hash.o`, and `tdma.o`.

Control flow and integration: this Kbuild file links core platform probing, skcipher algorithms, hash algorithms, and TDMA support into one driver.

State and persistence: build-time only.

Risks and test signals: missing `hash.o` or `tdma.o` would satisfy some symbols only when corresponding algorithms/features are used, so build coverage should include TDMA and hash-enabled platforms.
