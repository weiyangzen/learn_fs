# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/stm32-pinfunc.h

Purpose: `stm32-pinfunc.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 28 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are STM32MP (7), GPIO (1),
AF0 (1), AF1 (1), AF2 (1), AF3 (1), AF4 (1), AF5 (1), AF6 (1), AF7 (1). Representative constants are
`GPIO`, `AF0`, `AF1`, `AF2`, `AF3`, `AF4`, `AF5`, `AF6`, `...`, `RSVD`, `STM32MP_PKG_AA`,
`STM32MP_PKG_AB`, `STM32MP_PKG_AC`, `STM32MP_PKG_AD`, `STM32MP_PKG_AI`, `STM32MP_PKG_AK`,
`STM32MP_PKG_AL`. Function-like helpers are `PIN_NO`, `STM32_PINMUX`. Value shape: literal numeric
range 0..2048 across 26 macros; 2 alias or symbol-derived values; 2 function-like packing helpers.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_STM32_PINFUNC_H`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`define PIN modes`, `define Pins number`, `package information`, which is the intended lookup
structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 46 lines long. Notable source comments include `define PIN modes`, `define Pins number`,
`package information`, `_DT_BINDINGS_STM32_PINFUNC_H`. Example value clusters are STM32MP:
`STM32MP_PKG_AA=0x1`, `STM32MP_PKG_AB=0x2`, `STM32MP_PKG_AC=0x4`, `STM32MP_PKG_AD=0x8`; GPIO:
`GPIO=0x0`; AF0: `AF0=0x1`; AF1: `AF1=0x2`; AF2: `AF2=0x3`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `GPIO`, `AF0`, `AF1`, `AF2`, `AF3`, `AF4`, `AF5`, `AF6`. Test signals include
dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe logs, GPIO loopback, and
peripheral bring-up using representative mux groups.
