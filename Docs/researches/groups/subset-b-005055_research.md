# Research Group subset-b-005055

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7622.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7622.c

## Purpose
`pinctrl-mt7622.c` is the MediaTek MT7622 SoC pinctrl description for the common "Moore" pinctrl core. It is not an algorithm-heavy driver; it supplies the static pin, register-field, pin group, pin function, external interrupt, and pin configuration callback metadata consumed by `mtk_moore_pinctrl_probe()`.

## Important APIs, Types, And Data
The file includes `pinctrl-moore.h` and relies on shared types such as `struct mtk_pin_field_calc`, `struct mtk_pin_reg_calc`, `struct mtk_pin_desc`, `struct group_desc`, `struct pinfunction`, `struct mtk_eint_hw`, and `struct mtk_pin_soc`. `MT7622_PIN()` wraps `MTK_PIN()` with EINT mux value 1, EINT number equal to the GPIO number, and drive group `DRV_GRP0`.

The register calculator arrays map pin numbers 0 through 102 to MT7622 register offsets and bit fields. Covered logical registers include mode, direction, input, output, slew rate, Schmitt trigger, pull-up, pull-down, E4/E8 drive selection, TDSEL, and RDSEL. `mt7622_reg_cals` binds these arrays to `PINCTRL_PIN_REG_*` indices.

`mt7622_pins` names 103 pads, including GPIO, I2S, SPI, I2C, Ethernet, NAND/eMMC, PMIC, PCIe, PWM, UART, watchdog, and LED pads. The many `*_pins` and `*_funcs` arrays define pinmux groups, and `mt7622_groups` exposes them through `PINCTRL_PIN_GROUP()`. `mt7622_functions` then publishes user-facing mux functions such as `antsel`, `emmc`, `eth`, `i2c`, `i2s`, `ir`, `led`, `flash`, `pcie`, `pmic`, `pwm`, `sd`, `spi`, `tdm`, `uart`, and `watchdog`.

## Control Flow
The only runtime flow in this file is platform driver registration and probe. `arch_initcall(mt7622_pinctrl_init)` registers `mt7622_pinctrl_driver`. Device tree matching uses compatible string `mediatek,mt7622-pinctrl`. `mt7622_pinctrl_probe()` passes the static `mt7622_data` descriptor to `mtk_moore_pinctrl_probe()`, which performs the actual pinctrl, GPIO, pinmux, pinconf, and EINT registration.

## State And Persistence
The file owns no dynamic or persistent runtime state. All state is static constant hardware description data. Runtime pin state is maintained in SoC registers through the common pinctrl core. The descriptor selects `gpio_m = 1`, `ies_present = false`, default MediaTek register base names, standard bias callbacks, and standard drive callbacks.

## Dependencies And Integration Points
Integration is through Linux platform-driver probing, device tree compatible matching, the common MediaTek v2 pinctrl register calculator, pinmux group/function descriptors, and the MediaTek EINT subsystem. `mt7622_eint_hw` declares 7 EINT ports, AP EINT count equal to the pin count, 20 debounce counters, and `debounce_time_mt6765`.

## Risks
The file is table-driven, so the main risks are silent metadata mistakes: wrong register offsets, wrong bit widths, mismatched pin/function array lengths, or group names omitted from function lists. Because `ies_present` is false while many newer SoCs expose IES fields, any board-level expectation of per-pin input-enable control must match MT7622 hardware behavior. Pin groups also contain many overlapping alternatives, so device tree consumers must select non-conflicting groups.

## Test Signals
Useful validation signals are compile coverage for array and descriptor declarations, boot-time probe success for `mediatek,mt7622-pinctrl`, GPIO direction/input/output tests across several banks, pinmux smoke tests for Ethernet, SPI, UART, I2C, PCIe reset/wake, and storage groups, EINT debounce tests, and pinconf get/set tests for bias and drive callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7622.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7623.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7623.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7629.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7629.c

## Purpose
`pinctrl-mt7629.c` provides the MT7629 SoC pinctrl description for the common MediaTek Moore pinctrl framework. It maps 79 pins to register ranges, pin groups, device-tree functions, EINT metadata, and pin configuration callbacks.

