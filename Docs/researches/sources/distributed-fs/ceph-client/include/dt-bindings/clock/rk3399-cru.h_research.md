# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3399-cru.h

## Purpose
`rk3399-cru.h` is the device-tree ABI header for the Rockchip RK3399 clock and reset unit. It gives DTS files and the RK3399 CRU/PMUCRU clock driver stable integer IDs for PLLs, ARM core clocks, special clocks, ACLK/PCLK/HCLK bus gates, display/media clocks, and soft-reset lines.

## Important APIs, types, and functions
There are no C functions or types; the exported API is the macro namespace. Important families are `PLL_*` for PLL IDs, `ARMCLKL`/`ARMCLKB` for little/big CPU clusters, `SCLK_*` for special/peripheral source clocks, `ACLK_*`, `PCLK_*`, and `HCLK_*` for bus-domain gates, `DCLK_*` for display clocks, and `SRST_*` for reset specifiers. The reset block is grouped by `cru_softrst_con0` through later CRU reset registers plus PMU reset IDs.

## Control flow
The header has compile-time inclusion flow only: the guard `_DT_BINDINGS_CLK_ROCKCHIP_RK3399_H` prevents duplicate definitions, and consumers include the macros into device trees or drivers. At runtime, a clock phandle cell using one of these IDs is resolved by the RK3399 CRU provider, which maps the ID to clock/reset operations in the driver tables.

## State and persistence
No state is stored in the header. The numeric IDs are persistent ABI values: changing or reusing them would break existing device trees and any compiled DTBs that reference RK3399 clock or reset specifiers.

## Dependencies and integration points
It integrates with RK3399 DTS nodes, `drivers/clk/rockchip` clock tables, reset-controller users, power-domain descriptions, and peripheral drivers requesting clocks by phandle. The PMU clock indices are part of the same ABI for always-on/low-power domains.

## Risks and test signals
Main risks are renumbering stable IDs, assigning a peripheral to the wrong bus family, missing reset lines when adding device-tree nodes, and confusing CRU and PMU reset spaces. Test signals include `dtbs_check`, successful boot-time CRU registration, no unresolved clock/reset phandles, and peripheral probes for UART, I2C, MMC, USB, VOP, VPU, GPU, and PCIe blocks that consume these IDs.
