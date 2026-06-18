# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/Kconfig

## Purpose
Defines build-time configuration for the DEC Tulip family and related PCI/CardBus Ethernet drivers.

## Important APIs, Types, and Functions
Defines the group gate `NET_TULIP`, individual driver symbols `DE2104X`, `TULIP`, `WINBOND_840`, `DM9102`, `ULI526X`, and `PCMCIA_XIRCOM`, plus tuning symbols `DE2104X_DSL`, `TULIP_MWI`, `TULIP_MMIO`, `TULIP_NAPI`, `TULIP_NAPI_HW_MITIGATION`, and SPARC helper `TULIP_DM910X`. Driver options select needed library symbols such as `CRC32` and `MII`.

## Control Flow and State
There is no runtime flow. Build-time control chooses which drivers compile, whether the main Tulip driver uses MMIO, NAPI, hardware interrupt mitigation, memory-write-invalidate configuration, and descriptor skip length for early DE2104X hardware.

## Dependencies and Integration Points
Consumed by Kbuild and the parent DEC vendor Kconfig. Symbols are referenced by `dec/tulip/Makefile` and by driver source conditionals such as `CONFIG_TULIP_NAPI`, `CONFIG_TULIP_NAPI_HW_MITIGATION`, `CONFIG_DE2104X_DSL`, and `CONFIG_TULIP_DM910X`.

## Risks and Test Signals
Risks include wrong bus dependencies, missing `select CRC32/MII`, invalid descriptor skip ranges, or enabling experimental Tulip options on unsupported builds. Test signals are `oldconfig` prompts, allyesconfig/allmodconfig builds, NAPI and non-NAPI compile coverage, SPARC DM910X symbol behavior, and successful module names matching help text.
