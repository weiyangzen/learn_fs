<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/Makefile

Purpose: defines the Qualcomm Crypto Engine module composition for the kernel build.

Important build contract: `CONFIG_CRYPTO_DEV_QCE` builds `qcrypto.o` from `core.o`, `common.o`, and `dma.o`. Feature Kconfig options add `sha.o`, `skcipher.o`, and `aead.o` through conditional `qcrypto-*` object lists.

Control flow and integration: the Makefile keeps the platform driver, shared register setup, and DMA helper always present for QCE, while allowing hash, skcipher, and AEAD algorithm families to be compiled independently.

State and persistence: no runtime state. Build state determines which `qce_algo_ops` are present in `core.c`.

Dependencies: Kbuild object aggregation and `CONFIG_CRYPTO_DEV_QCE_{SHA,SKCIPHER,AEAD}`.

Risks and test signals: mismatched Kconfig options can expose references only when a feature object is included. Build-test all feature combinations: core only, each single algorithm family, and all enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/Makefile -->
