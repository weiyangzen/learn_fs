# sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/Kconfig

Purpose: defines configuration prompts for SGI Ethernet drivers.

Important symbols: `NET_VENDOR_SGI` gates the vendor menu and depends on either PCI IOC3 MFD support or SGI IP32. `SGI_IOC3_ETH` is a built-in boolean for IOC3 Ethernet, depending on `PCI && SGI_MFD_IOC3` and selecting CRC16, CRC32, and MII. `SGI_O2MACE_ETH` is tristate O2 MACE support and depends on `SGI_IP32=y`.

Integration and state: Kconfig controls whether `ioc3-eth.o` and `meth.o` are reachable from the SGI Makefile. It has no runtime state.

Risks and tests: dependency mistakes break architecture-specific builds. Test `olddefconfig`/build combinations for SGI IP32, SGI_MFD_IOC3, and generic PCI-disabled configs.
