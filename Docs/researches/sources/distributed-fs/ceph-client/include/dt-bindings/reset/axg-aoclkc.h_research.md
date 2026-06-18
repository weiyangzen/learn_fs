# sources/distributed-fs/ceph-client/include/dt-bindings/reset/axg-aoclkc.h

Purpose: `axg-aoclkc.h` is a Devicetree binding header for a reset-controller provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 6 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_AO (6). Representative constants are
`RESET_AO_REMOTE`, `RESET_AO_I2C_MASTER`, `RESET_AO_I2C_SLAVE`, `RESET_AO_UART1`, `RESET_AO_UART2`,
`RESET_AO_IR_BLASTER`, `RESET_AO_REMOTE`, `RESET_AO_I2C_MASTER`, `RESET_AO_I2C_SLAVE`,
`RESET_AO_UART1`, `RESET_AO_UART2`, `RESET_AO_IR_BLASTER`. Function-like helpers are none. Value
shape: literal numeric range 0..5 across 6 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDINGS_RESET_AMLOGIC_MESON_AXG_AOCLK`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `RESET_AO group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 20 lines long. Notable source comments include none. Example value clusters are
RESET_AO: `RESET_AO_REMOTE=0`, `RESET_AO_I2C_MASTER=1`, `RESET_AO_I2C_SLAVE=2`, `RESET_AO_UART1=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_AO_REMOTE`,
`RESET_AO_I2C_MASTER`, `RESET_AO_I2C_SLAVE`, `RESET_AO_UART1`, `RESET_AO_UART2`,
`RESET_AO_IR_BLASTER`. Test signals include DTS compile checks, reset-controller probe, driver
reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
