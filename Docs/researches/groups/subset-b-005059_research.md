# subset-b-005059 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt2712.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt2712.h

## Purpose

`pinctrl-mtk-mt2712.h` is the static pin descriptor table for the MediaTek MT2712 pin controller driver. It defines `mtk_pins_mt2712[]`, a 210-entry `static const struct mtk_desc_pin` array covering pins 0 through 209. Each entry binds a Linux pin number and human-readable pad name to EINT metadata and the mux values that the older MediaTek common pinctrl driver can select.

This file contains descriptor data only. It does not implement executable control flow by itself, but it is included by `pinctrl-mt2712.c`, whose `mt2712_pinctrl_data` passes this table to `mtk_pctrl_common_probe`.

## Important APIs, Types, And Data

The table uses the older `pinctrl-mtk-common.h` descriptor API:

- `MTK_PIN(PINCTRL_PIN(number, name), pad, chip, eint, functions...)` expands into one `struct mtk_desc_pin`.
- `PINCTRL_PIN()` supplies the pinctrl core-visible pin number and pin name.
- `MTK_EINT_FUNCTION(eintmux, eintnum)` records the mux value and external interrupt number for a pin, or `NO_EINT_SUPPORT`.
- `MTK_FUNCTION(muxval, name)` describes one mux selector option. MT2712 uses mux values 0 through 7, with value 0 consistently representing GPIO mode.

The table has 210 `MTK_PIN` entries, 901 `MTK_FUNCTION` descriptors, and 210 EINT descriptors. The first pins are named `EINT0` through `EINT3`, then PWM, USB VBUS/ID, keypad, camera clocks, PCM, NAND, MSDC, Ethernet, UART, I2C, SPI, JTAG, display, audio, and PCIe-oriented pads. The final entries are `PERSTB_P0`, `CLKREQN_P0`, `WAKEEN_P0`, `PERSTB_P1`, `CLKREQN_P1`, and `WAKEEN_P1`.

## Control Flow And Runtime Use

At build time this header contributes `mtk_pins_mt2712[]` to `pinctrl-mt2712.c`. At probe time the platform driver matching `mediatek,mt2712-pinctrl` passes `mt2712_pinctrl_data` to `mtk_pctrl_common_probe`; that devdata references this header's pin table and companion arrays in the `.c` file for drive strength, pull-up/down, input-enable, and Schmitt-trigger handling.

At runtime the generic MediaTek pinctrl callbacks use the pin table to expose pins, groups, mux functions, GPIO mode, and EINT mapping to the Linux pinctrl, GPIO, and interrupt subsystems. Device-tree pinctrl states select function names or mux values; the common driver translates those choices into mode register writes using the register offsets and masks provided by the MT2712 `.c` file.

## State And Persistence Behavior

The header stores immutable static descriptor data. It has no heap allocation, no reference-counting, no file-backed persistence, and no direct hardware state. Runtime state lives in the common driver structures created at probe and in the hardware registers programmed through regmap. The only long-lived effect of this header is the compiled-in pin capability map that determines which mux/EINT configurations the driver will accept.

## Dependencies And Integration Points

Direct dependencies are `<linux/pinctrl/pinctrl.h>` and `pinctrl-mtk-common.h`. The header depends on the semantics of `struct mtk_desc_pin`, `struct mtk_desc_function`, and `struct mtk_desc_eint`.

The main integration point is `pinctrl-mt2712.c`, where `mt2712_pinctrl_data` sets `.pins = mtk_pins_mt2712`, `.npins = ARRAY_SIZE(mtk_pins_mt2712)`, EINT hardware properties, and older common-driver register offsets. The companion driver registers via `arch_initcall`, uses `mtk_pctrl_common_probe`, and wires EINT suspend/resume through `mtk_eint_pm_ops`.

## Risks And Edge Cases

