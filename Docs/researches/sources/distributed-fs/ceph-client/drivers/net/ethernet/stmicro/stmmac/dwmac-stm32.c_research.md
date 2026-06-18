<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-stm32.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-stm32.c

## Purpose
`dwmac-stm32.c` is the STM32 MCU/MP1/MP13/MP25 stmmac glue layer. It selects Ethernet PHY mode in SYSCFG, validates and enables clock sources, handles low-power stop clocks and wake IRQs, and provides suspend/resume clock sequencing for STM32 variants.

## Important APIs, Types, and Functions
- `struct stm32_dwmac` stores TX/RX/ETH/syscfg/stop clocks, PHY clock-source flags, wake IRQ, SYSCFG register/mask, speed, ops, and device.
- `struct stm32_ops` selects mode programming, suspend/resume hooks, extra parsing, and variant flags.
- `stm32_dwmac_clk_enable()` and `stm32_dwmac_clk_disable()` manage TX/RX/syscfg/ETH clocks.
- `stm32mp1_select_ethck_external()` and `stm32mp1_validate_ethck_rate()` decide and validate ETH_CK use.
- `stm32mp1_configure_pmcr()` and `stm32mp2_configure_syscfg()` write MP1/MP2 syscfg mode bits.
- `stm32mcu_set_mode()` programs MCU MII/RMII selection.
- `stm32mp1_parse_data()` reads clock-source properties, optional wake IRQ, and low-power clocks.
- `stm32_dwmac_probe/remove()` manage stmmac lifecycle and extra suspend RX clock enable.

## Control Flow
Probe obtains resources and stmmac DT data, selects variant ops, parses required TX/RX clocks and variant-specific data, stores private state, installs suspend/resume callbacks, runs initial mode selection and clock enable, optionally enables RX clock a second time for suspend retention, then registers stmmac. Remove unregisters stmmac, balances the extra RX clock, disables clocks, and clears wake IRQ setup. Suspend disables normal clocks then enables ETH stop clock for MP variants; resume disables stop clock and reruns init.

## State and Persistence
Private state is per-device. Hardware state includes SYSCFG mode registers, PMCCLRR clear writes on MP1, clock enable counts, optional wake IRQ registration, and device wakeup enablement. No file-backed persistence exists.

## Dependencies and Integration Points
It depends on clk APIs, syscon/regmap phandle arguments, PM wake IRQ helpers, stmmac platform PM, OF properties, and generic PHY selectors. Compatible strings include `st,stm32-dwmac`, `st,stm32mp1-dwmac`, `st,stm32mp13-dwmac`, and `st,stm32mp25-dwmac`.

## Risks and Edge Cases
- ETH_CK frequency must match PHY mode when enabled; invalid board clocks fail init.
- MP13 requires a syscfg mask in DT; older MP1 can default it.
- Wake IRQ setup is conditional on no `eth-ck` clock and can leave wake disabled by default.
- Clock enable/disable order must balance the extra RX suspend reference.
- MP2 uses a different full-width ETHCR mask and always selects PTP clock from RCC.

## Test Signals
Test MCU MII/RMII and MP MII/GMII/RGMII/RMII modes, ETH_CK 25/50/125 MHz validation, syscfg clear/set writes, wake IRQ registration and wake enable toggling, suspend/resume in low-power stop, remove path clock balancing, and probe failure for missing required clocks or invalid syscfg masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-stm32.c -->
