<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt65xx.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt65xx.h

Purpose: Shared MediaTek pinctrl binding helpers and electrical configuration constants.

Important APIs/types/functions: This header exports 27 DT-visible macros in the `pinctrl` binding namespace. Main API surface: `MTK_PIN_NO(x)`, `MTK_GET_PIN_NO(x)`, and `MTK_GET_PIN_FUNC(x)` pack/unpack pinmux cells; `MTK_PUPD_SET_*`, `MTK_PULL_SET_RSEL_*`, and `MTK_DRIVE_*mA` expose pull/drive encodings. First exported macros: `MTK_PIN_NO(x)`, `MTK_GET_PIN_NO(x)`, `MTK_GET_PIN_FUNC(x)`, `MTK_PUPD_SET_R1R0_00`, `MTK_PUPD_SET_R1R0_01`, `MTK_PUPD_SET_R1R0_10`, `MTK_PUPD_SET_R1R0_11`, `MTK_PULL_SET_RSEL_000`. Last exported macros: `MTK_DRIVE_14mA`, `MTK_DRIVE_16mA`, `MTK_DRIVE_20mA`, `MTK_DRIVE_24mA`, `MTK_DRIVE_28mA`, `MTK_DRIVE_32mA`. Function-like/helper macros: `MTK_PIN_NO(x)`, `MTK_GET_PIN_NO(x)`, `MTK_GET_PIN_FUNC(x)`

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: MediaTek SoC-specific pinfunc headers include this file and depend on its packed-cell layout. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt65xx.h -->
