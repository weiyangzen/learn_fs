# subset-b-005062 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8195.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8195.h

## Purpose
This header is the MT8195 SoC pin description table for the MediaTek Paris pinctrl framework. It includes `pinctrl-paris.h` and defines `static const struct mtk_pin_desc mtk_pins_mt8195[]`, a contiguous 165-pin catalogue from GPIO0 through GPIO164. Each entry binds a Linux pin number/name to its EINT line, drive group, and legal mux values. The table is consumed by an MT8195 platform driver through an `mtk_pin_soc` descriptor in companion code, then the shared Paris driver builds one pinctrl group per pin and validates devicetree `pinmux` function numbers against this per-pin function list.

## Important APIs, Types, And Data
The file is data-only and exports no functions. It relies on Paris macros:

- `MTK_PIN(number, name, eint, drv_n, ...)` to initialize `struct mtk_pin_desc`.
- `MTK_EINT_FUNCTION(instance, number)` to connect pins to external interrupt routing.
- `MTK_FUNCTION(muxval, name)` to declare alternate functions.
- `DRV_GRP4` and `DRV_FIXED` from the common v2 drive-strength group enum.

The table covers high-density multimedia and platform I/O functions: MSDC0/MSDC2, SPI, I2C, UART, PWM, TDM/I2S, DMIC, DPI/DGI display pins, GBE pins, SCP/SSPM/MD32 sideband GPIOs, debug monitor functions, PCIe/USB sideband signals, and clock outputs. Most pins use `DRV_GRP4`; the final fixed/special pins use `DRV_FIXED` and often expose only `MTK_FUNCTION(0, NULL)`.

## Control Flow And Integration
There is no executable control flow in this header. At runtime the flow is indirect: a board devicetree supplies encoded `pinmux` cells, `mtk_pctrl_dt_subnode_to_map()` in `pinctrl-paris.c` decodes pin/function numbers, and `mtk_pctrl_is_function_valid()` walks the `funcs` array in this table before allowing a mux map. `mtk_pmx_set_mux()` later writes `PINCTRL_PIN_REG_MODE` using the selected `muxval`. GPIO request paths switch the same pin to `soc->gpio_m`, and GPIO/IRQ operations use the `eint` descriptors from this file.

## State And Persistence
The header has no mutable state. Its data is compiled into kernel text/rodata. Runtime state lives in the shared Paris `struct mtk_pinctrl`, gpiochip registration, EINT controller state, and hardware registers. Pin mux, direction, bias, input enable, and drive strength persist only as SoC register values until reset or suspend/resume restoration by platform code.

## Dependencies
The table depends on the Paris/common-v2 schema matching the SoC driver's register calculators. The number of table entries must match `npins`, and pin numbers are assumed to be valid indexes by Paris code paths such as `hw->soc->pins[pin]`. EINT values must match MT8195 interrupt-controller wiring and devicetree binding expectations.

## Risks
The main risk is silent board malfunction from table inaccuracies: an incorrect mux value can route a peripheral to the wrong pad; an incorrect EINT number can break interrupts or wake sources; an incorrect drive group can expose invalid drive-strength behavior. Pins near the end of the table with `NULL` function names are intentionally limited, but they are risky because debug output and function validation must tolerate unnamed function zero. Because Paris uses one pin per group, any non-contiguous or duplicate pin number would corrupt group creation; this file appears contiguous from 0 to 164.

## Test Signals
Useful tests are DT binding compilation for MT8195 pinmux cells, boot probing of the companion MT8195 pinctrl driver, `debugfs` pinctrl dumps via `mtk_pctrl_show_one_pin()`, GPIO request/direction tests on representative pins, peripheral smoke tests for MSDC/I2C/SPI/UART/audio/display/GBE functions, and IRQ/debounce tests for EINT-backed pins. Build coverage should include `COMPILE_TEST` or MT8195 defconfig coverage so macro/schema drift is caught.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8195.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8196.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8196.h

## Purpose
This header provides the MT8196 pin and EINT description data for the MediaTek Paris pinctrl framework. It defines `mtk_pins_mt8196[]` with 293 contiguous pin descriptors, GPIO0 through virtual EINT-style pins `veint292`, and a matching `eint_pins_mt8196[]` table with 293 `MTK_EINT_PIN()` entries. The data lets the shared Paris driver expose MT8196 pins to the Linux pinctrl, pinmux, pinconf, GPIO, and EINT subsystems.

## Important APIs, Types, And Data
The file is data-only. It depends on `pinctrl-paris.h`, `struct mtk_pin_desc`, and `struct mtk_eint_pin`. `EINT_INVALID_BASE` is defined as `0xff` and used in the EINT table for pins without a valid EINT backing instance. The pin table uses `MTK_PIN`, `MTK_EINT_FUNCTION`, `MTK_FUNCTION`, and `DRV_GRP4`; unlike MT8195 there are no fixed drive groups in the scanned table.

