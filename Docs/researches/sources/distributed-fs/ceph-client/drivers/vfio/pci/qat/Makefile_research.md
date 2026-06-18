# sources/distributed-fs/ceph-client/drivers/vfio/pci/qat/Makefile

Purpose: wires the QAT VFIO PCI migration module into kbuild.

Important build behavior: `obj-$(CONFIG_QAT_VFIO_PCI)` creates `qat_vfio_pci.o` from `main.o`.

Dependencies and integration: the module imports the `CRYPTO_QAT` namespace in `main.c`.

Risks and test signals: build tests should verify symbol namespace import and all QAT generation dependency combinations.