## Important APIs, Types, And Data
`MT7629_PIN()` wraps `MTK_PIN()` with EINT mux value 0, a caller-supplied EINT number, and drive group `DRV_GRP1`. The register calculators cover mode, direction, data input/output, IES, Schmitt trigger, pull enable, pull select, drive strength, TDSEL, and RDSEL. Most non-GPIO pad controls are partitioned by broad pin ranges at offsets `0x1000` through `0x7600`, while GPIO mode/dir/di/do use the standard lower offsets.

`mt7629_pins` names pads for Wi-Fi 2G/5G interfaces, LEDs, watchdog, I2C, GPIO, UART, Ethernet PHY MDI pairs, SMI MDC/MDIO, PCIe, PWM, SPI, and UART0. Pin group arrays model ePHY/GPHY LEDs, I2C alternatives, SPI and optional WP/HOLD pins, UART data/control pairs, MDIO, PCIe reset/wake/clkreq, PWM, Wi-Fi front-end groups, serial NAND, and SPI NOR. `mt7629_functions` exposes `eth`, `i2c`, `led`, `pcie`, `pwm`, `spi`, `uart`, `watchdog`, `wifi`, and `flash`.

## Control Flow
`arch_initcall(mt7629_pinctrl_init)` registers a platform driver named `mt7629-pinctrl`. Device tree matching uses `mediatek,mt7629-pinctrl`. Probe is a single delegation: `mt7629_pinctrl_probe()` calls `mtk_moore_pinctrl_probe(pdev, &mt7629_data)`. No SoC-specific post-probe register writes are performed in this file.

## State And Persistence
The source owns no mutable driver state. The runtime state is hardware register state managed by the common pinctrl framework after the static `mt7629_data` descriptor is registered. `mt7629_data` indicates `gpio_m = 0`, `ies_present = true`, default register base names, rev1 bias callbacks, and rev1 drive callbacks.

## Dependencies And Integration Points
The file integrates with Linux platform driver discovery, device tree pinctrl consumers, MediaTek EINT, and generic pinconf/pinmux interfaces. `mt7629_eint_hw` defines 7 ports, AP EINT count equal to the number of pins, 16 debounce counters, and the MT2701 debounce timing table.

## Risks
Table accuracy is the main risk. The Wi-Fi group `mt7629_wf0_2g_pins` lists 9 pins but the visible `mt7629_wf0_2g_funcs` initializer has 8 entries, which is a metadata mismatch risk for group setup. As with all string-based pinctrl function tables, typos in group names would surface as device tree mux failures rather than obvious logic errors. The register maps use broad pin ranges, so one incorrect range boundary could affect multiple unrelated peripherals.

## Test Signals
Expected signals include successful compilation, successful probe for `mediatek,mt7629-pinctrl`, DTS pinctrl lookup success for Ethernet, Wi-Fi, flash, SPI, UART, I2C, PCIe, and LEDs, GPIO loopback tests for direction/value paths, EINT debounce tests, and pinconf get/set checks for pull, Schmitt, IES, drive, TDSEL, and RDSEL controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7629.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt76x8.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt76x8.c

## Purpose
`pinctrl-mt76x8.c` is an older Ralink/MTMIPS-style pinmux driver for MT76x8, MT7620-compatible, and RT2880-compatible pin controllers. Unlike the Moore drivers in this group, it does not describe per-pin register field calculators; it describes mux groups controlled by shared GPIO mode bitfields.

## Important APIs, Types, And Data
The file includes Linux module/platform/of headers and `pinctrl-mtmips.h`. It uses `struct mtmips_pmx_func` and `struct mtmips_pmx_group` through helper macros `FUNC()`, `GRP()`, and `GRP_G()`. The `MT76X8_GPIO_MODE_*` constants define bit shifts in the SoC GPIO mode register, while `MT76X8_GPIO_MODE_MASK` defines two-bit mux selectors for most groups.

Function arrays enumerate alternatives for PWM, UART, I2C, REFCLK, PERST, watchdog, SPI, SD, I2S, SPI chip-select, SPI slave, GPIO/PCIe, and Ethernet LED pins. The `mt76x8_pinmux_data` array registers each mux group with its mode mask, GPIO fallback value, shift, and available functions, ending with a zero sentinel.

