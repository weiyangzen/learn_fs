# Research: subset-b-005061

This grouped report covers five MediaTek Paris pinctrl SoC pin metadata headers. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8183.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8183.h

## Purpose

`pinctrl-mtk-mt8183.h` is the MT8183 pin descriptor catalog consumed by the MediaTek Paris pinctrl driver. It defines one file-local array, `mtk_pins_mt8183`, containing 192 `struct mtk_pin_desc` entries for GPIO0 through GPIO191. Each entry describes the Linux pin number, GPIO name, EINT mux/number mapping, drive-strength selector group, and the alternate-function mux values exposed through pinctrl and device tree pinmux configuration.

The header is included by `pinctrl-mt8183.c`, which places the array into `mt8183_data.pins`, sets `.npins` and `.ngrps` from `ARRAY_SIZE(mtk_pins_mt8183)`, and combines it with MT8183 register-calculation ranges, EINT hardware metadata, bias/drive callbacks, and register base names. This file is therefore data rather than executable control logic, but it is a central ABI table for every MT8183 board using this pinctrl driver.

## Important APIs, Types, And Data

- `mtk_pins_mt8183`: static `struct mtk_pin_desc` array. Unlike the newer neighboring headers, this one is not declared `const`, so accidental writes inside the same translation unit would be possible if introduced later.
- `MTK_PIN(number, name, eint, drv_n, ...)`: macro from `pinctrl-paris.h` that expands to a `struct mtk_pin_desc` initializer with a compound-literal `struct mtk_func_desc[]` terminated by an empty entry.
- `MTK_EINT_FUNCTION(eintmux, eintnum)`: stores `.eint_m` and `.eint_n`; every MT8183 pin has an EINT initializer, though some late GPIOs use non-linear EINT numbers.
- `MTK_FUNCTION(muxval, name)`: maps mux selector values to function names. Function 0 is normally the GPIO identity string.
- `DRV_GRP4`: the drive-strength group used by every MT8183 descriptor in this header.

The table has 939 `MTK_FUNCTION` entries. Early pins expose dense audio, SPI, I2C, UART, PWM, touch-panel, SCP, modem, connectivity, JTAG, and debug monitor alternatives. Later pins include RF/BSI, MSDC, keypad, antenna selection, clock, USB ID/VBUS, and a run of simple GPIO-only descriptors.

## Control Flow

There is no runtime branching in this header. At compile time, `pinctrl-mt8183.c` includes it before constructing the `struct mtk_pin_soc` instance. At probe time, `mtk_paris_pinctrl_probe()` receives that SoC data through the platform-device match table, registers each descriptor as a pin/group, and uses `mtk_pin_desc.funcs` to satisfy pinmux requests. Pin state changes then flow through the Paris core and the register-calculation tables in `pinctrl-mt8183.c`; this header only supplies the pin/function metadata selected by those operations.

## State And Persistence

The file contributes static in-kernel metadata. It does not allocate memory, persist state, or perform I/O. Pin configuration state lives in hardware registers and is restored or queried by the common pinctrl/GPIO/EINT layers. Because `mtk_pins_mt8183` is a static array included into one `.c` file, its lifetime is the loaded driver lifetime.

## Dependencies And Integration Points

- Depends directly on `pinctrl-paris.h`, which includes the common v2 pinctrl types and defines the initializer macros.
- Integrated by `pinctrl-mt8183.c` through `.pins = mtk_pins_mt8183`, `.npins = ARRAY_SIZE(mtk_pins_mt8183)`, and `.ngrps = ARRAY_SIZE(mtk_pins_mt8183)`.
- Must stay synchronized with `mt8183_reg_cals`, `mt8183_eint_hw`, and `mt8183_pinctrl_register_base_names` in the companion `.c` file.
- Function strings are externally observed through pinctrl debug output and board device-tree pinmux choices, so renaming or mux-value drift can break boards without C compiler warnings.

## Risks

- The late GPIO range has non-linear EINT numbering: GPIO171-179 map to EINT184-192, while GPIO180-191 map back to EINT171-183 with a gap. Off-by-one edits here would break interrupt routing.
- The array count is the source for both `.npins` and `.ngrps`; adding, deleting, or reordering entries changes the pinctrl ABI exposed to device trees and userspace debug interfaces.
- All descriptors use `DRV_GRP4`; if hardware has pin-specific drive groups, this table would not express them and drive-strength requests could be wrong.
- Because the array is not `const`, future code in the including translation unit could mutate descriptor metadata, unlike the MT8186/MT8188/MT8189/MT8192 headers.
- Generated-looking large tables are easy to review poorly. A single wrong mux value or function name can silently route a peripheral to the wrong pad.

