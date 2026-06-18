# sources/distributed-fs/ceph-client/drivers/phy/xilinx/phy-zynqmp.c

## Purpose
Xilinx ZynqMP PS-GTR transceiver driver. It exposes four lanes as generic PHYs for USB3, SATA, DisplayPort, PCIe, and SGMII, configures reference clocks and PLL/SSC settings, validates lane/controller mappings, applies protocol init, and saves/restores runtime PM state.

## APIs, Flow, And State
`struct xpsgtr_dev` stores controller resources, lane objects, refclks, mutex, TX termination workaround flag, saved ICM registers, and saved lane registers. `struct xpsgtr_phy` records lane, protocol, instance, refclk, and skip-init state. Probe maps `serdes`/`siou`, gets `ref0`-`ref3`, creates four PHYs and debugfs status files, registers OF xlate, enables runtime PM, and allocates save storage. Xlate consumes lane/type/instance/refclk cells. PHY init enables refclk, optionally applies TX termination fix, configures PLL/SSC, writes ICM protocol, and runs DP/SATA/SGMII setup. Power-on waits for PLL lock; configure handles DP swing/pre-emphasis.

## Dependencies And Integration
Uses generic PHY, clocks, runtime PM, debugfs, OF xlate, MMIO, and PHY type bindings. Integrated with USB, SATA, DP, PCIe, and Ethernet consumers.

## Risks And Tests
ICM validation checks instance values without tying them to protocol columns, `saved_regs` allocation failure after PM resume lacks full unwind, clock-enable failure loses the exact error, and DP table indexes are not range-checked here. Test valid/invalid phandles, all refclk rates, PLL lock timeout, DP configure, SATA SIOU writes, SGMII bus width, TX termination fix, runtime resume skip, debugfs, and clock balancing.
