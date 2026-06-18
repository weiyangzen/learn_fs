# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/sppctl.h

Purpose: `sppctl.h` is a Devicetree binding header for a pin controller. It exports numeric C preprocessor
constants that DTS files and provider drivers share as the ABI for phandle cells, selector values,
and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 11 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are SPPCTL (9), IOP_G (2).
Representative constants are `IOP_G_MASTE`, `IOP_G_FIRST`, `SPPCTL_PCTL_G_PMUX`,
`SPPCTL_PCTL_G_GPIO`, `SPPCTL_PCTL_G_IOPP`, `SPPCTL_PCTL_L_OUT`, `SPPCTL_PCTL_L_OU1`,
`SPPCTL_PCTL_L_INV`, `SPPCTL_PCTL_G_PMUX`, `SPPCTL_PCTL_G_GPIO`, `SPPCTL_PCTL_G_IOPP`,
`SPPCTL_PCTL_L_OUT`, `SPPCTL_PCTL_L_OU1`, `SPPCTL_PCTL_L_INV`, `SPPCTL_PCTL_L_ONV`,
`SPPCTL_PCTL_L_ODR`. Function-like helpers are `SPPCTL_IOPAD`. Value shape: 11 alias or symbol-
derived values; 1 function-like packing helpers.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_PINCTRL_SPPCTL_H__`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`SPPCTL group`, `IOP_G group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 31 lines long. Notable source comments include `Sunplus dt-bindings Pinctrl header
file`, `Output LOW`, `Output HIGH`, `Input Invert`, `Output Invert`, `Output Open Drain`. Example
value clusters are SPPCTL: `SPPCTL_PCTL_G_PMUX=(0x00 | IOP_G_MASTE)`,
`SPPCTL_PCTL_G_GPIO=(IOP_G_FIRST | IOP_G_MASTE)`, `SPPCTL_PCTL_G_IOPP=(IOP_G_FIRST | 0x00)`,
`SPPCTL_PCTL_L_OUT=(0x01 << 0) /* Output LOW */`; IOP_G: `IOP_G_MASTE=(0x01 << 0)`,
`IOP_G_FIRST=(0x01 << 1)`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `IOP_G_MASTE`, `IOP_G_FIRST`, `SPPCTL_PCTL_G_PMUX`, `SPPCTL_PCTL_G_GPIO`,
`SPPCTL_PCTL_G_IOPP`, `SPPCTL_PCTL_L_OUT`, `SPPCTL_PCTL_L_OU1`, `SPPCTL_PCTL_L_INV`. Test signals
include dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe logs, GPIO
loopback, and peripheral bring-up using representative mux groups.