The table is hardware-contract data, so most risks are silent misconfiguration rather than local crashes. Wrong mux names or mux values can route a peripheral to the wrong pad. Wrong EINT numbers can break wakeup or interrupt delivery. Pads with `NO_EINT_SUPPORT` must stay aligned with hardware and device-tree expectations. Because the table is positional and large, accidental insertion, deletion, or renumbering can desynchronize pin numbers from companion drive-strength and special pull arrays in `pinctrl-mt2712.c`.

Another risk is duplicate or unexpected function naming. Device-tree users and debugfs output rely on stable function names such as `MSDC*`, `I2C*`, `SPI*`, `GBE*`, `TDM*`, and debug monitor functions. Renaming a function is a binding-visible change even when the numeric mux value is unchanged.

## Test Signals

Useful validation signals include successful kernel build of the MT2712 pinctrl driver, boot-time probe of `mediatek,mt2712-pinctrl`, no pinctrl lookup failures for board DTS pin states, and debugfs pin listings showing 210 pins with expected names and mux options. Hardware tests should cover GPIO direction/value, pinmux for major buses such as MSDC, I2C, SPI, UART, Ethernet, display/audio, and EINT trigger/wakeup paths. Regression checks should compare `ARRAY_SIZE(mtk_pins_mt2712)` with `.npins`, confirm pin numbers remain contiguous 0-209, and spot-check EINT numbering against the SoC datasheet and DTS users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt2712.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6397.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6397.h

## Purpose

`pinctrl-mtk-mt6397.h` describes the 41 GPIO-capable pins exposed by the MediaTek MT6397 PMIC pin controller. It defines `mtk_pins_mt6397[]`, a `static const struct mtk_desc_pin` array used by the MT6397 pinctrl platform driver to expose PMIC pins to Linux pinctrl and GPIO consumers.

Unlike the application-processor SoC tables in this directory, this table is for an MFD child of the MT6397 PMIC. The companion `.c` driver obtains the parent `mt6397_chip` regmap and calls `mtk_pctrl_init` with this descriptor table and PMIC register offsets.

## Important APIs, Types, And Data

The file uses the older `pinctrl-mtk-common.h` descriptor interface:

- `MTK_PIN(PINCTRL_PIN(number, name), pad, "mt6397", eint, functions...)` creates one `struct mtk_desc_pin`.
- `MTK_EINT_FUNCTION()` records external interrupt support. The table has 41 EINT descriptors, 25 real EINT-capable pins, and 16 `NO_EINT_SUPPORT` pins.
- `MTK_FUNCTION()` lists mux options. The table contains 209 function descriptors using mux values 0 through 7.

Pins 0-11 cover PMIC interrupt, source-voltage enable, clock/event, SPI, and audio signals. Pins 12-36 cover keypad columns/rows, PWM, I2C, and EINT alternate functions. Pins 37-40 expose HDMI/DDC/hotplug/CEC style functions. GPIO mode is represented as mux value 0 for every pin.

## Control Flow And Runtime Use

This header is included by `pinctrl-mt6397.c`. During `mt6397_pinctrl_probe`, the driver gets the parent PMIC object with `dev_get_drvdata(pdev->dev.parent)` and passes `mt6397->regmap` plus `mt6397_pinctrl_data` into `mtk_pctrl_init`.

The common pinctrl code then uses this table to register PMIC pins, enumerate per-pin functions, resolve GPIO requests, and apply pinmux or pinconf operations through the PMIC regmap. Because this is an MFD child, register I/O does not go through an MMIO resource owned by the pinctrl device; it goes through the parent regmap with offsets rooted at `MT6397_PIN_REG_BASE`.

## State And Persistence Behavior

The header is immutable descriptor data. It stores no runtime state and performs no writes. Hardware state is persisted only in the MT6397 register map after the common driver writes direction, pull enable/select, data out, and pinmux registers. The descriptor table controls what the driver considers valid, but it does not cache the resulting register values.

## Dependencies And Integration Points

