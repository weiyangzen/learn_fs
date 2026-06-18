# sources/distributed-fs/ceph-client/include/dt-bindings/reset/actions,s500-reset.h

Purpose: `actions,s500-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 54 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_USB2 (2), RESET_DMAC (1), RESET_NORIF (1),
RESET_DDR (1), RESET_NANDC (1), RESET_SD0 (1), RESET_SD1 (1), RESET_PCM1 (1), RESET_DE (1),
RESET_LCD (1). Representative constants are `RESET_DMAC`, `RESET_NORIF`, `RESET_DDR`, `RESET_NANDC`,
`RESET_SD0`, `RESET_SD1`, `RESET_PCM1`, `RESET_DE`, `...`, `RESET_WD0RESET`, `RESET_WD1RESET`,
`RESET_WD2RESET`, `RESET_WD3RESET`, `RESET_DBG0RESET`, `RESET_DBG1RESET`, `RESET_DBG2RESET`,
`RESET_DBG3RESET`. Function-like helpers are none. Value shape: literal numeric range 0..53 across
54 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_ACTIONS_S500_RESET_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RESET_USB2 group`, `RESET_DMAC group`, `RESET_NORIF group`, `RESET_DDR group`, `RESET_NANDC
group`, `RESET_SD0 group`, `RESET_SD1 group`, `RESET_PCM1 group`, `RESET_DE group`, `RESET_LCD
group`, `RESET_SD2 group`, `RESET_DSI group`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 67 lines long. Notable source comments include `Device Tree binding constants for
Actions Semi S500 Reset Management Unit`, `__DT_BINDINGS_ACTIONS_S500_RESET_H`. Example value
clusters are RESET_USB2: `RESET_USB2_0=23`, `RESET_USB2_1=45`; RESET_DMAC: `RESET_DMAC=0`;
RESET_NORIF: `RESET_NORIF=1`; RESET_DDR: `RESET_DDR=2`; RESET_NANDC: `RESET_NANDC=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_DMAC`,
`RESET_NORIF`, `RESET_DDR`, `RESET_NANDC`, `RESET_SD0`, `RESET_SD1`, `RESET_PCM1`, `RESET_DE`. Test
signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
