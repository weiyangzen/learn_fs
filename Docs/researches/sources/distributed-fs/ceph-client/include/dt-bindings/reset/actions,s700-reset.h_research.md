# sources/distributed-fs/ceph-client/include/dt-bindings/reset/actions,s700-reset.h

Purpose: `actions,s700-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 23 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_AUDIO (1), RESET_CSI (1), RESET_DE (1),
RESET_DSI (1), RESET_GPIO (1), RESET_I2C0 (1), RESET_I2C1 (1), RESET_I2C2 (1), RESET_I2C3 (1),
RESET_KEY (1). Representative constants are `RESET_AUDIO`, `RESET_CSI`, `RESET_DE`, `RESET_DSI`,
`RESET_GPIO`, `RESET_I2C0`, `RESET_I2C1`, `RESET_I2C2`, `...`, `RESET_SPI3`, `RESET_UART0`,
`RESET_UART1`, `RESET_UART2`, `RESET_UART3`, `RESET_UART4`, `RESET_UART5`, `RESET_UART6`. Function-
like helpers are none. Value shape: literal numeric range 0..22 across 23 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_ACTIONS_S700_RESET_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RESET_AUDIO group`, `RESET_CSI group`, `RESET_DE group`, `RESET_DSI group`, `RESET_GPIO group`,
`RESET_I2C0 group`, `RESET_I2C1 group`, `RESET_I2C2 group`, `RESET_I2C3 group`, `RESET_KEY group`,
`RESET_LCD0 group`, `RESET_SI group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 34 lines long. Notable source comments include `__DT_BINDINGS_ACTIONS_S700_RESET_H`.
Example value clusters are RESET_AUDIO: `RESET_AUDIO=0`; RESET_CSI: `RESET_CSI=1`; RESET_DE:
`RESET_DE=2`; RESET_DSI: `RESET_DSI=3`; RESET_GPIO: `RESET_GPIO=4`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_AUDIO`,
`RESET_CSI`, `RESET_DE`, `RESET_DSI`, `RESET_GPIO`, `RESET_I2C0`, `RESET_I2C1`, `RESET_I2C2`. Test
signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