Direct dependencies are `<linux/pinctrl/pinctrl.h>` and `pinctrl-mtk-common.h`. The companion driver also depends on `<linux/mfd/mt6397/core.h>` to access the parent PMIC regmap.

Key integration points are the `mediatek,mt6397-pinctrl` compatible, `mt6397_pinctrl_data`, and the PMIC register offsets in `pinctrl-mt6397.c`. That data marks input-enable and Schmitt-trigger offsets as `MTK_PINCTRL_NOT_SUPPORT`, so generic pin configuration requests for those features should fail rather than touching unsupported registers.

## Risks And Edge Cases

The table is small but binding-sensitive. EINT mappings begin at pin 12 with mux value 2 and non-contiguous EINT numbers that must agree with PMIC interrupt wiring. Incorrect mapping can break keypad, hotplug, or wake-related use cases. GPIO and special function names are consumed by DTS pinctrl states and by debug tools, so renaming can break existing boards.

Because the register base is a PMIC regmap, an incorrect descriptor can drive pins that may be involved in power sequencing, clocks, or HDMI/CEC behavior. Unsupported input-enable and Schmitt controls are explicitly marked in the `.c` data; tests should ensure this header does not imply those capabilities indirectly through function naming.

## Test Signals

Validation signals include successful probe of the `mediatek-mt6397-pinctrl` MFD child, successful GPIO requests for pins 0-40, and expected pinctrl debugfs output for `INT`, SPI, audio, keypad, PWM, I2C, HDMI, hotplug, and CEC pins. Tests should exercise PMIC-backed register writes through regmap, verify unsupported input-enable/Schmitt requests fail cleanly, and confirm EINT-capable pins 12-36 can trigger interrupts with the documented mux setting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6397.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6765.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6765.h

## Purpose

`pinctrl-mtk-mt6765.h` defines the pin descriptor table for the MediaTek MT6765 Paris-generation pinctrl driver. It contributes `mtk_pins_mt6765[]`, a 180-entry `struct mtk_pin_desc` array covering GPIO0 through GPIO179. Each descriptor gives the Paris common driver the pin number, name, EINT mapping, drive group class, and mux-function list for that pin.

The file is descriptor-only and is included by `pinctrl-mt6765.c`, which supplies the register field calculators and platform-driver registration for `mediatek,mt6765-pinctrl`.

## Important APIs, Types, And Data

This header uses `pinctrl-paris.h` and the v2 common data model:

- `MTK_PIN(number, name, eint, drv_n, functions...)` expands into `struct mtk_pin_desc`.
- `MTK_EINT_FUNCTION(eint_m, eint_n)` fills `struct mtk_eint_desc`.
- `DRV_GRP0` and `DRV_GRP4` classify drive-strength handling. The table uses 175 pins in `DRV_GRP4` and 5 pins in `DRV_GRP0`.
- `MTK_FUNCTION(muxval, name)` lists mux options. MT6765 uses mux values 0 through 7, and mux value 0 is GPIO mode.

The table has 180 `MTK_PIN` descriptors and 836 function descriptors. It exposes peripheral families including UART, clock monitor outputs, modem interrupt and UART pins, I2S/audio, SPI and SCP SPI, keypad rows/columns, MSDC, MIPI, antenna selection, connectivity, BPI, JTAG, PWM, and debug monitor functions. EINT data has 180 entries, with 114 real EINT mappings and 66 `NO_EINT_SUPPORT` entries.

## Control Flow And Runtime Use

`pinctrl-mt6765.c` includes this header and sets `.pins = mtk_pins_mt6765`, `.npins = ARRAY_SIZE(mtk_pins_mt6765)`, and `.ngrps = ARRAY_SIZE(mtk_pins_mt6765)` in `mt6765_data`. The platform driver matches `mediatek,mt6765-pinctrl` and probes through `mtk_paris_pinctrl_probe`.

