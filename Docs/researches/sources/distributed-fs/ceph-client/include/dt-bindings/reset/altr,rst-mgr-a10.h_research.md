# sources/distributed-fs/ceph-client/include/dt-bindings/reset/altr,rst-mgr-a10.h

Purpose: `altr,rst-mgr-a10.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 72 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are EMAC0 (2), EMAC1 (2), EMAC2 (2), USB0 (2), USB1 (2),
NAND (2), QSPI (2), SDMMC (2), OCRAM (2), CPU0 (1). Representative constants are `CPU0_RESET`,
`CPU1_RESET`, `WDS_RESET`, `SCUPER_RESET`, `EMAC0_RESET`, `EMAC1_RESET`, `EMAC2_RESET`,
`USB0_RESET`, `...`, `CLKMGRCOLD_RESET`, `S2FCOLD_RESET`, `TIMESTAMPCOLD_RESET`, `TAPCOLD_RESET`,
`HMCCOLD_RESET`, `IOMGRCOLD_RESET`, `NRSTPINOE_RESET`, `DBG_RESET`. Function-like helpers are none.
Value shape: literal numeric range 0..224 across 72 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_ALTR_RST_MGR_A10_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `MPUMODRST`, `PER0MODRST`, `55 is empty`, `PER1MODRST`, `70-71 is reserved`, `77-79 is
reserved`, `82-87 is reserved`, `BRGMODRST`, `SYSMODRST`, `130 is reserved`, `COLDMODRST`, `161-162
is reserved`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 102 lines long. Notable source comments include `MPUMODRST`, `PER0MODRST`, `55 is
empty`, `PER1MODRST`, `70-71 is reserved`, `77-79 is reserved`. Example value clusters are EMAC0:
`EMAC0_RESET=32`, `EMAC0_OCP_RESET=40`; EMAC1: `EMAC1_RESET=33`, `EMAC1_OCP_RESET=41`; EMAC2:
`EMAC2_RESET=34`, `EMAC2_OCP_RESET=42`; USB0: `USB0_RESET=35`, `USB0_OCP_RESET=43`; USB1:
`USB1_RESET=36`, `USB1_OCP_RESET=44`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `CPU0_RESET`,
`CPU1_RESET`, `WDS_RESET`, `SCUPER_RESET`, `EMAC0_RESET`, `EMAC1_RESET`, `EMAC2_RESET`,
`USB0_RESET`. Test signals include DTS compile checks, reset-controller probe, driver reset/deassert
paths, and peripheral reinitialization after module or runtime-PM cycles.