## Test Signals

- Build with the MT8183 pinctrl driver enabled to catch macro/type regressions.
- Boot on MT8183 hardware or an MT8183 board test target and confirm pinctrl probe, GPIO chip registration, and EINT registration.
- Exercise representative device-tree pinmux groups for SPI, I2C, audio, USB ID/VBUS, MSDC, modem/connectivity, and debug/JTAG alternatives.
- Inspect `/sys/kernel/debug/pinctrl/*/pins`, `pinmux-pins`, and GPIO/EINT interrupt behavior for pins with non-linear EINT mappings.
- Compare descriptor count and highest pin number: 192 `MTK_PIN` entries, GPIO0 through GPIO191.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8183.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8186.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8186.h

## Purpose

`pinctrl-mtk-mt8186.h` is the MT8186 pin descriptor catalog for the MediaTek Paris pinctrl framework. It defines `mtk_pins_mt8186`, a static const array of 197 `struct mtk_pin_desc` entries covering GPIO0 through GPIO196. The descriptors enumerate mux alternatives, EINT assignments, and drive group metadata for the MT8186 pad ring.

The companion `pinctrl-mt8186.c` includes this header and attaches the array to `mt8186_data`. That SoC data also provides register ranges, pull and resistance tables, EINT hardware parameters, and callbacks used by the common Paris implementation. This header is therefore the logical pin/function map used by pinctrl consumers, GPIO users, and EINT routing.

## Important APIs, Types, And Data

- `mtk_pins_mt8186`: static const `struct mtk_pin_desc` array. The `const` qualifier matches the table's read-only role after compilation.
- 197 `MTK_PIN` entries and 988 `MTK_FUNCTION` entries.
- `MTK_EINT_FUNCTION(0, n)` appears on every descriptor; pins 185 through 196 map to EINT197 through EINT208 and are fixed/reserved descriptors.
- `DRV_GRP4` is used for normal pins; `DRV_FIXED` is used for GPIO185-GPIO196 with `MTK_FUNCTION(0, NULL)`.
- Function alternatives cover I2S, SPI, DPI/display, UART, JTAG for SPM/SCP/ADSP/connectivity, PWM, touch-panel GPIO, SCP, modem, MSDC, SPMI, audio, connectivity, watchdog, and debug monitor names.

## Control Flow

The header has no functions and no runtime control flow. Its initializers are compiled into `pinctrl-mt8186.c`. During platform probe, the Paris driver reads `mt8186_data.pins`, registers one pin group per descriptor because `.ngrps = ARRAY_SIZE(mtk_pins_mt8186)`, and uses each descriptor's function list when pinmux clients request a mux value. Actual register accesses are calculated through `mt8186_reg_cals` in the `.c` file.

## State And Persistence

The header contributes immutable static metadata. It does not persist driver state or hardware state. Persistent effects are only indirect: when a pinctrl state is applied, the common driver programs SoC registers based on the pin numbers and mux values declared here. Runtime state is in hardware registers and Linux pinctrl/GPIO/EINT subsystems.

## Dependencies And Integration Points

- Depends on `pinctrl-paris.h` for `struct mtk_pin_desc`, `MTK_PIN`, `MTK_FUNCTION`, and `MTK_EINT_FUNCTION`.
- Included by `pinctrl-mt8186.c`, which configures `.pins`, `.npins`, `.ngrps`, `.nfuncs = 8`, `.gpio_m = 0`, `.eint_hw = &mt8186_eint_hw`, `.pull_type`, `.pin_rsel`, and bias/drive callbacks.
- Must align with the register base names and `mt8186_reg_cals` arrays in the `.c` file. If a pin exists here but no register range covers the corresponding field, pin configuration will fail or touch the wrong register.
- The EINT numbers must agree with `mt8186_eint_hw.ap_num = 217`, port mask, port count, and debounce limits.

## Risks

- GPIO185-GPIO196 are fixed descriptors with NULL function names. Code that assumes function 0 always has a printable GPIO string can misreport or dereference NULL if not guarded in common code.
- The fixed pins still have EINT mappings, so tests must distinguish "no muxable GPIO function" from "no interrupt support".
- Sparse mux alternatives leave holes in some `MTK_FUNCTION` value sequences. Consumers must use explicit mux values, not ordinal positions in the initializer list.
- Any table edit can break board device-tree pinctrl states because function names and mux numeric values form a de facto hardware ABI.
- The file relies on all normal pins being `DRV_GRP4`; mismatched drive metadata would show up only through electrical behavior or pinconf failures.

## Test Signals

