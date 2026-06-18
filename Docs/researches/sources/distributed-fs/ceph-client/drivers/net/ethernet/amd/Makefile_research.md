# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/Makefile

## Purpose
`amd/Makefile` maps AMD Ethernet Kconfig symbols to build objects and subdirectories. It is the build glue for legacy AMD LANCE drivers, PCI drivers, AMD XGBE, and AMD/Pensando core support.

## Important APIs, Types, And Functions
The important entries are `obj-$(CONFIG_A2065) += a2065.o`, `obj-$(CONFIG_AMD8111_ETH) += amd8111e.o`, `obj-$(CONFIG_ARIADNE) += ariadne.o`, `obj-$(CONFIG_ATARILANCE) += atarilance.o`, `obj-$(CONFIG_DECLANCE) += declance.o`, `obj-$(CONFIG_HPLANCE) += hplance.o 7990.o`, `obj-$(CONFIG_MIPS_AU1X00_ENET) += au1000_eth.o`, `obj-$(CONFIG_MVME147_NET) += mvme147.o 7990.o`, `obj-$(CONFIG_PCNET32) += pcnet32.o`, `obj-$(CONFIG_SUN3LANCE) += sun3lance.o`, `obj-$(CONFIG_SUNLANCE) += sunlance.o`, `obj-$(CONFIG_AMD_XGBE) += xgbe/`, and `obj-$(CONFIG_PDS_CORE) += pds_core/`.

## Control Flow, State, And Integration
There is no runtime flow. Kbuild evaluates enabled config symbols and compiles or descends into the listed objects/directories. The key integration point for this work item is that `7990.o` is shared by both HPLANCE and MVME147, so changes to generic LANCE routines affect both platform drivers.

## Dependencies
It depends on symbols declared in `amd/Kconfig`, Kbuild object syntax, and the source files/subdirectories being present. Build ordering is simple object aggregation.

## Risks And Test Signals
Risks include duplicate inclusion of common objects if multiple configs are built into the same linkage unit, stale object names, and missing subdirectory wiring. Test signals include building combinations of `CONFIG_HPLANCE` and `CONFIG_MVME147_NET`, AMD allmodconfig coverage, and verifying modules contain expected objects.
