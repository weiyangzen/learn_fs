<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6779-pinfunc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6779-pinfunc.h

Purpose: MediaTek MT6779 pin-function binding constants for GPIO alternate functions.

Important APIs/types/functions: This header exports 1019 DT-visible macros in the `pinctrl` binding namespace. Main API surface: It includes the shared `mt65xx.h` helpers and defines `PINMUX_GPIO<n>__FUNC_*` values for GPIO0 through GPIO209, covering SPI, I2S/TDM/PCM, I2C, UART, touch panel, antenna/PTA, display, camera, debug, and clock monitor functions. First exported macros: `PINMUX_GPIO0__FUNC_GPIO0`, `PINMUX_GPIO0__FUNC_SPI6_MI`, `PINMUX_GPIO0__FUNC_I2S5_LRCK`, `PINMUX_GPIO0__FUNC_TDM_LRCK_2ND`, `PINMUX_GPIO0__FUNC_PCM1_SYNC`, `PINMUX_GPIO0__FUNC_SCL_6306`, `PINMUX_GPIO0__FUNC_TP_GPIO0_AO`, `PINMUX_GPIO0__FUNC_PTA_RXD`. Last exported macros: `PINMUX_GPIO204__FUNC_GPIO204`, `PINMUX_GPIO205__FUNC_GPIO205`, `PINMUX_GPIO206__FUNC_GPIO206`, `PINMUX_GPIO207__FUNC_GPIO207`, `PINMUX_GPIO208__FUNC_GPIO208`, `PINMUX_GPIO209__FUNC_GPIO209`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: `<dt-bindings/pinctrl/mt65xx.h>` It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: MT6779 DTS pinmux properties use these constants to select SoC pin alternate functions. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6779-pinfunc.h -->