- Build-test `pinctrl-mt8186.c` with this header to verify macro/type compatibility.
- Probe on MT8186 hardware and check the expected 197 pins/groups and 8-function mux model.
- Apply representative device-tree pin states for SPI, I2S, DPI, UART, JTAG, MSDC, SPMI, audio, and connectivity pins.
- Exercise GPIO185-GPIO196 debug output and pinctrl enumeration to ensure NULL function names and `DRV_FIXED` are handled correctly.
- Validate EINT delivery for regular pins and for late fixed pins that still carry EINT numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8186.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8188.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8188.h

## Purpose

`pinctrl-mtk-mt8188.h` defines the MT8188 pin descriptor table for the MediaTek Paris pinctrl driver. Its `mtk_pins_mt8188` array has 190 static const descriptors for GPIO0 through GPIO189. Each descriptor maps a pad to EINT metadata, a drive group, and up to eight mux-function names.

The table is included by `pinctrl-mt8188.c`, where `mt8188_data` uses it as the source of pin and group definitions. The companion `.c` file supplies register ranges, pull/resistance settings, EINT hardware limits, and callbacks. This header's role is to expose the SoC's pad-function matrix to Linux pinctrl, GPIO, and device-tree consumers.

## Important APIs, Types, And Data

- `mtk_pins_mt8188`: static const `struct mtk_pin_desc` array.
- 190 `MTK_PIN` entries and 1104 `MTK_FUNCTION` entries, making this one of the denser mux tables in this group.
- Function names often carry direction/bank prefixes such as `B0_`, `B1_`, `I0_`, `I1_`, and `O_`. Those prefixes are meaningful hardware naming, not local C types.
- `DRV_GRP4` covers GPIO0-GPIO176. GPIO177-GPIO189 are fixed descriptors with `DRV_FIXED` and `MTK_FUNCTION(0, NULL)`.
- Peripheral coverage includes SPI master ports, UART, DMIC, I2S/TDM/SPDIF audio, PWM, clock monitor/reference signals, HDMI/CEC hotplug-related signals, APU/VPU/IPU/ADSP/SCP/CCU/JTAG, DPI/display, camera, I2C, MSDC0/1/2, SPMI, LVTS, and debug monitor alternatives.

## Control Flow

This header has no runtime logic. The `MTK_PIN` and `MTK_FUNCTION` initializers are expanded at compile time into descriptor data. At probe, the Paris core consumes `mt8188_data.pins` and registers each pin as a group. When clients apply mux states, the core resolves the requested pin/group and mux value against this descriptor table before using register ranges from `pinctrl-mt8188.c` to program hardware.

## State And Persistence

All state in this file is compile-time static metadata. There are no mutable globals, allocations, locks, or persistence paths. Runtime pin state persists only in SoC pinctrl registers, and suspend/resume handling comes from the common Paris driver and SoC data in the companion `.c` file.

## Dependencies And Integration Points

- Depends on `pinctrl-paris.h` for the descriptor macros and common types.
- Included by `pinctrl-mt8188.c`, where `mt8188_data` assigns `.pins = mtk_pins_mt8188`, `.npins` and `.ngrps` from `ARRAY_SIZE`, `.nfuncs = 8`, `.gpio_m = 0`, `.eint_hw = &mt8188_eint_hw`, register base names, pull type tables, resistance-selection ranges, and bias/drive callbacks.
- EINT descriptors must align with `mt8188_eint_hw.ap_num = 225`; fixed pins GPIO177-GPIO189 map to EINT212-EINT224.
- Function names and mux values must match board DTS pinctrl definitions and hardware documentation.

## Risks

- The prefix-heavy function names make copy/paste errors hard to detect; swapping `I0_`, `I1_`, `O_`, `B0_`, or `B1_` can invert signal direction or select a different physical bank.
- GPIO177-GPIO189 have `DRV_FIXED` and NULL function names. Common debug or mux enumeration code must tolerate NULL function descriptors.
- The guard macro's closing comment spells `__PINCTRL__MTK_MT8188_H`, while the actual guard macro is `__PINCTRL_MTK_MT8188_H`. This is only a comment mismatch, but it can mislead manual review.
- A single descriptor count change affects both pin and group counts because `.ngrps` equals `ARRAY_SIZE(mtk_pins_mt8188)`.
- Dense shared mux values among debug, JTAG, media, audio, and storage functions increase the risk of board-level conflicts that compile cleanly.

## Test Signals

