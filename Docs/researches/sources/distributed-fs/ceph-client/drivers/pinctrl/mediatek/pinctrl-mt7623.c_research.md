# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7623.c

## Purpose
`pinctrl-mt7623.c` describes the MT7623 pin controller for the MediaTek Moore pinctrl core. It maps a large 280-entry pin namespace onto register fields, pin groups, device-tree function names, EINT metadata, and one SoC-specific post-probe bonding workaround.

## Important APIs, Types, And Data
The driver uses `pinctrl-moore.h` and the common MediaTek v2 pinctrl data model. `MT7623_PIN()` wraps `MTK_PIN()` with EINT mux value 0 and per-pin drive group selection. The custom `PIN_FIELD15`, `PIN_FIELD16`, and `PINS_FIELD16` helpers express register fields with 15-bit or 16-bit packing, matching the MT7623 register layout.

Register calculators cover mode, direction, data input/output, IES, Schmitt trigger, pull enable, pull select, drive strength, TDSEL, PUPD, R0, and R1. The PUPD/R0/R1 fields focus on MSDC-related pins, reflecting advanced pull resistor handling for storage interfaces. `mt7623_pins` names pins 0 through 279, spanning PMIC wrapper, SPI, RTC, watchdog, audio/I2S/PCM/SPDIF, NAND, WLAN/BT, display/HDMI/MIPI, MSDC, PCIe, USB OTG, Ethernet, JTAG, and many internal rambuf pins.

Group/function tables expose many user-facing functions: `audck`, `disp`, `eth`, `sdio`, `hdmi`, `i2c`, `i2s`, `ir`, `lcd`, `msdc`, `nand`, `otg`, `pcie`, `pcm`, `pwm`, `pwrap`, `rtc`, `spi`, `spdif`, `uart`, and `watchdog`.

## Control Flow
`arch_initcall(mtk_pinctrl_init)` registers the platform driver named `mt7623-moore-pinctrl`. On a `mediatek,mt7623-moore-pinctrl` device, `mt7623_pinctrl_probe()` calls `mtk_moore_pinctrl_probe(pdev, &mt7623_data)`. If probe succeeds, `mt7623_bonding_disable()` obtains `struct mtk_pinctrl *` from platform driver data and uses `mtk_rmw()` to clear bonding constraints in `PIN_BOND_REG0`, `PIN_BOND_REG1`, and `PIN_BOND_REG2`, enabling high-numbered mux modes for PCIe, I2S, and MSDC0E.

## State And Persistence
Most state is immutable table data. The one intentional hardware state mutation is the bonding-disable sequence after common probe. That change is persistent in the live register state until reset or later reprogramming, and it affects mux-mode availability rather than individual Linux objects.

## Dependencies And Integration Points
The file depends on the common Moore probe path, MediaTek register update helper `mtk_rmw()`, shared pinconf callbacks, and the EINT subsystem. `mt7623_eint_hw` declares 6 ports, 169 AP EINTs, 20 debounce counters, and `debounce_time_mt2701`. `mt7623_data` uses rev1 bias and drive callbacks plus advanced pull get/set hooks.

## Risks
This file has the highest table-maintenance risk in the group. The source includes duplicate group names such as repeated `pcie1_1_perst`; function lists also appear to reference names not declared in `mt7623_groups`, for example several later PWM names and duplicate `"spi2"` in the SPI function list. Those string mismatches may not fail compilation but can make device tree function/group selection fail at runtime. The bonding-disable write sequence is also sensitive: wrong register masks could expose unsupported muxes or change package-bond behavior globally.

## Test Signals
Compile testing is necessary but insufficient because many group/function errors are string-level. Boot logs should show successful probe and no pinctrl lookup failures for board DTS files. Practical tests should exercise storage pull configuration through MSDC/eMMC/SD paths, PCIe reset/wake/clkreq variants including revised modes, I2C/UART/SPI alternatives, EINT operation for the AP EINT range, and the high-mode paths that rely on `mt7623_bonding_disable()`.
