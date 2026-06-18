<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/lochnagar.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/lochnagar.h

Purpose: Cirrus Logic Lochnagar audio evaluation board pinctrl binding constants.

Important APIs/types/functions: This header exports 116 DT-visible macros in the `pinctrl` binding namespace. Main API surface: The API enumerates Lochnagar1 and Lochnagar2 logical pins, including codec/DSP resets, CIF modes, FPGA GPIOs, SPDIF/I2C/SPI/GF GPIOs, clocks, and DSP GPIOs, ending in per-device `*_NUM_GPIOS` bounds. First exported macros: `LOCHNAGAR1_PIN_CDC_RESET`, `LOCHNAGAR1_PIN_DSP_RESET`, `LOCHNAGAR1_PIN_CDC_CIF1MODE`, `LOCHNAGAR1_PIN_NUM_GPIOS`, `LOCHNAGAR2_PIN_CDC_RESET`, `LOCHNAGAR2_PIN_DSP_RESET`, `LOCHNAGAR2_PIN_CDC_CIF1MODE`, `LOCHNAGAR2_PIN_CDC_LDOENA`. Last exported macros: `LOCHNAGAR2_PIN_PSIA1_MCLK`, `LOCHNAGAR2_PIN_PSIA2_MCLK`, `LOCHNAGAR2_PIN_GF_GPIO1`, `LOCHNAGAR2_PIN_GF_GPIO5`, `LOCHNAGAR2_PIN_DSP_GPIO20`, `LOCHNAGAR2_PIN_NUM_GPIOS`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The Lochnagar MFD/pinctrl driver uses these IDs to expose board-level pin and GPIO routing. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/lochnagar.h -->
