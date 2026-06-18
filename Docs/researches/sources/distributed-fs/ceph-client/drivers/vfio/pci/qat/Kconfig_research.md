# sources/distributed-fs/ceph-client/drivers/vfio/pci/qat/Kconfig

Purpose: adds `QAT_VFIO_PCI`, a VFIO PCI migration driver for Intel QAT VFs.

Important configuration: selects `VFIO_PCI_CORE` and depends on one of the QAT PF drivers (`CRYPTO_DEV_QAT_4XXX`, `420XX`, or `6XXX`). Help text identifies the module name `qat_vfio_pci`.

Control flow and integration: this option enables the QAT VFIO PCI module built from `main.c`, relying on the QAT migration device API exported by the crypto QAT driver.

Risks and test signals: dependency coverage must prevent builds without QAT migration symbols. Build tests should include module and built-in combinations.
