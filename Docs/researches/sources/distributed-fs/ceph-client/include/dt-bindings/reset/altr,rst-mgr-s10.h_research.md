# sources/distributed-fs/ceph-client/include/dt-bindings/reset/altr,rst-mgr-s10.h

Purpose: `altr,rst-mgr-s10.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 68 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are EMAC0 (2), EMAC1 (2), EMAC2 (2), USB0 (2), USB1 (2),
NAND (2), SDMMC (2), CPU0 (1), CPU1 (1), CPU2 (1). Representative constants are `CPU0_RESET`,
`CPU1_RESET`, `CPU2_RESET`, `CPU3_RESET`, `EMAC0_RESET`, `EMAC1_RESET`, `EMAC2_RESET`, `USB0_RESET`,
`...`, `CPUPO0_RESET`, `CPUPO1_RESET`, `CPUPO2_RESET`, `CPUPO3_RESET`, `L2_RESET`, `DBG_RESET`,
`CSDAP_RESET`, `TAP_RESET`. Function-like helpers are none. Value shape: literal numeric range
0..256 across 68 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_ALTR_RST_MGR_S10_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `MPUMODRST`, `PER0MODRST`, `38 is empty`, `46 is empty`, `55 is empty`, `PER1MODRST`, `79 is
empty`, `82-87 is empty`, `BRGMODRST`, `COLDMODRST`, `164-167 is empty`, `DBGMODRST`, which is the
intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 100 lines long. Notable source comments include `derived from Steffen Trumtrar's
"altr,rst-mgr-a10.h"`, `MPUMODRST`, `PER0MODRST`, `38 is empty`, `46 is empty`, `55 is empty`.
Example value clusters are EMAC0: `EMAC0_RESET=32`, `EMAC0_OCP_RESET=40`; EMAC1: `EMAC1_RESET=33`,
`EMAC1_OCP_RESET=41`; EMAC2: `EMAC2_RESET=34`, `EMAC2_OCP_RESET=42`; USB0: `USB0_RESET=35`,
`USB0_OCP_RESET=43`; USB1: `USB1_RESET=36`, `USB1_OCP_RESET=44`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `CPU0_RESET`,
`CPU1_RESET`, `CPU2_RESET`, `CPU3_RESET`, `EMAC0_RESET`, `EMAC1_RESET`, `EMAC2_RESET`, `USB0_RESET`.
Test signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
