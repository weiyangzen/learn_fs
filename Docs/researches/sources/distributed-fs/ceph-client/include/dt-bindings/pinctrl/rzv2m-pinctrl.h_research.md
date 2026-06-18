# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/rzv2m-pinctrl.h

Purpose: `rzv2m-pinctrl.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering pinctrl pin, pad, mux, drive,
bias, or electrical configuration cells. The main macro families are RZV2M (3). Representative
constants are `RZV2M_PINS_PER_PORT`, `RZV2M_PINS_PER_PORT`. Function-like helpers are
`RZV2M_PORT_PINMUX`, `RZV2M_GPIO`. Value shape: literal numeric range 16..16 across 1 macros; 2
alias or symbol-derived values; 2 function-like packing helpers.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RZV2M_PINCTRL_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`Convert a port and pin label to its global pin index`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 23 lines long. Notable source comments include `This header provides constants for
Renesas RZ/V2M pinctrl bindings.`, `Create the pin index from its bank and position numbers and
store in the upper 16 bits the alternate function identifier`, `Convert a port and pin label to its
global pin index`, `__DT_BINDINGS_RZV2M_PINCTRL_H`. Example value clusters are RZV2M:
`RZV2M_PINS_PER_PORT=16`, `RZV2M_PORT_PINMUX=((b) * RZV2M_PINS_PER_PORT + (p) | ((f) << 16))`,
`RZV2M_GPIO=((port) * RZV2M_PINS_PER_PORT + (pin))`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `RZV2M_PINS_PER_PORT`, `RZV2M_PORT_PINMUX`, `RZV2M_GPIO`. Test signals include
dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe logs, GPIO loopback, and
peripheral bring-up using representative mux groups.
