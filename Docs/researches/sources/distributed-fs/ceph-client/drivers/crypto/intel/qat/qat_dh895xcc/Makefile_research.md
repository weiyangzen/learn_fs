# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xcc/Makefile

Purpose: builds the physical-function DH895xCC QAT driver module when `CONFIG_CRYPTO_DEV_QAT_DH895xCC` is enabled.

Important declarations: the Kbuild target `qat_dh895xcc.o` is selected by the config symbol and is composed from `adf_drv.o` and `adf_dh895xcc_hw_data.o`.

Control flow and integration: this file connects the PCI probe/remove module implementation with chip-specific hardware-data initialization. It relies on common QAT objects from parent directories and produces the module that imports the `CRYPTO_QAT` namespace.

State and persistence: no runtime state is declared here; it controls build-time object aggregation only.

Risks and test signals: build tests should verify the config symbol produces exactly the PF module and that both listed objects are linked. Missing either object would leave the PCI driver without hardware callbacks or without module entry points.