Function coverage is broad: touchscreen always-on pins, display PWM/DSI/DP, SPI/I2C/UART, DMIC and FMI2S audio, MD/MD32/SCP/SSPM/ADSP/SPU control pins, GPS, BPI modem signals, CONN/UDI/debug monitor functions, PCIe sideband, and dual GBE groups. Pins 271 through 292 are named `veint*` and expose only function zero with a `NULL` function name, representing interrupt-only or virtual pin entries rather than normal muxable pads.

## Control Flow And Integration
The runtime flow is mediated entirely by the Paris common driver. During probe, the MT8196 companion driver supplies this table through `device_get_match_data()` as part of `struct mtk_pin_soc`. Paris builds one group per pin, registers pinctrl, enables it, builds EINT with `mtk_build_eint()`, and then registers the gpiochip. Devicetree `pinmux` cells are validated against each pin's `funcs` list before `PINCTRL_PIN_REG_MODE` writes are issued. GPIO-to-IRQ and debounce requests use `desc->eint.eint_n`, while the more detailed `eint_pins_mt8196[]` table maps logical EINT pins to EINT instances, indexes, and debounce support.

## State And Persistence
The header contains immutable compile-time SoC data. Runtime state is held in the Paris `struct mtk_pinctrl`, `struct mtk_eint`, gpiochip state, and hardware register fields. EINT mapping is not persisted outside the kernel image; selected mux and GPIO states persist as hardware register state until reset, suspend handling, or explicit reconfiguration.

## Dependencies
The pin table and EINT table must remain index-aligned with the SoC's `npins`. Paris code indexes `hw->soc->pins[pin]` directly, so gaps or duplicate numbers would be unsafe. The companion SoC driver must provide register calculators for mode, direction, input/output, bias, drive, and EINT registers that cover all real and virtual pins. Devicetree bindings must use mux values no larger than the Paris `func0` through `func15` function namespace.

## Risks
The highest risk is mismatched EINT metadata: `EINT_INVALID_BASE` correctly marks unsupported lines, but a wrong instance/index/debounce bit can break IRQ delivery or wake behavior. Virtual `veint` entries need careful treatment because they have `NULL` function names and are probably not normal GPIO pads. Other risks are incorrect mux values for complex shared subsystems like modem/BPI, PCIe, DP, and GBE, and the sheer size of the table makes off-by-one review errors likely.

## Test Signals
Test signals include successful MT8196 pinctrl probe, complete `debugfs` pin listing including virtual pins, DT validation for typical board pin states, GPIO loopback tests on normal pads, IRQ mapping and debounce tests across all EINT instances, and smoke tests for high-risk buses such as SPI, I2C, UART, MSDC, PCIe sideband, DP, audio, and GBE. A focused static check should verify 293 `MTK_PIN()` entries and 293 `MTK_EINT_PIN()` entries remain aligned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8196.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8365.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8365.h

## Purpose
This header is the MT8365 pin descriptor table for the older MediaTek pinctrl common framework, not the Paris/common-v2 schema. It includes `pinctrl-mtk-common.h` and defines `static const struct mtk_desc_pin mtk_pins_mt8365[]`, a 156-pin contiguous table from GPIO0 to BIAS1_MSDC1. Each entry maps a `PINCTRL_PIN()` descriptor to an EINT function and a list of legal mux functions for MT8365 pads.

## Important APIs, Types, And Data
The central type is `struct mtk_desc_pin`, which wraps a `struct pinctrl_pin_desc`, `struct mtk_desc_eint`, and a null-terminated `struct mtk_desc_function` list. The file uses the legacy `MTK_PIN(_pin, _pad, _chip, _eint, ...)` macro shape, where the `_pad` and `_chip` arguments are present for compatibility but not structurally retained by the macro shown in `pinctrl-mtk-common.h`.

The table covers display DPI pins, PWM, I2S/TDM/audio, external modem/UART-like signals, CONN MCU and wireless pins, debug monitor outputs, MSDC0/MSDC1/MSDC2, SPI, I2C, APU/ADSP/UDI/DFD, antenna and connectivity control, DMIC, TDM TX, and reset/bias pins. The final region includes nonstandard pad names such as `TESTMODE`, `SYSRSTB`, and BIAS_* pins that generally expose only GPIO/function zero.

## Control Flow And Integration
This file has no executable code. Legacy MediaTek SoC driver code includes it in a platform driver data structure, registers the pin descriptions with the old common pinctrl implementation, and uses the per-pin function list to validate mux selections from board pinctrl states. GPIO, pinconf, and EINT operations are implemented by the older common driver and hardware-specific register tables in the companion C file.

## State And Persistence
All contents are immutable compile-time data. Runtime state is handled by the legacy MediaTek common driver and SoC registers. Pin mode, GPIO direction/value, bias, input-enable, Schmitt, and drive strength settings persist only in hardware register state and are re-established by driver probe or board pinctrl state application.

## Dependencies
The table depends on the legacy `pinctrl-mtk-common.h` macro and type layout. It must align with the companion MT8365 devdata: total pin count, EINT count, register offsets, drive tables, IES/SMT tables, special pull-up/down tables, and devicetree binding values. Function names and mux numbers must match datasheet and binding documentation, especially for shared display, audio, storage, and connectivity pins.

