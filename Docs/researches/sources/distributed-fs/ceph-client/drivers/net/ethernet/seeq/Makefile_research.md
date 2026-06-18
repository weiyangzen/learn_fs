# sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/Makefile

Purpose: Maps SEEQ Kconfig symbols to driver objects.

Important APIs and flow: `obj-$(CONFIG_ARM_ETHER3) += ether3.o` builds the Acorn/ANT Ether3 driver, and `obj-$(CONFIG_SGISEEQ) += sgiseeq.o` builds the SGI Seeq8003 driver.

State and dependencies: The Makefile depends entirely on Kconfig symbol selection and provides no additional state. It is consumed by the kernel build system under the Ethernet driver tree.

Risks and test signals: The main risk is symbol/object drift if driver files or Kconfig names change. Build coverage for both tristate options as built-in and module should confirm object selection.
