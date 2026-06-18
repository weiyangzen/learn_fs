<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/arizona.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mfd/arizona.h

Purpose: Cirrus/Wolfson Arizona MFD device-tree constants for GPIO function selection, GPIO config flags, clock selection, DMIC routing, input mode, MICD timing, accessory detect, and GPSW state.

Important APIs/types/functions: This header exports 89 DT-visible macros in the `mfd` binding namespace. Main API surface: `ARIZONA_GP_FN_*` values describe pin alternate functions; `ARIZONA_GPN_*` bits compose GPIO configuration words; convenience macros such as `ARIZONA_GP_INPUT` combine function and direction. First exported macros: `ARIZONA_GP_FN_TXLRCLK`, `ARIZONA_GP_FN_GPIO`, `ARIZONA_GP_FN_IRQ1`, `ARIZONA_GP_FN_IRQ2`, `ARIZONA_GP_FN_OPCLK`, `ARIZONA_GP_FN_FLL1_OUT`, `ARIZONA_GP_FN_FLL2_OUT`, `ARIZONA_GP_FN_PWM1`. Last exported macros: `ARIZONA_ACCDET_MODE_HPM`, `ARIZONA_ACCDET_MODE_ADC`, `ARIZONA_GPSW_OPEN`, `ARIZONA_GPSW_CLOSED`, `ARIZONA_GPSW_CLAMP_ENABLED`, `ARIZONA_GPSW_CLAMP_DISABLED`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The codec/MFD GPIO, clock, jack-detect, and audio routing drivers decode these values from board DT properties. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/arizona.h -->
