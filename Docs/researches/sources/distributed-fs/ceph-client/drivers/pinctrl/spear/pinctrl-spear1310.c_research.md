<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear1310.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear1310.c

## Purpose
This file is the SPEAr1310 SoC-specific pinmux table for the shared SPEAr pinctrl core. It describes pins 0 through 245, all SPEAr1310 muxable peripheral groups, the function-to-group map exported to the pinctrl subsystem, and GPIO fallback mux records used when selected pins are requested as GPIOs.

## Important APIs, Types, And Data
- `spear1310_pins[]` combines `SPEAR_PIN_0_TO_101` and `SPEAR_PIN_102_TO_245`.
- Register constants cover `PERIP_CFG`, `PCIE_SATA_CFG`, `PAD_FUNCTION_EN_0..2`, and `PAD_DIRECTION_SEL_0..2`.
- `struct spear_muxreg`, `struct spear_modemux`, `struct spear_pingroup`, and `struct spear_function` tables encode all hardware behavior.
- Major functions include `i2c0`, `ssp0`, `i2s0`, `i2s1`, `clcd`, `arm_gpio`, `smi`, `gmii`, `rgmii`, `smii_0_1_2`, `nand`, `keyboard`, `uart0`, `gpt0`, `gpt1`, `sdhci`, `cf`, `xd`, `uart1`, `uart2_3`, `uart4`, `uart5`, `i2c_1_2`, `i2c3_i2s1`, `i2c_4_5`, `i2c_6_7`, `can0`, `can1`, `pci`, `pci_express`, `sata`, `ssp1`, and `gpt64`.
- `DEFINE_2_MUXREG()` and `GPIO_PINGROUP()` build per-pin GPIO reclaim mappings for many muxed pads.
- `spear1310_machdata` is the final descriptor consumed by `spear_pinctrl_probe()`.

## Control Flow And Integration
The platform driver matches `st,spear1310-pinmux`. Probe is intentionally simple: `spear1310_pinctrl_probe()` passes the static `spear1310_machdata` to `spear_pinctrl_probe()`. The shared SPEAr core performs DT parsing, pinctrl registration, function selection, register updates through regmap, and GPIO handoff behavior.

Most groups program both a pad function-enable register and a direction-select register. Storage/media functions add extra selector writes: `sdhci`, `cf`, and `xd` share the `MCIF_MUXREG` sequence and then set `PERIP_CFG` to SD, CompactFlash, or XD mode. PCIe and SATA groups have no pin list and instead program fixed lane/clock/reset bits in `PCIE_SATA_CFG`. Ethernet variants select large shared pin ranges and either assert GMII bits or clear overlapping RGMII/SMII masks to route alternate wiring.

## State And Persistence
The file itself contains static tables and no mutable runtime state beyond platform-driver registration. Persistent hardware state is the set of MMIO register fields written by the common SPEAr core: pad function bits, direction-select bits, MCIF media selection, and PCIe/SATA lane configuration. GPIO persistence is represented by `spear1310_gpio_pingroup[]`, which tells the core which mux bits to clear/set when GPIO consumers request those pads.

## Dependencies
It depends on Linux platform/OF/init headers and local `pinctrl-spear.h` definitions. It depends behaviorally on the common SPEAr core honoring multi-register `spear_modemux` entries and on the pin names and macro ranges in `pinctrl-spear.h`.

## Risks And Review Notes
- Table consistency is the main risk. Pin arrays, group names, function group strings, and GPIO fallback entries must stay synchronized.
- Register masks often combine unrelated shared pins. A wrong value can disable boot-critical NAND, SD/MMC, GMII/RGMII, PCI, PCIe, or SATA routing.
- The `i2c3_unction` C identifier appears misspelled, although the function table still references it and the exported function name is `i2c3_i2s1`.
- Several muxes intentionally clear function bits to select alternate signals. These entries are easy to misread because `val = 0` can be the active peripheral selection, not GPIO.
- PCIe/SATA groups have no pins; consumers and debug tooling may show function selection as register-side configuration rather than a visible pin group.

## Test Signals
Build with the SPEAr pinctrl configuration and `W=1` to catch array/prototype drift. Boot a SPEAr1310 DT using `st,spear1310-pinmux` and verify pinctrl debugfs lists all groups/functions. Exercise representative states for NAND, SDHCI, CF/XD, UART/I2C alternate groups, GMII/RGMII/SMII, PCI, PCIe, SATA, and GPIO requests on muxed pads. Hardware register readback should confirm both `PAD_FUNCTION_EN_*` and `PAD_DIRECTION_SEL_*` fields change together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear1310.c -->
