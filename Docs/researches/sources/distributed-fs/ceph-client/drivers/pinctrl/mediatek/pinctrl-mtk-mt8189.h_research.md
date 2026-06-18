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
