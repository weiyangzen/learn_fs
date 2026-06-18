# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/rzg2l-pinctrl.h

Purpose: `rzg2l-pinctrl.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering pinctrl pin, pad, mux, drive,
bias, or electrical configuration cells. The main macro families are RZG2L (3). Representative
constants are `RZG2L_PINS_PER_PORT`, `RZG2L_PINS_PER_PORT`. Function-like helpers are
`RZG2L_PORT_PINMUX`, `RZG2L_GPIO`. Value shape: literal numeric range 8..8 across 1 macros; 2 alias
or symbol-derived values; 2 function-like packing helpers.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RZG2L_PINCTRL_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`Convert a port and pin label to its global pin index`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 23 lines long. Notable source comments include `This header provides constants for
Renesas RZ/G2L family pinctrl bindings.`, `Create the pin index from its bank and position numbers
and store in the upper 16 bits the alternate function identifier`, `Convert a port and pin label to
its global pin index`, `__DT_BINDINGS_RZG2L_PINCTRL_H`. Example value clusters are RZG2L:
`RZG2L_PINS_PER_PORT=8`, `RZG2L_PORT_PINMUX=((b) * RZG2L_PINS_PER_PORT + (p) | ((f) << 16))`,
`RZG2L_GPIO=((port) * RZG2L_PINS_PER_PORT + (pin))`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `RZG2L_PINS_PER_PORT`, `RZG2L_PORT_PINMUX`, `RZG2L_GPIO`. Test signals include
dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe logs, GPIO loopback, and
peripheral bring-up using representative mux groups.
