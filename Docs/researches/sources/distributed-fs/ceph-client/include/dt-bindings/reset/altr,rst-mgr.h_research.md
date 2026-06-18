# sources/distributed-fs/ceph-client/include/dt-bindings/reset/altr,rst-mgr.h

Purpose: `altr,rst-mgr.h` is a Devicetree binding header for a reset-controller provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 63 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are CPU0 (1), CPU1 (1), WDS_RESET (1), SCUPER (1),
L2_RESET (1), EMAC0 (1), EMAC1 (1), USB0 (1), USB1 (1), NAND (1). Representative constants are
`CPU0_RESET`, `CPU1_RESET`, `WDS_RESET`, `SCUPER_RESET`, `L2_RESET`, `EMAC0_RESET`, `EMAC1_RESET`,
`USB0_RESET`, `...`, `TIMESTAMPCOLD_RESET`, `CLKMGRCOLD_RESET`, `SCANMGR_RESET`,
`FRZCTRLCOLD_RESET`, `SYSDBG_RESET`, `DBG_RESET`, `TAPCOLD_RESET`, `SDRCOLD_RESET`. Function-like
helpers are none. Value shape: literal numeric range 0..144 across 63 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_ALTR_RST_MGR_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MPUMODRST`, `PERMODRST`, `PER2MODRST`, `BRGMODRST`, `MISCMODRST`, which is the intended lookup
structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 82 lines long. Notable source comments include `MPUMODRST`, `PERMODRST`, `PER2MODRST`,
`BRGMODRST`, `MISCMODRST`. Example value clusters are CPU0: `CPU0_RESET=0`; CPU1: `CPU1_RESET=1`;
WDS_RESET: `WDS_RESET=2`; SCUPER: `SCUPER_RESET=3`; L2_RESET: `L2_RESET=4`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `CPU0_RESET`,
`CPU1_RESET`, `WDS_RESET`, `SCUPER_RESET`, `L2_RESET`, `EMAC0_RESET`, `EMAC1_RESET`, `USB0_RESET`.
Test signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
