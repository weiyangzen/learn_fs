# sources/distributed-fs/ceph-client/include/dt-bindings/reset/altr,rst-mgr-a10sr.h

Purpose: `altr,rst-mgr-a10sr.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 6 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are A10SR (6). Representative constants are
`A10SR_RESET_ENET_HPS`, `A10SR_RESET_PCIE`, `A10SR_RESET_FILE`, `A10SR_RESET_BQSPI`,
`A10SR_RESET_USB`, `A10SR_RESET_NUM`, `A10SR_RESET_ENET_HPS`, `A10SR_RESET_PCIE`,
`A10SR_RESET_FILE`, `A10SR_RESET_BQSPI`, `A10SR_RESET_USB`, `A10SR_RESET_NUM`. Function-like helpers
are none. Value shape: literal numeric range 0..5 across 6 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_ALTR_RST_MGR_A10SR_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `Peripheral PHY resets`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 22 lines long. Notable source comments include `Reset binding definitions for Altera
Arria10 MAX5 System Resource Chip Adapted from altr,rst-mgr-a10.h`, `Peripheral PHY resets`. Example
value clusters are A10SR: `A10SR_RESET_ENET_HPS=0`, `A10SR_RESET_PCIE=1`, `A10SR_RESET_FILE=2`,
`A10SR_RESET_BQSPI=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `A10SR_RESET_ENET_HPS`,
`A10SR_RESET_PCIE`, `A10SR_RESET_FILE`, `A10SR_RESET_BQSPI`, `A10SR_RESET_USB`, `A10SR_RESET_NUM`.
Test signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
