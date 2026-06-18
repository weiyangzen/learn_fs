# sources/distributed-fs/ceph-client/include/dt-bindings/reset/bt1-ccu.h

Purpose: `bt1-ccu.h` is a Devicetree binding header for a reset-controller provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 22 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are CCU_AXI (11), CCU_SYS (11). Representative constants
are `CCU_AXI_MAIN_RST`, `CCU_AXI_DDR_RST`, `CCU_AXI_SATA_RST`, `CCU_AXI_GMAC0_RST`,
`CCU_AXI_GMAC1_RST`, `CCU_AXI_XGMAC_RST`, `CCU_AXI_PCIE_M_RST`, `CCU_AXI_PCIE_S_RST`, `...`,
`CCU_SYS_DDR_INIT_RST`, `CCU_SYS_PCIE_PCS_PHY_RST`, `CCU_SYS_PCIE_PIPE0_RST`,
`CCU_SYS_PCIE_CORE_RST`, `CCU_SYS_PCIE_PWR_RST`, `CCU_SYS_PCIE_STICKY_RST`,
`CCU_SYS_PCIE_NSTICKY_RST`, `CCU_SYS_PCIE_HOT_RST`. Function-like helpers are none. Value shape:
literal numeric range 0..10 across 22 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RESET_BT1_CCU_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`CCU_AXI group`, `CCU_SYS group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 34 lines long. Notable source comments include `Baikal-T1 CCU reset indices`,
`__DT_BINDINGS_RESET_BT1_CCU_H`. Example value clusters are CCU_AXI: `CCU_AXI_MAIN_RST=0`,
`CCU_AXI_DDR_RST=1`, `CCU_AXI_SATA_RST=2`, `CCU_AXI_GMAC0_RST=3`; CCU_SYS: `CCU_SYS_SATA_REF_RST=0`,
`CCU_SYS_APB_RST=1`, `CCU_SYS_DDR_FULL_RST=2`, `CCU_SYS_DDR_INIT_RST=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `CCU_AXI_MAIN_RST`,
`CCU_AXI_DDR_RST`, `CCU_AXI_SATA_RST`, `CCU_AXI_GMAC0_RST`, `CCU_AXI_GMAC1_RST`,
`CCU_AXI_XGMAC_RST`, `CCU_AXI_PCIE_M_RST`, `CCU_AXI_PCIE_S_RST`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
