# sources/distributed-fs/ceph-client/include/dt-bindings/reset/econet,en751221-scu.h

Purpose: `econet,en751221-scu.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 42 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are EN751221 (42). Representative constants are
`EN751221_XPON_PHY_RST`, `EN751221_PCM1_ZSI_ISI_RST`, `EN751221_FE_QDMA1_RST`,
`EN751221_FE_QDMA2_RST`, `EN751221_FE_UNZIP_RST`, `EN751221_PCM2_RST`, `EN751221_PTM_MAC_RST`,
`EN751221_CRYPTO_RST`, `...`, `EN751221_UART4_RST`, `EN751221_UART5_RST`, `EN751221_I2C2_RST`,
`EN751221_XSI_MAC_RST`, `EN751221_XSI_PHY_RST`, `EN751221_DMT_RST`, `EN751221_USB_PHY_P0_RST`,
`EN751221_USB_PHY_P1_RST`. Function-like helpers are none. Value shape: literal numeric range 0..41
across 42 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RESET_CONTROLLER_ECONET_EN751221_H_`; after preprocessing, DTS C-preprocessor users
and C drivers see only the constants and any packing helpers. Comment-delimited groups or observed
macro clusters are `EN751221 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 49 lines long. Notable source comments include
`__DT_BINDINGS_RESET_CONTROLLER_ECONET_EN751221_H_`. Example value clusters are EN751221:
`EN751221_XPON_PHY_RST=0`, `EN751221_PCM1_ZSI_ISI_RST=1`, `EN751221_FE_QDMA1_RST=2`,
`EN751221_FE_QDMA2_RST=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`EN751221_XPON_PHY_RST`, `EN751221_PCM1_ZSI_ISI_RST`, `EN751221_FE_QDMA1_RST`,
`EN751221_FE_QDMA2_RST`, `EN751221_FE_UNZIP_RST`, `EN751221_PCM2_RST`, `EN751221_PTM_MAC_RST`,
`EN751221_CRYPTO_RST`. Test signals include DTS compile checks, reset-controller probe, driver
reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