- Build with MT8188 pinctrl enabled and run sparse/checkpatch-style static checks for table syntax regressions.
- Probe on MT8188 hardware and confirm 190 pins/groups are visible through pinctrl debugfs.
- Exercise DTS pinmux states for audio, SPI, I2C, display/HDMI, camera, MSDC, SPMI, and JTAG/debug paths.
- Verify fixed GPIO177-GPIO189 enumeration and any EINT behavior expected for EINT212-EINT224.
- Compare pin descriptor names and mux values against the MT8188 datasheet or generated vendor source when changing the table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8188.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8189.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8189.h

## Purpose

`pinctrl-mtk-mt8189.h` is the MT8189 pin and EINT mapping table for the MediaTek Paris pinctrl driver. It defines `mtk_pins_mt8189`, a static const descriptor array with 211 pins from GPIO0 through GPIO210, and `eint_pins_mt8189`, a separate EINT-pin routing table with 210 entries. This makes the file more than a simple mux catalog: it also supplies explicit EINT instance/index/debounce metadata consumed by the MT8189 SoC data.

The companion `pinctrl-mt8189.c` includes this header and assigns both `.pins = mtk_pins_mt8189` and `.eint_pin = eint_pins_mt8189` in `mt8189_data`. That SoC data is probed by the common Paris implementation to expose MT8189 pinmux, GPIO, and external-interrupt behavior.

## Important APIs, Types, And Data

- `mtk_pins_mt8189`: static const `struct mtk_pin_desc` array with 211 `MTK_PIN` entries and 957 `MTK_FUNCTION` entries.
- `eint_pins_mt8189`: static `struct mtk_eint_pin` array with 210 `MTK_EINT_PIN(number, instance, index, debounce)` entries.
- `MTK_EINT_FUNCTION`: used in every pin descriptor, including one descriptor using `NO_EINT_SUPPORT` for the EINT number.
- `DRV_GRP4`: used for normal muxable pins. `DRV_FIXED` is used for GPIO183-GPIO210, which expose `MTK_FUNCTION(0, NULL)` in this table.
- Function alternatives cover touch-panel GPIO, SPI, I2S, SCP SPI, connectivity BPI/antenna, VADSP, UART, clock monitor/reference, PWM, USB, DPI/display, camera, I2C, SPMI, MSDC, JTAG/debug, SPM/SCP/ADSP/SSPM signals, and debug monitor paths.

## Control Flow

The file itself has no executable control flow. At compile time, the pin and EINT arrays become static data in `pinctrl-mt8189.c`. At probe, `mtk_paris_pinctrl_probe()` receives `mt8189_data`, registers the pin descriptors, and passes the EINT map to the MediaTek EINT layer. Pinmux requests use the descriptor functions; interrupt setup uses the explicit EINT pin mapping to translate a logical GPIO/pin into an EINT instance and index.

## State And Persistence

All state here is static metadata. Runtime pinmux, pull, drive, and interrupt state is stored in hardware registers and managed by the common pinctrl/GPIO/EINT subsystems. The EINT mapping table is static for the loaded module lifetime and does not persist across boots.

## Dependencies And Integration Points

- Depends on `pinctrl-paris.h` for descriptor and EINT initializer macros.
- Included by `pinctrl-mt8189.c`, which sets `.pins`, `.npins`, `.ngrps`, `.eint_pin`, `.eint_hw`, `.nfuncs = 8`, `.gpio_m = 0`, register base names, and pinconf callbacks.
- Must align with `mt8189_eint_hw`, especially `.ap_num = 210`, `.ports = 3`, `.db_cnt = 32`, and the debounce timing table.
- The explicit `eint_pins_mt8189` map introduces an additional synchronization requirement: descriptor-level `MTK_EINT_FUNCTION` values, EINT map entries, and the EINT hardware limits all need to describe the same interrupt topology.

## Risks

- There are 211 pin descriptors but 210 EINT map entries. This appears intentional because EINT AP count is 210, but it is a high-value invariant to verify after edits.
- Some `MTK_EINT_PIN` entries set debounce to 0 while most use 1. If those flags are copied incorrectly, debounce behavior changes without affecting build output.
- GPIO183-GPIO210 are fixed/NULL-function descriptors. Debug paths and mux enumeration must tolerate NULL names.
- One pin descriptor uses `MTK_EINT_FUNCTION(0, NO_EINT_SUPPORT)`, and the late fixed pins use ordinary EINT numbers. Tests must cover unsupported and supported late-pin interrupt cases separately.
- Function-name prefixes and mixed VLP/VCORE/AO naming make board DTS names easy to mistype or misroute.

## Test Signals