## Risks
Legacy schema differences are a risk: code expecting `struct mtk_pin_desc` from Paris cannot consume this table. Mux-value mistakes can be hard to detect because many pins carry debug or alternate subsystem signals in high mux values. The final bias/reset pins have limited functions and can be mistaken for normal GPIOs. EINT numbers are simple and mostly one-to-one, so any exception in silicon wiring needs explicit review in companion data.

## Test Signals
Validation should include compiling the MT8365 pinctrl driver, DT pinctrl state checks for major peripherals, GPIO request/direction/value tests, EINT tests on several GPIO and special pins, and peripheral bring-up for DPI, I2S/TDM, MSDC, SPI/I2C/UART, connectivity, and PWM. Static checks should preserve 156 `MTK_PIN()` entries and contiguous pin numbers 0 through 155.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8365.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8516.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8516.h

## Purpose
This header defines the MT8516 pin table for the legacy MediaTek pinctrl common driver. It includes `pinctrl-mtk-common.h` and declares `static const struct mtk_desc_pin mtk_pins_mt8516[]`, a 125-pin table. The first pins are named `EINT0` through `EINT19`, later entries use functional pad names such as MSDC0 lines, and the table ends with GPIO121 through GPIO124.

## Important APIs, Types, And Data
The file uses legacy `struct mtk_desc_pin` and the macros `MTK_PIN`, `PINCTRL_PIN`, `MTK_EINT_FUNCTION`, and `MTK_FUNCTION`. It is not compatible with Paris `struct mtk_pin_desc` without translation. Each pin lists one or more mux values, with function zero normally being the GPIO mode. Important function families include PWM, I2S/I2S3/TDM, external bus/control signals, CONN MCU/debug signals, SQI/SPI, USB, PWRAP, MSDC0/MSDC1/MSDC2, PCM/MRG, SPDIF, antenna control, and debug monitor outputs.

## Control Flow And Integration
This file contributes static data to the MT8516 platform pinctrl driver. The legacy common driver registers these pins with Linux pinctrl, maps pinmux states from devicetree to per-pin functions, and performs register writes through companion MT8516 register/drive/EINT data. There is no local function control flow in this header.

## State And Persistence
All state in the file is immutable kernel data. Runtime mux and pin configuration state is stored in hardware registers and the common driver's private structures. No values are persisted to disk or NVRAM by this code.

## Dependencies
The table depends on old MediaTek common-driver definitions and companion MT8516 register metadata. The EINT naming of early pins must match both hardware interrupt numbering and board devicetree usage. Function names and mux values must match binding headers and datasheet definitions for multimedia, storage, connectivity, and external bus functions.

## Risks
The main risk is mux-value mismatch on shared pins. MT8516 uses many function names that encode bus lanes or debug monitor bits; a wrong value can partially break a bus while still allowing the pinctrl state to apply. Early `EINT*` pad names can confuse code or tests that assume names are `GPIO*`. Tail pins with only function zero should be treated as limited GPIO-only pads. Schema mismatch with Paris/common-v2 is also a maintenance risk.

## Test Signals
Test with MT8516 driver compilation, devicetree pin state parsing, GPIO request and direction tests across EINT-named and GPIO-named pads, EINT interrupt tests for early pins, and peripheral smoke tests for PWM, audio, SPI/SQI, USB, PWRAP, MSDC, and external interface pins. Static review should preserve 125 contiguous entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8516.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtmips.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtmips.c

## Purpose
This file implements the shared pinctrl/pinmux core for older Ralink/MediaTek MIPS SoCs such as RT2880, RT305x, RT3352, RT5350, and RT3883. It consumes SoC-specific `struct mtmips_pmx_group` arrays and registers a Linux pinctrl device named `mtmips-pinctrl`. It is focused on muxing groups through Ralink system controller GPIO mode registers; it does not implement full pinconf or a gpiochip.

## Important APIs, Types, And Functions
The private state is `struct mtmips_priv`, holding generated pin descriptors, group/function indexes, GPIO-capability flags, and the source SoC group table. Pinctrl operations are `mtmips_get_group_count()`, `mtmips_get_group_name()`, and `mtmips_get_group_pins()`. Pinmux operations are `mtmips_pmx_func_count()`, `mtmips_pmx_func_name()`, `mtmips_pmx_group_get_groups()`, `mtmips_pmx_group_enable()`, and `mtmips_pmx_group_gpio_request_enable()`.

The exported integration entry is `int mtmips_pinctrl_init(struct platform_device *pdev, struct mtmips_pmx_group *data)`. Initialization uses `mtmips_pinctrl_index()` to count groups/functions and build lookup arrays, then `mtmips_pinctrl_pins()` to synthesize contiguous `io%d` pin descriptors and default GPIO eligibility.

## Control Flow
Probe callers pass a sentinel-terminated SoC group table. `mtmips_pinctrl_index()` counts groups, allocates `group_names`, adds a synthetic function zero named `gpio`, and gives every hardware function a backpointer to its single owning group. `mtmips_pinctrl_pins()` allocates per-function pin arrays from `pin_first` and `pin_count`, computes `max_pins`, allocates the GPIO bitmap and pad descriptors, and names pins `io0` through `ioN`.

