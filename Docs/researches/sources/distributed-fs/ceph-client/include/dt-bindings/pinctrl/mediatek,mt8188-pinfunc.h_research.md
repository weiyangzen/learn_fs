<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mediatek,mt8188-pinfunc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mediatek,mt8188-pinfunc.h

Purpose: MediaTek MT8188 pin-function binding constants for every GPIO alternate function.

Important APIs/types/functions: This header exports 1091 DT-visible macros in the `pinctrl` binding namespace. Main API surface: It includes `mt65xx.h` and defines more than one thousand `PINMUX_GPIO<n>__FUNC_*` entries built with `MTK_PIN_NO(n) | function`, covering GPIO, SPI, UART, I2S, DMIC, debug monitor, SPMI, LVTS, JTAG, MSDC, and many SoC-specific signals. First exported macros: `PINMUX_GPIO0__FUNC_B_GPIO0`, `PINMUX_GPIO0__FUNC_B0_TP_GPIO0_AO`, `PINMUX_GPIO0__FUNC_O_SPIM5_CSB`, `PINMUX_GPIO0__FUNC_O_UTXD1`, `PINMUX_GPIO0__FUNC_O_DMIC3_CLK`, `PINMUX_GPIO0__FUNC_B0_I2SIN_MCK`, `PINMUX_GPIO0__FUNC_O_I2SO2_MCK`, `PINMUX_GPIO0__FUNC_B0_DBG_MON_A0`. Last exported macros: `PINMUX_GPIO174__FUNC_B1_MSDC2_DAT3`, `PINMUX_GPIO174__FUNC_I0_LVTS_SDI`, `PINMUX_GPIO175__FUNC_B_GPIO175`, `PINMUX_GPIO175__FUNC_B0_SPMI_M_SCL`, `PINMUX_GPIO176__FUNC_B_GPIO176`, `PINMUX_GPIO176__FUNC_B0_SPMI_M_SDA`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: `"mt65xx.h"` It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: MT8188 DTS pinmux entries use these constants as the ABI between board descriptions and the MediaTek pinctrl driver. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mediatek,mt8188-pinfunc.h -->
