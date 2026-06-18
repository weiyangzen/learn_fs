# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-a1-reset.h

Purpose: `amlogic,meson-a1-reset.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 42 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_I2C (7), RESET_PWM (3), RESET_UART (3),
RESET_AM2AXI (2), RESET_AUDIO (2), RESET_NIC (2), RESET_PSRAM (1), RESET_PAD (1), RESET_TEMP (1),
RESET_SPICC (1). Representative constants are `RESET_AM2AXI_VAD`, `RESET_PSRAM`, `RESET_PAD_CTRL`,
`RESET_TEMP_SENSOR`, `RESET_AM2AXI_DEV`, `RESET_SPICC_A`, `RESET_MSR_CLK`, `RESET_AUDIO`, `...`,
`RESET_RAMB`, `RESET_ROM`, `RESET_SPIFC`, `RESET_GIC`, `RESET_UART_C`, `RESET_UART_B`,
`RESET_UART_A`, `RESET_OSC_RING`. Function-like helpers are none. Value shape: literal numeric range
1..59 across 42 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_MESON_A1_RESET_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RESET0`, `2-3`, `30-31`, `RESET1`, `39-41`, `51-52`, `60-63`, `RESET2`, `64-95`, which is the
intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 74 lines long. Notable source comments include `RESET0`, `0`, `2-3`, `6`, `9`, `20`.
Example value clusters are RESET_I2C: `RESET_I2C_S_A=22`, `RESET_I2C_M_D=24`, `RESET_I2C_M_C=25`,
`RESET_I2C_M_B=26`; RESET_PWM: `RESET_PWM_EF=17`, `RESET_PWM_CD=18`, `RESET_PWM_AB=19`; RESET_UART:
`RESET_UART_C=56`, `RESET_UART_B=57`, `RESET_UART_A=58`; RESET_AM2AXI: `RESET_AM2AXI_VAD=1`,
`RESET_AM2AXI_DEV=8`; RESET_AUDIO: `RESET_AUDIO=12`, `RESET_AUDIO_VAD=15`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_AM2AXI_VAD`,
`RESET_PSRAM`, `RESET_PAD_CTRL`, `RESET_TEMP_SENSOR`, `RESET_AM2AXI_DEV`, `RESET_SPICC_A`,
`RESET_MSR_CLK`, `RESET_AUDIO`. Test signals include DTS compile checks, reset-controller probe,
driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
