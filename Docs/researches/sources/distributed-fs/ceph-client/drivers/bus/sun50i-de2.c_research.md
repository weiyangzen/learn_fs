# sources/distributed-fs/ceph-client/drivers/bus/sun50i-de2.c

## Purpose
This built-in Allwinner A64 Display Engine 2.0 bus driver claims the required SRAM mapping for the display engine bus and then populates child display-engine devices.

## Important APIs, Types, and Functions
`sun50i_de2_bus_probe()` calls `sunxi_sram_claim()` for the bus device and then `of_platform_populate()`. `sun50i_de2_bus_remove()` releases the SRAM claim. The driver matches `allwinner,sun50i-a64-de2` and is registered with `builtin_platform_driver()`.

## Control Flow
Probe claims SRAM before creating any children, so child display drivers only appear when the SRAM routing is available. Remove releases SRAM but does not explicitly depopulate children in this source.

## State and Persistence
The driver stores no private state. Persistent state is the SRAM ownership/routing managed by the sunxi SRAM subsystem for the lifetime of the platform device.

## Dependencies and Integration Points
It depends on OF platform population and `linux/soc/sunxi/sunxi_sram.h`. It integrates with Allwinner display-engine child nodes whose access depends on SRAM mapping.

## Risks and Test Signals
Risks are minimal but include no check of `of_platform_populate()` return value and no explicit child depopulation before SRAM release on remove. Test signals include successful SRAM claim, display-engine child probing, and failure propagation when SRAM cannot be mapped.
