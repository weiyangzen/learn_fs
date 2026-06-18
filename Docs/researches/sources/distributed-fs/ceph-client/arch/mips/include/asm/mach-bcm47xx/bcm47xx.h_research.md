# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm47xx/bcm47xx.h

**Purpose:** Defines the BCM47xx common bus abstraction for systems using either SSB or BCMA internal buses.

**Important APIs/types/functions:** Exports `enum bcm47xx_bus_type`, `union bcm47xx_bus` containing `struct ssb_bus` and/or `struct bcma_soc` depending on Kconfig, extern `bcm47xx_bus`, extern `bcm47xx_bus_type`, and `bcm47xx_set_system_type(u16 chip_id)`. Includes SSB, BCMA, NVRAM, and SPROM headers.

**Control flow:** Platform probe selects the active internal bus, populates the union, sets the bus type, and records a system type based on chip ID. Later code branches on `bcm47xx_bus_type` to access SSB or BCMA-specific resources.

**State and persistence behavior:** Global bus union and bus type persist for the running kernel and represent discovered SoC fabric state. The header declares, but does not define, that state.

**Dependencies and integration points:** Integrated by BCM47xx early platform setup, SSB/BCMA bus cores, NVRAM/SPROM handling, wireless/Ethernet/flash drivers, and system type reporting.

**Risks:** The union is Kconfig-shaped; code must not access unavailable members. Incorrect bus type or chip ID breaks all downstream device discovery. Including both bus backends requires careful runtime checks.

**Test signals:** Build SSB-only, BCMA-only, and combined configurations where supported; boot hardware from both families, verify bus detection, SPROM/NVRAM access, device enumeration, and system type strings.
