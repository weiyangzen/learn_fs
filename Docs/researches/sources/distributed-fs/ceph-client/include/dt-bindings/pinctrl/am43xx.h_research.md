<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/am43xx.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/am43xx.h

Purpose: TI AM43xx pinctrl binding constants for mux modes, active/off-state pad bits, and IOPAD address helper.

Important APIs/types/functions: This header exports 36 DT-visible macros in the `pinctrl` binding namespace. Main API surface: `MUX_MODE*`, `PULL_*`, `INPUT_EN`, `DS0_*`, `PIN_*`, and `AM4372_IOPAD(pa, val)` compose pad register values. First exported macros: `MUX_MODE0`, `MUX_MODE1`, `MUX_MODE2`, `MUX_MODE3`, `MUX_MODE4`, `MUX_MODE5`, `MUX_MODE6`, `MUX_MODE7`. Last exported macros: `PIN_OUTPUT_PULLUP`, `PIN_OUTPUT_PULLDOWN`, `PIN_INPUT`, `PIN_INPUT_PULLUP`, `PIN_INPUT_PULLDOWN`, `AM4372_IOPAD(pa, val)`. Function-like/helper macros: `AM4372_IOPAD(pa, val)`

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: AM437x DTS pinctrl-single nodes use the helper to translate physical pad addresses to register offsets. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/am43xx.h -->
