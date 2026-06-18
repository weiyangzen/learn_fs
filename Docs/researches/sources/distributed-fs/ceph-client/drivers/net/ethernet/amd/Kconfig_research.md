# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/Kconfig

## Purpose
`amd/Kconfig` defines the kernel configuration menu for AMD-family Ethernet drivers. It gates visibility behind `NET_VENDOR_AMD` and declares selectable drivers for legacy LANCE variants, PCI PCnet/AMD8111, AMD XGBE, and AMD/Pensando core devices.

## Important APIs, Types, And Functions
Configuration symbols include `NET_VENDOR_AMD`, `A2065`, `AMD8111_ETH`, `PCNET32`, `ARIADNE`, `ATARILANCE`, `DECLANCE`, `HPLANCE`, `MIPS_AU1X00_ENET`, `MVME147_NET`, `SUN3LANCE`, `SUNLANCE`, `AMD_XGBE`, `AMD_XGBE_DCB`, `AMD_XGBE_HAVE_ECC`, and `PDS_CORE`. Dependencies select architecture/bus prerequisites such as ZORRO, PCI, DIO, SBUS, MIPS_ALCHEMY, MVME147, SUN3, ARM64, HAS_IOMEM, and optional PTP/DCB features. Several symbols select helper libraries such as CRC32, MII, PHYLIB, BITREVERSE, AUXILIARY_BUS, and NET_DEVLINK.

## Control Flow, State, And Integration
There is no runtime control flow. Kconfig state controls which objects in the AMD Makefile are built and what dependencies become available. The `NET_VENDOR_AMD` menu prevents irrelevant prompts on unsupported platforms. The common `7990.o` code is pulled indirectly by Makefile entries for HPLANCE and MVME147 when their config symbols are enabled.

## Dependencies
This file depends on Linux Kconfig semantics and architecture symbols. It integrates with `drivers/net/ethernet/amd/Makefile` and documentation references for PDS core.

## Risks And Test Signals
Risks include missing dependencies causing build failures on uncommon architectures, over-restrictive dependencies hiding valid drivers, missing selected libraries, and stale help text/module names. Test signals include `allyesconfig`, `allmodconfig`, architecture-specific configs for m68k/Sparc/MIPS/PCI, and verifying selected modules match Makefile object names.