## Control Flow
Runtime flow is minimal. `core_initcall_sync(mt76x8_pinctrl_init)` registers `mt76x8_pinctrl_driver`. The platform driver matches `ralink,mt76x8-pinctrl`, `ralink,mt7620-pinctrl`, and `ralink,rt2880-pinmux`. Probe calls `mtmips_pinctrl_init(pdev, mt76x8_pinmux_data)`, which is responsible for registering the pinmux provider and applying group selections.

## State And Persistence
The file owns static mux metadata only. Runtime mux state lives in the MTMIPS GPIO mode register and is manipulated by the shared MTMIPS pinctrl implementation. The `enabled` fields in the MTMIPS structs are part of the common framework state, not directly mutated by this file.

## Dependencies And Integration Points
This file integrates with the MTMIPS pinctrl subsystem rather than the MediaTek Moore v2 subsystem. It depends on platform driver matching from device tree and on the shared MTMIPS implementation to interpret group masks, shifts, and GPIO fallback values. It exports module device-table metadata for OF autoloading.

## Risks
The table packs many unrelated muxes into one global mode register, so incorrect mask/shift values can corrupt adjacent mux settings. Some groups share pins or offer debug/JTAG/UTIF alternatives, making board DTS selection important. The compatible list includes older SoCs, so behavior must remain compatible with legacy bindings and any subtle register-layout differences covered by the common MTMIPS layer.

## Test Signals
Useful tests are successful probe for all listed compatible strings, boot-time pinctrl lookup success on MT76x8 board DTS files, mux checks for UART0/1/2, SPI, I2C, SDXC, PWM, I2S/PCM, WDT, REFCLK, PCIe/PERST, and Ethernet LED groups, plus GPIO fallback tests for groups where `GRP_G()` defines an explicit GPIO value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt76x8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7981.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7981.c

## Purpose
`pinctrl-mt7981.c` describes MT7981 pin control for the MediaTek Moore framework. It provides multi-base register-field metadata, 57 pin descriptors, mux group/function tables for networking-oriented peripherals, EINT metadata, and combined bias/pull handling.

## Important APIs, Types, And Data
`MT7981_PIN()` wraps `MTK_PIN()` with EINT mux 0, EINT number equal to the pin number, and `DRV_GRP4`. Local `PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` helpers extend `PIN_FIELD_CALC()` with an explicit register base index, because MT7981 pin configuration is spread across `"gpio"`, `"iocfg_rt"`, `"iocfg_rm"`, `"iocfg_rb"`, `"iocfg_lb"`, `"iocfg_bl"`, `"iocfg_tm"`, and `"iocfg_tl"` bases.

Register calculators cover mode, direction, data input/output, SMT, IES, PU, PD, drive, PUPD, R0, and R1. `mt7981_pull_type` selects either PUPD/R1/R0 style pulls for pins 0-39 or separate PU/PD style pulls for pins 40-56. Pins include WPS/reset, watchdog, PCIe reset/wake/clkreq, JTAG and wireless-offload JTAG, USB VBUS, PWM, SPI0/1/2, UART0, MDIO, GBE interrupt/reset, and Wi-Fi front-end pins.

Function groups cover WA/WM debug, DFD, JTAG, PTA, PCM, UDI, USB, antenna select, Ethernet/MDIO/Wi-Fi modes, I2C, LEDs, PWM, SPI, UART, watchdog, flash, and PCIe.

## Control Flow
`arch_initcall(mt7981_pinctrl_init)` registers `mt7981_pinctrl_driver`. Matching uses `mediatek,mt7981-pinctrl`; probe delegates to `mtk_moore_pinctrl_probe(pdev, &mt7981_data)`. All hardware programming after probe is handled by common pinctrl operations using the supplied register tables and callbacks.

## State And Persistence
State is static descriptor data plus live SoC register state managed by the common framework. `mt7981_data` enables IES support, combined pull handling through `pull_type`, `mtk_pinconf_bias_set_combo()`, and `mtk_pinconf_bias_get_combo()`, rev1 drive callbacks, and advanced pull callbacks. The EINT block declares 7 ports, AP EINT count equal to the pin count, and 16 debounce counters.