The Paris common driver builds pin groups from the descriptors, resolves mux selectors from the per-pin function arrays, and uses the `.reg_cal` tables in the `.c` file for MODE, DIR, DI, DO, SMT, PD, PU, TDSEL, RDSEL, DRV, PUPD, R0, R1, and IES fields. The header supplies the semantic pin/function choices; the `.c` file supplies how those choices map to register addresses and bits.

## State And Persistence Behavior

The header stores compile-time static descriptor data and no mutable state. The function arrays are compound literals embedded in each `MTK_PIN` initializer and are consumed as read-only capability descriptions. Runtime state is maintained by the Paris pinctrl instance, GPIO chip, EINT subsystem, and hardware registers across the named IO configuration bases.

## Dependencies And Integration Points

The direct dependency is `pinctrl-paris.h`, which brings in `pinctrl-mtk-common-v2.h`, Linux pinctrl/pinmux/pinconf headers, and EINT support. The key companion integration is `pinctrl-mt6765.c`, whose `mt6765_pinctrl_register_base_names` are `iocfg0` through `iocfg7` and whose `mt6765_eint_hw` advertises 160 AP EINTs, 6 ports, and 13 debounce counters.

The SoC data uses generic Paris helpers such as `mtk_pinconf_bias_set_combo`, `mtk_pinconf_drive_set_raw`, and advanced pull helpers. Device trees must provide compatible pinctrl nodes with the expected base resources and function names that match this table.

## Risks And Edge Cases

The biggest risk is mismatch between this semantic table and the register calculators in `pinctrl-mt6765.c`. Pin numbers, drive groups, and EINT numbers must stay aligned with field ranges. Pins 176-178 are named GPIO-only and have `NO_EINT_SUPPORT`; pin 179 has EINT 151, so tail-end EINT coverage is not simply contiguous. Some mux lists omit certain numeric mux values, which is valid but easy to misread during edits.

Function names are binding-facing strings used by DTS pinctrl states and debug output. A typo in a bus name such as `SCP_SPI`, `MSDC`, `CONN`, `ANT_SEL`, `BPI_BUS`, or `DBG_MON` can make an otherwise correct numeric mux inaccessible by name. Incorrect drive group assignment can produce wrong electrical drive-strength behavior even when muxing works.

## Test Signals

Test signals include a clean build, successful `mt6765-pinctrl` probe, debugfs showing 180 pins/groups, and valid pinmux application for UART, SPI, I2S, keypad, MSDC, connectivity, and debug monitor states used by board DTS files. EINT tests should cover both real mappings and `NO_EINT_SUPPORT` rejection. Pinconf tests should cover bias combo, raw drive strength, advanced pull fields, and register-base selection across `iocfg0` through `iocfg7`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6765.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6779.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6779.h

## Purpose

`pinctrl-mtk-mt6779.h` is the MT6779 pin descriptor table for the MediaTek Paris pinctrl framework. It defines `mtk_pins_mt6779[]`, a 210-entry `static const struct mtk_pin_desc` array covering GPIO0 through GPIO209. Each entry records the pin's EINT mapping, drive group, and mux-function set.

The header is paired with `pinctrl-mt6779.c`, which provides register field ranges, EINT hardware sizing, base-name mapping, and platform-driver registration for `mediatek,mt6779-pinctrl`.

## Important APIs, Types, And Data

The table uses the Paris `MTK_PIN` API:

- `MTK_PIN(number, "GPIOx", MTK_EINT_FUNCTION(...), DRV_GRPn, MTK_FUNCTION(...))` creates a `struct mtk_pin_desc`.
- `MTK_EINT_FUNCTION(0, eint_number)` maps pins to AP EINT lines; unsupported pins use `NO_EINT_SUPPORT`.
- `DRV_GRP4` is used for most pins, while 6 pins use `DRV_GRP0`.
- `MTK_FUNCTION()` lists mux values 0 through 7, with GPIO mode at 0.

