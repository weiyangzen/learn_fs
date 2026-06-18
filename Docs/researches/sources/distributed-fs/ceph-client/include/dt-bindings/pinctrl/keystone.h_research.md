<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/keystone.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/keystone.h

Purpose: TI Keystone pinctrl binding constants for mux modes, buffer class, pulls, and address translation.

Important APIs/types/functions: This header exports 15 DT-visible macros in the `pinctrl` binding namespace. Main API surface: `MUX_MODE0` through `MUX_MODE5`, `BUFFER_CLASS_*`, `PIN_PULL*`, `KEYSTONE_IOPAD_OFFSET(pa, offset)`, and `K2G_CORE_IOPAD(pa)` define pad selector cells. First exported macros: `MUX_MODE0`, `MUX_MODE1`, `MUX_MODE2`, `MUX_MODE3`, `MUX_MODE4`, `MUX_MODE5`, `BUFFER_CLASS_B`, `BUFFER_CLASS_C`. Last exported macros: `BUFFER_CLASS_E`, `PULL_DISABLE`, `PIN_PULLUP`, `PIN_PULLDOWN`, `KEYSTONE_IOPAD_OFFSET(pa, offset)`, `K2G_CORE_IOPAD(pa)`. Function-like/helper macros: `KEYSTONE_IOPAD_OFFSET(pa, offset)`, `K2G_CORE_IOPAD(pa)`

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: Keystone/K2G DTS pinctrl-single entries use these to form register offsets and config values. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/keystone.h -->
