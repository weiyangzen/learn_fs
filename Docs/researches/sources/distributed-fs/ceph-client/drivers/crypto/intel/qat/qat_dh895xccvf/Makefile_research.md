# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xccvf/Makefile

Purpose: builds the DH895xCC virtual-function QAT driver module when `CONFIG_CRYPTO_DEV_QAT_DH895xCCVF` is enabled.

Important declarations: `qat_dh895xccvf.o` is composed from `adf_drv.o` and `adf_dh895xccvf_hw_data.o`.

Control flow and integration: this Kbuild file links the VF PCI driver and VF-specific hardware-data callbacks into one module. It relies on common QAT VF/PFVF support from parent directories.

State and persistence: build-time only; no runtime state.

Risks and test signals: config/build tests should ensure the VF module does not pull PF-only objects and that both VF probe and hw-data initialization symbols are linked.
