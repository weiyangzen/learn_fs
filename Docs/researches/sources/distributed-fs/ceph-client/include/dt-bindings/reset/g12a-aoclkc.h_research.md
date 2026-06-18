# sources/distributed-fs/ceph-client/include/dt-bindings/reset/g12a-aoclkc.h

Purpose: `g12a-aoclkc.h` is a Devicetree binding header for a reset-controller provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 7 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_AO (7). Representative constants are
`RESET_AO_IR_IN`, `RESET_AO_UART`, `RESET_AO_I2C_M`, `RESET_AO_I2C_S`, `RESET_AO_SAR_ADC`,
`RESET_AO_UART2`, `RESET_AO_IR_OUT`, `RESET_AO_IR_IN`, `RESET_AO_UART`, `RESET_AO_I2C_M`,
`RESET_AO_I2C_S`, `RESET_AO_SAR_ADC`, `RESET_AO_UART2`, `RESET_AO_IR_OUT`. Function-like helpers are
none. Value shape: literal numeric range 0..6 across 7 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDINGS_RESET_AMLOGIC_MESON_G12A_AOCLK`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `RESET_AO group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 18 lines long. Notable source comments include none. Example value clusters are
RESET_AO: `RESET_AO_IR_IN=0`, `RESET_AO_UART=1`, `RESET_AO_I2C_M=2`, `RESET_AO_I2C_S=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_AO_IR_IN`,
`RESET_AO_UART`, `RESET_AO_I2C_M`, `RESET_AO_I2C_S`, `RESET_AO_SAR_ADC`, `RESET_AO_UART2`,
`RESET_AO_IR_OUT`. Test signals include DTS compile checks, reset-controller probe, driver
reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