## Dependencies And Integration Points
The file depends on accurate base-name ordering in `mt7981_pinctrl_register_base_names`, the Moore probe path, generic pinmux/pinconf APIs, MediaTek EINT, and board device trees that use the named groups/functions.

## Risks
Several visible table anomalies are risk signals: `mt7981_wa_aice_groups` references group strings such as `wm_aice1_1` and `wm_aice1_2`, while the declared group names are `wm_aice1` and `wm_aice2`; some group comments do not match group purposes; `mt7981_ant_sel_pins` lists more entries than the visible funcs array. These are likely to surface as missing pinctrl groups or bad group initialization rather than compile-time logic failures. Multi-base register indexing also makes off-by-one base selection a high-impact risk.

## Test Signals
Validation should include compile testing, successful probe for `mediatek,mt7981-pinctrl`, pinctrl lookup tests for every DTS function name, GPIO/value tests, IES/SMT tests, combo bias tests over both pull-type classes, drive-strength tests, and peripheral smoke tests for SPI flash/SNFI/eMMC, MDIO, PCIe, UART, I2C, LEDs, watchdog, USB VBUS, and Wi-Fi front-end modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7981.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7986.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7986.c

## Purpose
`pinctrl-mt7986.c` describes MT7986A and MT7986B pin controllers for the MediaTek Moore framework. It shares one register map and group/function set across two package variants, while using different pin descriptor arrays and EINT descriptors for A and B.

## Important APIs, Types, And Data
The file defines `MT7986_PIN()` for normal ballout pins and `MT7986_NOT_BALLOUT_PIN()` for MT7986B package holes. Register-base enum values identify `"gpio"`, `"iocfg_rt"`, `"iocfg_rb"`, `"iocfg_lt"`, `"iocfg_lb"`, `"iocfg_tr"`, and `"iocfg_tl"`. The comments document how these bases correspond to physical pad regions around the chip carrier.

Register calculators cover mode, direction, input/output, IES, SMT, PU, PD, drive, PUPD, R0, and R1 for pins 0-100. `mt7986_pull_type` marks pins 0-68 as PUPD/R1/R0 pull style and pins 69-100 as separate PU/PD style. `mt7986a_pins` names all 101 pads; `mt7986b_pins` intentionally marks pins 41-65 as not ballout while preserving numbering. Group/function tables expose watchdog, Wi-Fi LEDs, I2C, UART alternatives, SPI, PWM, eMMC, SNFI, PCIe, Ethernet MDIO/switch interrupt, PCM/I2S, and Wi-Fi front-end modes.

## Control Flow
Two platform drivers are registered at arch init: `mt7986a-pinctrl` and `mt7986b-pinctrl`. The compatible strings are `mediatek,mt7986a-pinctrl` and `mediatek,mt7986b-pinctrl`. Each probe calls `mtk_moore_pinctrl_probe()` with the matching SoC descriptor.

## State And Persistence
The file maintains no dynamic state. Runtime state is hardware register state owned by the common pinctrl operations. The A and B descriptors share `mt7986_reg_cals`, `mt7986_groups`, and `mt7986_functions`, but differ in `pins`, `npins`, and EINT hardware pointer. Both descriptors enable IES and combo bias handling, rev1 drive callbacks, and advanced pull callbacks.

## Dependencies And Integration Points
Integration points are the Moore pinctrl core, multiple IO configuration register resources named in device tree, MediaTek EINT, and board DTS pinctrl groups. The MT7986B not-ballout placeholders are an important package integration mechanism because they keep pin numbers stable while preventing named use of unavailable pads.

## Risks
The shared group table includes groups for pads that are not ballout on MT7986B; the common framework and board DTS must avoid selecting unavailable package pins. Some visible group metadata has array-length concerns, for example Wi-Fi 2G pin/function arrays appear uneven. Multi-base register maps raise the cost of incorrect base indices, and package-specific testing must ensure that A and B compatible strings do not accidentally expose invalid pads.

