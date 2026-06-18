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