Mux selection in `mtmips_pmx_group_enable()` rejects double-use only by logging if the group is already enabled, marks the group and function enabled, selects `SYSC_REG_GPIO_MODE` or `SYSC_REG_GPIO_MODE2` depending on shifts >= 32, clears the group's mask, marks all group pins as GPIO, then either writes the group's GPIO value for function zero or writes the selected function value and marks that function's pins as non-GPIO. Writes go through `rt_sysc_r32()`/`rt_sysc_w32()`.

## State And Persistence
Driver state is devm-managed memory tied to the platform device. The `enabled` flags in group/function structs are mutable and persist until driver removal or reboot. Hardware mux choices persist in Ralink sysc registers until changed or reset. The file does not persist state to storage and does not provide suspend/resume save/restore.

## Dependencies
This file depends on Linux pinctrl core, pinctrl utility DT parsing, Ralink sysc register helpers, and SoC-specific tables declared with `pinctrl-mtmips.h` macros. It assumes each function can be described as a contiguous pin range and each non-GPIO function belongs to one group.

## Risks
There is no locking around sysc read-modify-write or `enabled` flags, so concurrent mux changes could race. Returning success when a group is already enabled may hide conflicting pinctrl state requests. Bounds checks are limited: function selectors are assumed valid by pinctrl core paths, and `gpio_request_enable` indexes `p->gpio[pin]`. The implementation also lacks pinconf and gpiochip integration, so board expectations must be limited to mux validation and pinctrl ownership.

## Test Signals
Test by booting each SoC-specific driver, applying DT states for GPIO and alternate functions, checking sysc GPIO mode register values, attempting GPIO requests before and after mux changes, and verifying pinctrl debug output lists generated `io%d` pins and expected groups. Race-sensitive changes should be reviewed with lockdep or serialized pinctrl state application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtmips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtmips.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtmips.h

## Purpose
This header defines the small table-building API for MTMIPS/Ralink pinmux drivers. SoC files use it to declare mux functions, groups, masks, GPIO values, and register shifts, then pass the resulting group array to `mtmips_pinctrl_init()`.

## Important APIs And Types
`FUNC(name, value, pin_first, pin_count)` initializes `struct mtmips_pmx_func` with a mux value and contiguous pin range. `GRP(name, func, mask, shift)` initializes a group whose GPIO value equals its mask. `GRP_G(name, func, mask, gpio, shift)` allows a group-specific GPIO value separate from the field mask.

`struct mtmips_pmx_func` stores the public function name, field value, contiguous pin range, generated pin array, owning groups, group count, and an `enabled` flag. `struct mtmips_pmx_group` stores the group name, enabled flag, sysc field shift/mask/GPIO value, function array, and function count. The only declared function is `mtmips_pinctrl_init()`.

## Control Flow And Integration
This header has no runtime flow itself. The SoC-specific drivers include it, build sentinel-terminated `struct mtmips_pmx_group` arrays, and call the shared initializer from their probe functions. The shared implementation mutates `pins`, `groups`, `group_count`, and `enabled` fields at runtime, so these tables are not strictly const.

## State And Persistence
The structs include mutable fields populated or changed by `pinctrl-mtmips.c`. Generated pin arrays and group backpointers are devm-managed by the initializer. Hardware persistence is not described here; the implementation writes sysc GPIO mode registers.

## Dependencies
The header assumes Linux kernel types such as `u32`, `ARRAY_SIZE`, and `struct platform_device` are available from including C files. It also assumes contiguous pin ranges are sufficient to describe every SoC function.

## Risks
Because function/group tables are mutable, declaring them `const` in a SoC file would be invalid with the current implementation. The `char` type for mux values, masks, and GPIO values is narrow; larger fields would need schema changes. Incorrect `pin_first`/`pin_count` values directly affect generated pin descriptors and GPIO eligibility.

## Test Signals
Compile all RT2880/RT305x/RT3883 users after macro changes. Runtime tests should verify group counts, function names, generated pin names, and sysc field writes match each SoC table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtmips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-paris.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-paris.c

## Purpose
This is the MediaTek Paris common pinctrl driver for newer SoCs using per-pin vendor bindings. It supplies shared pinctrl, pinmux, pinconf, GPIO, EINT, debugfs, and PM behavior for SoC drivers that provide an `mtk_pin_soc` descriptor and `struct mtk_pin_desc` tables.

## Important APIs, Types, And Functions
The exported entry point is `mtk_paris_pinctrl_probe()`, which allocates `struct mtk_pinctrl`, maps named register bases, builds one-pin groups, registers and enables pinctrl, builds EINT, and registers a gpiochip. `mtk_pctrl_show_one_pin()` is exported for debug display. `mtk_paris_pinctrl_pm_ops` wraps EINT suspend/resume.

