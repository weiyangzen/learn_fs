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
