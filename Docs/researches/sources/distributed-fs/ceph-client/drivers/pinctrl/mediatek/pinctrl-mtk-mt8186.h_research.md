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