The file contains 210 pin descriptors and 1019 function descriptors. It has broad peripheral coverage: SPI, connectivity, JTAG, BPI, SCP, MSDC, I2S, antenna selection, modem, DPI/MIPI/display, TDM/PCM/audio, UART, keypad, PWM, and debug monitor signals. EINT coverage is high: 194 real mappings and 16 unsupported entries.

## Control Flow And Runtime Use

At probe, `pinctrl-mt6779.c` passes `mtk_pins_mt6779` through `mt6779_data` into `mtk_paris_pinctrl_probe`. The Paris driver uses this table to create one group per pin, expose the per-pin mux functions, and resolve pinconf or pinmux requests from device-tree states.

The companion `.c` file supplies register calculators for MODE, DIR, DI, DO, SMT, IES, PU, PD, DRV, PUPD, R0, and R1. Its base names are `gpio`, `iocfg_rm`, `iocfg_br`, `iocfg_lm`, `iocfg_lb`, `iocfg_rt`, `iocfg_lt`, and `iocfg_tl`; this header's pin numbers are the lookup keys into those ranges.

## State And Persistence Behavior

This header is read-only compiled-in capability data. It does not allocate memory, persist configuration, or write registers. Runtime changes happen when pinctrl and GPIO callbacks program SoC registers through the Paris common driver. The pin/function/EINT descriptors constrain which operations are accepted and how names resolve to mux values.

## Dependencies And Integration Points

The direct include is `pinctrl-paris.h`. Integration is through `pinctrl-mt6779.c`, whose `mt6779_data` sets `.ies_present = true`, 195 AP EINTs, 6 EINT ports, 13 debounce counters, and generic combo bias/raw drive/advanced pull operations.

Device-tree integration depends on the `mediatek,mt6779-pinctrl` compatible and on pin/function names matching DTS pinctrl states. EINT integration depends on `mtk_build_eint` and the EINT hardware description from the `.c` file.

## Risks And Edge Cases

The table has some tail entries where mux value 0 is represented as `NULL` rather than a printable GPIO function name. That may be intentional for reserved pins, but it is a notable debugfs and lookup edge case. EINT numbering is mostly dense but not identical to pin numbering near the end, so automated assumptions about `pin == eint` would be wrong.

Large mux lists increase risk of typographical binding regressions. The `.h` table and `.c` register calculators must agree on pin range coverage through GPIO209; otherwise pinctrl may expose a valid function but fail to program the corresponding field. Drive group misclassification can lead to wrong current limits, and incorrect EINT entries can break wakeup-capable GPIOs.

## Test Signals

Expected test signals are successful build/probe for `mt6779-pinctrl`, debugfs enumeration of 210 pins, no missing register-range warnings when applying pin states, and working mux for common DTS users such as SPI, I2S, MSDC, display, connectivity, and modem interfaces. EINT tests should include late-numbered pins such as GPIO206-GPIO209, while debugfs or pinmux self-checks should verify that `NULL` function names do not break function enumeration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6779.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6795.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6795.h

## Purpose

`pinctrl-mtk-mt6795.h` defines the MT6795 pin descriptor table for the MediaTek Paris pinctrl driver. It exports `mtk_pins_mt6795[]`, a 197-entry `static const struct mtk_pin_desc` array for GPIO0 through GPIO196. The table records each pin's EINT line, drive-strength class, and mux-function options.

The companion `pinctrl-mt6795.c` provides the register layout, pull-type table, EINT hardware data, and platform-driver registration that consume this descriptor table.

## Important APIs, Types, And Data

The descriptor API comes from `pinctrl-paris.h`:

