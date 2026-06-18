<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/am33xx.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/am33xx.h

Purpose: TI AM33xx pinctrl binding constants for pad configuration and SoC pin offsets.

Important APIs/types/functions: This header exports 136 DT-visible macros in the `pinctrl` binding namespace. Main API surface: It includes OMAP pinctrl defaults, overrides pull/input bits for AM33xx, defines `PIN_*` convenience configs, and enumerates `AM335X_PIN_*` offsets from GPMC through USB drive-VBUS pins. First exported macros: `PULL_DISABLE`, `INPUT_EN`, `SLEWCTRL_SLOW`, `SLEWCTRL_FAST`, `PIN_OUTPUT`, `PIN_OUTPUT_PULLUP`, `PIN_OUTPUT_PULLDOWN`, `PIN_INPUT`. Last exported macros: `AM335X_PIN_RTC_PWRONRSTN`, `AM335X_PIN_PMIC_POWER_EN`, `AM335X_PIN_EXT_WAKEUP`, `AM335X_PIN_USB0_DRVVBUS`, `AM335X_PIN_USB1_DRVVBUS`, `AM335X_PIN_OFFSET_MAX`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: `<dt-bindings/pinctrl/omap.h>` It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: AM335x board DTS files use these offsets and config bits in pinctrl-single pad entries. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/am33xx.h -->