Pinconf uses custom parameters `mediatek,tdsel`, `mediatek,rdsel`, `mediatek,pull-up-adv`, `mediatek,pull-down-adv`, and `mediatek,drive-strength-adv`. It bridges advanced drive strength encoding to standard `PIN_CONFIG_DRIVE_STRENGTH_UA` for 125, 250, 500, and 1000 uA. Important control functions include `mtk_pinconf_get()`, `mtk_pinconf_set()`, `mtk_pctrl_dt_subnode_to_map()`, `mtk_pmx_set_mux()`, `mtk_gpio_to_irq()`, and `mtk_gpio_set_config()`.

## Control Flow
Devicetree mapping starts at `mtk_pctrl_dt_node_to_map()`, iterating child nodes and calling `mtk_pctrl_dt_subnode_to_map()`. Each child must have `pinmux`; generic pinconf properties are parsed once and attached to each one-pin group. `MTK_GET_PIN_NO()` and `MTK_GET_PIN_FUNC()` decode pin/function cells, the pin/function pair is validated against the SoC pin's function list, then mux and optional group config maps are added.

Mux application validates the requested selector for the pin group and writes `PINCTRL_PIN_REG_MODE` with the SoC-provided mux value. GPIO request forces GPIO mode; direction, value, input, debounce, and IRQ routing delegate to common-v2 register helpers and EINT helpers. Probe orders pinctrl enable before gpiochip creation so gpiolib requests can use pinctrl operations.

## State And Persistence
Runtime state lives in `struct mtk_pinctrl`: mapped register bases, gpiochip, SoC data pointer, EINT handle, generated groups, group names, spinlock, and `rsel_si_unit` DT flag. The driver mutates hardware registers for mux, direction, output, input-enable, Schmitt, bias, drive, and EINT debounce. There is no storage persistence; suspend/resume calls EINT PM helpers only.

## Dependencies
The driver depends on `pinctrl-mtk-common-v2.h`, `mtk-eint.h`, Linux pinctrl/pinconf/gpio subsystems, named platform resources, and SoC descriptors with valid register calculators and optional callback hooks. It assumes one pin per group and direct indexing by pin number into `hw->soc->pins`.

## Risks
The global static `mtk_desc` is modified at probe time, which can be risky if multiple Paris instances with different SoC data probe concurrently. `mtk_pctrl_build_state()` allocates `ngrps` groups but iterates `npins`, so SoC descriptors must keep those counts consistent. Advanced drive-strength fallback deliberately disables advanced drive mode when no uA or explicit advanced setting is present; this can surprise board authors. Virtual GPIO handling is special in direction and debug paths and must be represented consistently by SoC data.

## Test Signals
Test with build coverage for multiple Paris SoCs, DT parsing failures for invalid pin/function cells, pinconf get/set for bias, input, Schmitt, level, drive-strength and custom fields, gpiochip direction/value operations, GPIO-to-IRQ mapping and debounce, debugfs pin dumps, and suspend/resume with EINT wake sources. Multi-instance SoC testing is useful because of the shared static descriptor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-paris.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-paris.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-paris.h

## Purpose
This header is the public interface and macro layer for the MediaTek Paris common pinctrl driver. It lets SoC-specific pin tables describe pins, EINT metadata, functions, register ranges, and pin groups in the `pinctrl-mtk-common-v2.h` schema.

## Important APIs And Types
The header includes kernel pinctrl/pinmux/pinconf dependencies plus internal pinctrl core headers, `mtk-eint.h`, and `pinctrl-mtk-common-v2.h`. Important macros are `MTK_RANGE()` for register range arrays, `MTK_EINT_FUNCTION()` for `struct mtk_eint_desc`, `MTK_FUNCTION()` for `struct mtk_func_desc`, `MTK_PIN()` for `struct mtk_pin_desc`, `MTK_EINT_PIN()` for `struct mtk_eint_pin`, and `PINCTRL_PIN_GROUP()` for one or more pin groups using pin/function arrays.

It declares `mtk_paris_pinctrl_probe()`, exported debug helper `mtk_pctrl_show_one_pin()`, and `mtk_paris_pinctrl_pm_ops`.

## Control Flow And Integration
There is no executable control flow in the header. SoC drivers include it to build static descriptor tables and to reference the common probe function from their platform driver. The macros create compound function arrays terminated by an empty descriptor, which Paris later walks for function validation.

## State And Persistence
This header defines compile-time data construction only. Runtime state is owned by `pinctrl-paris.c` and common-v2 helpers. Compound literals created by `MTK_PIN()` become part of static initializer data when used in static SoC arrays.

## Dependencies
The header depends on macro compatibility with `struct mtk_pin_desc`, `struct mtk_func_desc`, `struct mtk_eint_desc`, and `struct mtk_eint_pin`. Any schema change in common-v2 requires updating these macros and all SoC tables. It also exposes internal pinctrl headers, so it is meant for in-tree driver use rather than a stable external API.

## Risks
Macro-heavy table definitions can hide type or terminator mistakes. `MTK_FUNCTION(0, NULL)` is allowed by current tables for virtual or fixed pins, so function-walking code must treat a `NULL` name as terminator only where intended by macro-generated arrays. Incorrect use of `PINCTRL_PIN_GROUP()` can mismatch pin and function arrays by naming convention.