- `MTK_PIN(number, name, eint, drv_n, functions...)` creates each `struct mtk_pin_desc`.
- `MTK_EINT_FUNCTION(0, n)` maps all 197 pins to real EINT lines 0-196 in this table.
- `DRV_FIXED`, `DRV_GRP0`, `DRV_GRP2`, and `DRV_GRP4` classify drive-strength behavior. The distribution is 6 fixed-drive pins, 54 `DRV_GRP0` pins, 91 `DRV_GRP2` pins, and 46 `DRV_GRP4` pins.
- `MTK_FUNCTION()` records mux options. MT6795 uses mux values 0 through 6 in this header.

The table has 698 function descriptors. Function families include BPI, MSDC, I2S/audio, modem, SPI, DPI/display, JTAG, PWM, LTE, PCM, SIM, UART, DSI/MIPI, camera clocks, and debug/test functions. GPIO mode remains mux value 0.

## Control Flow And Runtime Use

`pinctrl-mt6795.c` includes this file and assigns `.pins = mtk_pins_mt6795`, `.npins = ARRAY_SIZE(mtk_pins_mt6795)`, and `.ngrps = ARRAY_SIZE(mtk_pins_mt6795)` in `mt6795_data`. `mtk_paris_pinctrl_probe` uses the descriptors to register pins/groups and to resolve mux requests.

The `.c` file provides register calculators for MODE, DIR, DI, DO, SR, SMT, DRV, PUPD, R0, R1, IES, PULLEN, and PULLSEL. It also supplies `mt6795_pull_type[]`, which differentiates `MTK_PULL_PULLSEL_TYPE` and `MTK_PULL_PUPD_R1R0_TYPE` per pin. The header's pin ordering is therefore tied to both register calculators and the pull-type array.

## State And Persistence Behavior

The file contains only immutable compiled-in descriptors. Runtime pin state is not stored in this header; it is programmed into hardware registers through Paris pinctrl operations. The driver may read back register state for pinconf queries, but this header remains the static capability map.

## Dependencies And Integration Points

The direct dependency is `pinctrl-paris.h`. The companion driver matches `mediatek,mt6795-pinctrl`, uses the default single `"base"` register name, advertises 224 AP EINTs with 7 ports and 32 debounce counters, and enables Paris PM ops via `mtk_paris_pinctrl_pm_ops`.

The SoC data uses rev1 bias and drive helpers (`mtk_pinconf_bias_*_rev1`, `mtk_pinconf_drive_*_rev1`) plus combo and advanced pull helpers. Because this table supplies all EINT mappings, it is central to GPIO interrupt and wakeup behavior for MT6795 boards.

## Risks And Edge Cases

MT6795 has more varied drive groups and pull types than the simpler Paris tables. Descriptor edits must stay synchronized with `mt6795_pull_type[]`, the register-range arrays, and drive group expectations. All pins declare real EINT support, so an incorrect EINT number is especially likely to cause subtle interrupt routing bugs rather than a clean unsupported error.

The table uses mux values only through 6, unlike many neighboring SoCs that use 0 through 7. Adding a function at value 7 without hardware support would expose invalid pinmux states. Function-string stability matters for DTS users of modem, BPI, display, storage, and audio pins.

## Test Signals

Validation should include successful `mt6795-pinctrl` probe, debugfs enumeration of 197 pins, pinmux coverage for storage, display, modem, SPI, UART, SIM, I2S/PCM, and PWM use cases, and GPIO interrupt tests across low, middle, and high pin numbers. Pinconf tests should cover rev1 bias disable/set/get, pull-select versus PUPD/R0/R1 pins, slew-rate fields, and drive-strength values for `DRV_FIXED`, `DRV_GRP0`, `DRV_GRP2`, and `DRV_GRP4`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6795.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6797.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6797.h

## Purpose

`pinctrl-mtk-mt6797.h` defines the MT6797 pin descriptor table for the MediaTek Paris pinctrl framework. It contributes `mtk_pins_mt6797[]`, a 262-entry `static const struct mtk_pin_desc` array covering GPIO0 through GPIO261. Each entry provides the pin name, EINT descriptor, drive group, and mux-function alternatives.