- Build-test MT8189 pinctrl with this header and verify no const/type warnings around `eint_pins_mt8189`.
- Probe on MT8189 hardware and confirm 211 pin descriptors, 210 EINT mappings, and expected debugfs pin/group output.
- Exercise pinmux states for SPI, I2S, UART, SCP, connectivity BPI, display/camera, I2C, SPMI, MSDC, and JTAG/debug functions.
- Test EINT setup across multiple instances and pins with debounce flag 0 and 1.
- Specifically test fixed late pins and the descriptor that advertises `NO_EINT_SUPPORT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8189.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8192.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8192.h

## Purpose

`pinctrl-mtk-mt8192.h` defines the MT8192 SoC pin descriptor table for the MediaTek Paris pinctrl implementation. It exports `mtk_pins_mt8192`, a static const array of 228 `struct mtk_pin_desc` entries from GPIO0 through GPIO227. Each entry records pin number, name, EINT mapping, drive group, and alternate mux functions.

The header is included by `pinctrl-mt8192.c`, which attaches the array to `mt8192_data` and combines it with MT8192 register-calculation ranges, base names, pull types, EINT hardware metadata, and pinconf callbacks. This file is the source of truth for MT8192 logical pin identities and mux-name/value mappings.

## Important APIs, Types, And Data

- `mtk_pins_mt8192`: static const `struct mtk_pin_desc` array.
- 228 `MTK_PIN` entries and 1119 `MTK_FUNCTION` entries.
- Most descriptors use `MTK_EINT_FUNCTION(0, n)`, but GPIO206-GPIO219 use `MTK_EINT_FUNCTION(NO_EINT_SUPPORT, NO_EINT_SUPPORT)`.
- All descriptors use `DRV_GRP4` in this header; there are no `DRV_FIXED` entries, even for pins without EINT support.
- Functions span SPI, I2S/TDM/PCM/DMIC audio, PWM, touch-panel GPIO, modem interrupts, USB ID/VBUS, PCIe request/reset/wake, GPS/antenna, keypad, DPI/display, camera, UART, I2C, SPMI, MSDC0/1/2, SCP, connectivity, power-wrap SPI, watchdog, RTC clock, and debug monitor functions.

## Control Flow

The file has no executable code. Its macro initializers are compiled into the including `pinctrl-mt8192.c` translation unit. During probe, the Paris core consumes `mt8192_data.pins`, registers every descriptor as a pin/group, and uses the function lists to validate and apply mux settings. Register writes are routed through `mt8192_reg_cals` in the companion `.c` file rather than being encoded here.

## State And Persistence

The header contributes immutable static metadata. It does not allocate memory or persist any runtime state. Hardware register state is managed by the common pinctrl and GPIO layers, with suspend/resume handled outside this header.

## Dependencies And Integration Points

- Depends directly on `pinctrl-paris.h` for the MediaTek descriptor macros and types.
- Included by `pinctrl-mt8192.c`, where `mt8192_data` sets `.pins = mtk_pins_mt8192`, `.npins` and `.ngrps` from `ARRAY_SIZE`, `.pull_type`, `.eint_hw`, `.nfuncs = 8`, `.gpio_m = 0`, and bias/drive callbacks.
- Must stay consistent with `mt8192_reg_cals`, register base names, and `mt8192_eint_hw` in the companion file.
- The `NO_EINT_SUPPORT` run for GPIO206-GPIO219 must be consistent with board expectations and EINT hardware `ap_num` limits.

## Risks

- GPIO206-GPIO219 are muxable but explicitly lack EINT support. Board code that assumes every GPIO-numbered pad can be an interrupt source will fail at runtime.
- Because all pins use `DRV_GRP4`, electrical drive behavior depends on the companion register ranges and common drive callbacks matching that simplification.
- The table has the largest pin count in this group. Any insertion or deletion shifts group indices and can alter how debugfs and pinctrl consumers identify pins.
- Sparse function alternatives and repeated peripheral names across A/B instances require device-tree authors to select exact mux values and physical pins.
- Late GPIO220-GPIO227 map back to EINT208-EINT216 with a gap, so interrupt numbering is not a simple identity across the whole file.

## Test Signals

- Build with MT8192 pinctrl enabled and verify descriptor count remains 228 for GPIO0-GPIO227.
- Probe on MT8192 hardware and check debugfs pin/group output.
- Apply DTS pin states for SPI, I2C, PCIe, USB, audio, camera/display, MSDC, SPMI, PWRAP, GPS/antenna, and connectivity pins.
- Verify that GPIO206-GPIO219 reject or skip EINT setup as expected while still supporting any valid mux functions.
- Exercise late EINT mappings for GPIO220-GPIO227 and compare against hardware interrupt behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8192.h -->