## Test Signals
Compile all Paris SoC tables after macro edits. Static checks should verify function arrays are terminated, EINT tables are aligned, and SoC tables use the intended schema rather than the legacy `pinctrl-mtk-common.h` schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-paris.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-rt2880.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-rt2880.c

## Purpose
This file is the RT2880-specific MTMIPS pinmux driver. It declares RT2880 sysc GPIO mode bits, maps each mux group to a contiguous pin range, and registers a platform driver that calls `mtmips_pinctrl_init()`.

## Important APIs, Types, And Data
The SoC data is `rt2880_pinmux_data_act[]`, a sentinel-terminated `struct mtmips_pmx_group` array. Groups are `i2c`, `spi`, `uartlite`, `jtag`, `mdio`, `sdram`, and `pci`. The function arrays are simple one-function groups built with `FUNC()`: I2C pins 1-2, SPI pins 3-6, UART lite pins 7-14, JTAG pins 17-21, MDIO pins 22-23, SDRAM pins 24-39, and PCI pins 40-71.

## Control Flow
`rt2880_pinctrl_probe()` delegates directly to `mtmips_pinctrl_init()`. The platform driver matches `ralink,rt2880-pinctrl` and legacy `ralink,rt2880-pinmux`. Registration uses `core_initcall_sync()`, making it available early for board initialization.

## State And Persistence
The file itself has static mutable function/group arrays because the shared MTMIPS core fills runtime backpointers and enabled flags into the structs. Hardware mux state is stored in Ralink sysc GPIO mode registers.

## Dependencies
It depends on `pinctrl-mtmips.h`, Linux platform/of/module headers, and the shared MTMIPS core. The bit definitions must match RT2880 `SYSC_REG_GPIO_MODE` layout.

## Risks
The PCI group spans 32 pins and can move a large external bus at once. Since every group has a single non-GPIO function with mux value zero, the shared core relies entirely on the group mask/shift to distinguish GPIO from active peripheral mode. Incorrect shifts or masks would directly corrupt sysc mode bits.

## Test Signals
Boot an RT2880 DT with this compatible, verify early driver registration, inspect generated groups/functions, apply each mux state, and compare sysc GPIO mode register bits against expected values. GPIO request tests should fail when a pin is muxed away from GPIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-rt2880.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-rt305x.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-rt305x.c

## Purpose
This file provides one platform driver for several RT305x-family SoCs: RT305x/RT3350, RT3352, and RT5350. It defines shared and SoC-specific MTMIPS mux groups, then chooses the correct group table at probe time using Ralink `soc_is_*()` helpers.

## Important APIs, Types, And Data
The file defines UART0 mode masks/values, single-bit mode positions for I2C/SPI/UART1/JTAG/MDIO/SDRAM/RGMII, and extra RT5350/RT3352 LED, SPI CS1, LNA, and PA modes. Function arrays include a multi-option `uartf_grp` with UARTF, PCM/UARTF, PCM/I2S, I2S/UARTF, partial GPIO combinations, and simpler groups for I2C, SPI, UART lite, JTAG, MDIO, SDRAM, RGMII, LED, CS1, LNA, and PA.

Three sentinel-terminated group tables are present:

- `rt3050_pinmux_data` for RT305x/RT3350.
- `rt3352_pinmux_data` with RT3352-specific RGMII, LNA, PA, LED, and CS1 placement.
- `rt5350_pinmux_data` with RT5350 LED and CS1 but without MDIO/RGMII/SDRAM groups.

## Control Flow
`rt305x_pinctrl_probe()` selects the group table based on `soc_is_rt5350()`, `soc_is_rt305x() || soc_is_rt3350()`, or `soc_is_rt3352()`, then delegates to `mtmips_pinctrl_init()`. Unknown SoCs return `-EINVAL`. The platform driver matches three family-specific compatibles plus the legacy `ralink,rt2880-pinmux`, and is registered with `core_initcall_sync()`.

## State And Persistence
Runtime state is stored by the shared MTMIPS core in the mutable group/function arrays and sysc GPIO mode registers. The selected table is not copied before mutation, so only one matching platform instance is expected.

## Dependencies
The file depends on Ralink SoC identification headers, sysc layout constants, `pinctrl-mtmips.h`, and the shared MTMIPS implementation. Board DT compatible strings must align with actual SoC ID helpers; the compatible alone does not decide the table.

## Risks
The probe-time SoC ID branch can reject or misconfigure systems if the DT compatible and detected SoC disagree. UARTF is a multi-bit field with partial GPIO modes, so mask/value mistakes can expose only part of a peripheral. RT3352 and RT5350 reuse similar group names with different pin ranges, which is error-prone during edits.

## Test Signals
Test separately on RT305x/RT3350, RT3352, and RT5350. Verify chosen table, generated group list, UARTF mode permutations, SPI CS1 alternate functions, and sysc register writes. DT smoke tests should cover all advertised compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-rt305x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-rt3883.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-rt3883.c

