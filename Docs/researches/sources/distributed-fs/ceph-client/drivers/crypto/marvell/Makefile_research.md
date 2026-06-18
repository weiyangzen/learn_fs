# sources/distributed-fs/ceph-client/drivers/crypto/marvell/Makefile

Purpose: routes Marvell crypto configuration symbols to their implementation subdirectories.

Important declarations: `CRYPTO_DEV_MARVELL_CESA` builds `cesa/`, `CRYPTO_DEV_OCTEONTX_CPT` builds `octeontx/`, and `CRYPTO_DEV_OCTEONTX2_CPT` builds `octeontx2/`.

Control flow and integration: this is the top-level Kbuild switchboard for Marvell crypto drivers.

State and persistence: no runtime state.

Risks and test signals: build tests should verify enabling only CESA does not descend into CPT directories, and vice versa.