The header is included by `pinctrl-mt6797.c`, which is based on the MT6765 driver but supplies a much smaller pin configuration register model for MT6797.

## Important APIs, Types, And Data

This file uses the Paris descriptor macros:

- `MTK_PIN(number, "GPIOx", MTK_EINT_FUNCTION(...), DRV_GRP3, functions...)` creates each pin descriptor.
- Every entry uses `DRV_GRP3`, so the table has a uniform drive-strength class.
- Every EINT descriptor is `MTK_EINT_FUNCTION(NO_EINT_SUPPORT, NO_EINT_SUPPORT)`. The table has no real EINT-capable pins, even though many mux function names contain `EINT` as peripheral signal names.
- `MTK_FUNCTION()` supplies mux values 0 through 7, with GPIO mode at 0.

The table contains 262 pins and 1099 function descriptors. It heavily covers camera/MIPI CSI, debug monitor, SPI, connectivity, C2K, BPI, JTAG, modem, MSDC, DPI/display, I2S/audio, UART, PCM, antenna selection, clock monitor, SCP, and LTE/DFD debug functions. The final pins are JTAG-oriented GPIO257-GPIO261.

## Control Flow And Runtime Use

`pinctrl-mt6797.c` assigns this table to `mt6797_data` and probes through `mtk_paris_pinctrl_probe` for `mediatek,mt6797-pinctrl`. The Paris driver uses the descriptors to expose the pins and per-pin function lists.

Unlike MT6765/MT6779/MT6795, the companion `.c` file only provides register calculators for MODE, DIR, DI, and DO. It names five register bases: `gpio`, `iocfgl`, `iocfgb`, `iocfgr`, and `iocfgt`. Therefore this header's mux information is available, but advanced pinconf features such as bias, drive, input-enable, and Schmitt are not described by MT6797 register calculators in this driver.

## State And Persistence Behavior

The header is static descriptor data and contains no mutable runtime state. Runtime state is limited to the Paris pinctrl device, GPIO chip state, and hardware mode/direction/data registers. Because EINT support is absent in this table and no EINT hardware data is provided in `mt6797_data`, interrupt state is not built from this header.

## Dependencies And Integration Points

The direct include is `pinctrl-paris.h`. Integration occurs through `pinctrl-mt6797.c`, whose SoC data sets `.pins`, `.npins`, `.ngrps`, `.gpio_m = 0`, and base-name metadata but does not set `.eint_hw` or pinconf operation hooks.

Device-tree pinctrl states must use names and mux choices from this table. Since many functions are high-speed or debug signals, board DTS files need to match the exact pad capabilities. The absence of EINT support should be reflected in board designs that require GPIO interrupts.

## Risks And Edge Cases

The key edge case is that function names include `EINT`-looking peripheral names such as C2K-related signals, but the actual `struct mtk_eint_desc` values are all `NO_EINT_SUPPORT`. Consumers must not infer Linux GPIO interrupt support from function-string names.

Another risk is overexposing pinconf expectations. The header contains drive group values, but the companion driver only registers MODE, DIR, DI, and DO register calculators and no explicit drive/bias callbacks. Tests should verify unsupported pinconf requests fail cleanly. With 262 pins and many mux alternatives, typographical errors in function strings or pin-number alignment errors can affect camera, display, modem, connectivity, and debug interfaces.

## Test Signals

Validation signals include a clean build, successful `mt6797-pinctrl` probe, debugfs enumeration of 262 pins/groups, and correct GPIO mode/direction/data behavior for low and high pin numbers. Pinmux tests should focus on camera/MIPI CSI, SPI, MSDC, display DPI, audio/I2S, UART, connectivity, and JTAG/debug pins. Negative tests should confirm GPIO-to-IRQ/EINT requests are unsupported and that bias/drive/Schmitt/input-enable pinconf operations are not falsely advertised by this SoC data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6797.h -->