## Purpose
This file is the RT3883-specific MTMIPS pinmux driver. It describes RT3883 GPIO mode fields and group/function pin ranges, then registers a platform driver that delegates to the shared MTMIPS pinctrl core.

## Important APIs, Types, And Data
The file defines multi-bit mode constants for UART0, PCI, LNA_A, and LNA_G plus single-bit positions for I2C, SPI, UART1, JTAG, MDIO, GE1, and GE2. Function groups include I2C, SPI, multi-option UARTF, UART lite, JTAG, MDIO, LNA A/G, PCI with four mux values (`pci-dev`, `pci-host2`, `pci-host1`, `pci-fnc`), GE1, and GE2. `rt3883_pinmux_data[]` is the sentinel-terminated table passed to `mtmips_pinctrl_init()`.

## Control Flow
`rt3883_pinctrl_probe()` directly calls `mtmips_pinctrl_init()`. The platform driver matches `ralink,rt3883-pinctrl` and legacy `ralink,rt2880-pinmux`, and registers during `core_initcall_sync()`.

## State And Persistence
State is shared-core mutable table data plus hardware sysc GPIO mode registers. PCI, UARTF, and LNA selections are encoded as multi-bit fields in the register state.

## Dependencies
The driver depends on `pinctrl-mtmips.h`, Linux platform/of/module infrastructure, and the shared MTMIPS implementation. The mode constants must match RT3883 sysc register layout, including fields whose shifts already encode high bit positions.

## Risks
Multi-bit groups are the high-risk paths: UARTF has partial GPIO options, PCI has four function values over a 32-pin range, and LNA fields use shifted masks. The `GRP()` macro expects an unshifted mask plus shift, so passing a pre-shifted value would be dangerous; this file uses unshifted masks for PCI and LNA group masks via explicit mask constants.

## Test Signals
Boot with RT3883 compatible, verify groups and functions, exercise PCI mode values, UARTF mode values, LNA A/G, and GE1/GE2. Check sysc register field values after mux application and GPIO request behavior for pins returned to GPIO mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-rt3883.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/Kconfig

## Purpose
This Kconfig file defines build-time configuration for Amlogic Meson and newer Amlogic pinctrl drivers. `PINCTRL_MESON` is the menuconfig gate and selects common pinctrl, pinmux, pinconf, gpiolib, generic pinconf, and `REGMAP_MMIO` support.

## Important Symbols
`PINCTRL_MESON` is a tristate defaulting to `ARCH_MESON` and requiring OF plus either `ARCH_MESON` or `COMPILE_TEST`. Sub-options cover older Meson8/Meson8b/GXBB/GXL drivers using `PINCTRL_MESON8_PMX`, AXG/G12A/A1/S4/C3/T7 drivers using `PINCTRL_MESON_AXG_PMX`, and `PINCTRL_AMLOGIC_A4`, a bool driver for the newer generic Amlogic pinctrl style. `PINCTRL_AMLOGIC_C3` and `PINCTRL_AMLOGIC_T7` remain per-SoC tristate drivers.

## Control Flow And Integration
Kconfig has no runtime control flow, but it controls which objects the Makefile builds. Hidden symbols `PINCTRL_MESON8_PMX` and `PINCTRL_MESON_AXG_PMX` are selected by SoC entries to include shared mux backends. The A4 option does not select `PINCTRL_MESON_AXG_PMX`; it builds its own `pinctrl-amlogic-a4.o` implementation.

## State And Persistence
Configuration state persists in kernel `.config`. It affects compiled objects and module availability but has no runtime state.

## Dependencies
All entries depend on the top-level menu. Most newer SoC drivers depend on ARM64 or `COMPILE_TEST`. Older Meson8 entries depend on ARM or `COMPILE_TEST`. The menu selects generic dependencies required by the common Meson and Amlogic code paths.

## Risks
`PINCTRL_AMLOGIC_A4` is `bool` rather than `tristate`, so it cannot be built as a module even though nearby drivers can. Help text says new Amlogic SoCs only need DTS additions; that is true only for SoCs whose register layout matches the generic A4/S6/S7 parser and quirks. Missing selects here would manifest as link failures in the Makefile objects.

