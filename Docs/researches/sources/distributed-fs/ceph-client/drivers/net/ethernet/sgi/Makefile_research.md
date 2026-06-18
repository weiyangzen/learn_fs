# sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/Makefile

Purpose: maps SGI Ethernet Kconfig symbols to object files.

Important entries: `obj-$(CONFIG_SGI_O2MACE_ETH) += meth.o` and `obj-$(CONFIG_SGI_IOC3_ETH) += ioc3-eth.o`.

Integration and state: participates in kernel kbuild only. No runtime state.

Risks and tests: object-name drift or wrong symbol names would silently omit drivers. Test by building both SGI symbols as enabled/module where supported.