## Test Signals
Test signals include successful registration of both platform drivers, probe success for both compatibles, no DTS selection of `NULL` MT7986B pads, GPIO and EINT tests over available pins, combo bias tests across both pull types, drive-strength tests, and peripheral smoke tests for eMMC, SNFI, SPI, UART, I2C, PCIe reset/wake/clkreq, MDIO, switch interrupt, PCM/I2S, LEDs, watchdog, and Wi-Fi groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7986.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7988.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7988.c

## Purpose
`pinctrl-mt7988.c` describes MT7988 pin control for the MediaTek Moore pinctrl framework. It maps 84 pins across several IO configuration register pages and provides extensive mux metadata for Ethernet, PCIe, flash, UART, JTAG, I2C, LEDs, USB, audio, and debug functions.

## Important APIs, Types, And Data
The file defines `enum mt7988_pinctrl_reg_page` for `"gpio"`, `"iocfg_tr"`, `"iocfg_br"`, `"iocfg_rb"`, `"iocfg_lb"`, and `"iocfg_tl"` register pages. `MT7988_PIN()` wraps `MTK_PIN()` with EINT mux 0, EINT number equal to the pin number, and drive group `DRV_GRP4`. `PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` provide explicit register-base selection for field calculators.

Register calculators cover mode, direction, data input/output, IES, SMT, PU, PD, drive, PUPD, R0, and R1. `mt7988_pull_type` mixes PUPD/R1/R0, separate PU/PD, and PD-only pull models depending on pin. Pin descriptors name UARTs, SMI/MDIO, PCIe wake/clkreq/perst, watchdog, PMIC/I2C, SPI0/1/2, eMMC, PCM/I2S, JTAG, USB VBUS, Ethernet LEDs, GPIO, and UART1/2 pads.

The group table is broad: TOPS/WO JTAG, DFD, many I2C and PHY-I2C aliases, MDIO, PCIe sideband and PHY I2C pins, PMIC, watchdog, SPI, SNFI/eMMC/SD, UART/TOPS UART/WO UART, UDI, I2S/PCM, Ethernet LEDs, PWM, and USB VBUS. `mt7988_functions` exports audio, jtag, int_usxgmii, pwm, dfd, i2c, eth, pcie, pmic, watchdog, spi, flash, uart, udi, usb, and led functions.

## Control Flow
`arch_initcall(mt7988_pinctrl_init)` registers the `mt7988-pinctrl` platform driver. It matches `mediatek,mt7988-pinctrl`, then `mt7988_pinctrl_probe()` delegates to `mtk_moore_pinctrl_probe(pdev, &mt7988_data)`.

## State And Persistence
The file owns static tables only. Live pin state persists in hardware registers through common pinctrl operations. `mt7988_data` enables IES, combo bias callbacks, rev1 drive callbacks, advanced pull callbacks, and EINT metadata with 7 ports and 16 debounce counters.

## Dependencies And Integration Points
The driver depends on exact register-base resource ordering, shared Moore pinctrl logic, MediaTek EINT, generic pinconf/pinmux APIs, and DTS references to the published function/group strings. Its multi-base register mapping is central to pinconf correctness.

## Risks
Several string-table hazards are visible: duplicate group names appear in `mt7988_groups` such as repeated `tops_uart0_0` and repeated `net_wo*_uart_txd_0` names for later pin alternatives; `mt7988_uart_groups` references `ops_uart0_1` and `ops_uart1_1`, while the declared names are `tops_uart0_1` and `tops_uart1_1`; `mt7988_led_groups` references `wf5g_led0` and `wf5g_led1`, which are not present in the visible group table. These can cause runtime pinctrl lookups to fail even if the file compiles. Multi-base field offsets and mixed pull models are additional high-risk areas.

## Test Signals
Testing should include build coverage, boot-time probe success, DTS pinctrl lookup tests for all exported function names, GPIO direction/value tests, EINT debounce tests, combo-bias tests for PUPD, PU/PD, and PD-only pins, drive-strength tests, and hardware smoke tests for PCIe sideband signals, MDIO, Ethernet LEDs, SPI/SNFI/eMMC/SD, UART/TOPS UART, I2C/PHY I2C, watchdog, PMIC, USB VBUS, PCM/I2S, and debug/JTAG groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7988.c -->