## Test Signals
Run Kconfig builds for `ARCH_MESON`, ARM64 `COMPILE_TEST`, and module combinations. Verify hidden PMX backends are selected for older drivers and that `CONFIG_PINCTRL_AMLOGIC_A4=y` builds `pinctrl-amlogic-a4.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/Makefile

## Purpose
This Makefile maps Meson/Amlogic Kconfig symbols to pinctrl driver objects. It is the build integration layer for the folder.

## Important Rules
`obj-$(CONFIG_PINCTRL_MESON)` builds the common `pinctrl-meson.o`. Hidden mux backends build `pinctrl-meson8-pmx.o` and `pinctrl-meson-axg-pmx.o`. SoC object rules build Meson8, Meson8b, GXBB, GXL, AXG, G12A, A1, S4, A4, C3, and T7 drivers under their matching Kconfig symbols. `CONFIG_PINCTRL_AMLOGIC_A4` maps directly to `pinctrl-amlogic-a4.o`.

## Control Flow And Integration
There is no runtime flow. Build flow is Kconfig-driven: selected symbols expand to object list entries compiled into built-in code or modules depending on the symbol type. Since A4 is a bool symbol, its object is built-in when enabled.

## State And Persistence
Build state is held in kernel configuration and generated build artifacts. The Makefile itself has no runtime persistence.

## Dependencies
The rules depend on symbol names in `Kconfig` matching source filenames. Common objects must be present when SoC drivers reference shared symbols such as Meson pinctrl probe or PMX ops.

## Risks
The main risk is symbol/object drift: a renamed source file or Kconfig symbol would silently drop driver coverage or cause link failures. Because A4 does not use the older Meson common object in the same way as other drivers, dependency assumptions should be checked when refactoring.

## Test Signals
Use `make drivers/pinctrl/meson/` or broader kernel builds with each relevant config enabled. Check that `CONFIG_PINCTRL_AMLOGIC_A4=y` includes `pinctrl-amlogic-a4.o`, while AXG-family configs also include `pinctrl-meson-axg-pmx.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-amlogic-a4.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-amlogic-a4.c

## Purpose
This file implements a newer generic Amlogic pinctrl and GPIO driver for A4-style SoCs and related S6/S7 variants. Unlike older Meson drivers with static C pin tables, it discovers banks, pins, functions, and groups from devicetree, maps per-bank MMIO resources through regmap, and registers both pinctrl and gpiochips.

## Important APIs, Types, And Functions
Core state is `struct aml_pinctrl`, which owns the pinctrl device, bank array, parsed function array, parsed group array, and optional match data. `struct aml_gpio_bank` stores one gpiochip plus register maps for mux, GPIO, and drive-strength resources. `struct aml_pctl_group` holds parsed pins and function values from `pinmux`, while `struct aml_pmx_func` connects a function node name to its child group names.

Important functions include `aml_pctl_probe()`, `aml_pctl_probe_dt()`, `aml_gpiolib_register_bank()`, `aml_pctl_parse_functions()`, `aml_dt_node_to_map_pinmux()`, `aml_pmx_set_mux()`, `aml_pctl_set_function()`, `aml_pinconf_get()`/`aml_pinconf_set()`, and GPIO callbacks such as `aml_gpio_get_direction()`, `aml_gpio_direction_input()`, `aml_gpio_direction_output()`, `aml_gpio_get()`, and `aml_gpio_set()`.

## Control Flow
Probe allocates a pinctrl descriptor and `aml_pinctrl`, counts devicetree children into banks/functions/groups, allocates arrays, reads match data, counts pins from `gpio-ranges`, and fills pin descriptors by bank. GPIO-controller child nodes are mapped into `aml_gpio_bank` objects with named `mux`, `gpio`, and optional `ds` resources. Non-GPIO child nodes are parsed as functions; each child group uses `pinconf_generic_parse_dt_pinmux()` to load pins and mux function values.

After pinctrl registration, probe registers one gpiochip per bank. Mux application finds each pin's gpio range and writes a 4-bit mux value through `aml_pctl_set_function()`. S6/S7 match data can redirect subordinate-bank pins into another bank's mux registers through `struct multi_mux`. Pinconf operations calculate register offsets using default register offsets and bit strides, then update pull enable, pull direction, direction, output, input, or drive-strength bits.

## State And Persistence
Runtime state is devm-managed and rebuilt from devicetree at probe. Hardware state lives in MMIO registers accessed via regmap. Drive strength is encoded in two-bit values representing 500, 2500, 3000, or 4000 uA. No persistent storage is used; state is reset by hardware reset or reconfigured by pinctrl/gpio consumers.

## Dependencies
The driver depends on OF child-node layout: GPIO bank nodes must carry `gpio-controller`, `gpio-ranges`, and named register resources; function nodes must contain groups with `pinmux` and optional generic pinconf properties. It depends on `dt-bindings/pinctrl/amlogic,pinctrl.h` bank IDs, Linux pinctrl/gpio/regmap APIs, and resource names `mux`, `gpio`, and optionally `ds`.

## Risks
There are several correctness risks. `aml_pmx_set_mux()` ignores errors returned by `aml_pctl_set_function()` and always returns zero, so missing ranges or failed regmap writes can be hidden. Many helpers assume `pinctrl_find_gpio_range_from_pin()` succeeds; malformed DT pin numbers can cause null dereferences. If `ds` registers are missing, the driver aliases drive-strength writes to `reg_gpio`, which may be intentional for some layouts but risky if a SoC truly lacks drive-strength support. Multi-mux handling checks only one quirk entry per bank because `init_bank_register_bit()` breaks on the first match. GPIO `get()` ignores `regmap_read()` errors.

## Test Signals
Test with A4, S6, and S7 devicetrees. Validate bank counting, pin descriptor numbering from `bank_id << 8`, named resource mapping, gpiochip registration, mux changes for normal and multi-mux pins, pull-up/down/disable, output enable/level, drive-strength boundaries, and failure cases for invalid `pinmux` values. Static analysis should flag ignored return values in mux and gpio get paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-amlogic-a4.c -->
