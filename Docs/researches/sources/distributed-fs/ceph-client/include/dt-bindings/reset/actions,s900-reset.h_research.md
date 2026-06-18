# sources/distributed-fs/ceph-client/include/dt-bindings/reset/actions,s900-reset.h

Purpose: `actions,s900-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 54 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_DDR (2), RESET_GPU3D (2), RESET_CHIPID (1),
RESET_CPU (1), RESET_SRAMI (1), RESET_DMAC (1), RESET_GPIO (1), RESET_BISP (1), RESET_CSI0 (1),
RESET_CSI1 (1). Representative constants are `RESET_CHIPID`, `RESET_CPU_SCNT`, `RESET_SRAMI`,
`RESET_DDR_CTL_PHY`, `RESET_DMAC`, `RESET_GPIO`, `RESET_BISP_AXI`, `RESET_CSI0`, `...`,
`RESET_PCM0`, `RESET_SE`, `RESET_GIC`, `RESET_DDR_CTL_PHY_AXI`, `RESET_CMU_DDR`, `RESET_DMM`,
`RESET_HDCP2TX`, `RESET_ETHERNET`. Function-like helpers are none. Value shape: literal numeric
range 0..53 across 54 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_ACTIONS_S900_RESET_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RESET_DDR group`, `RESET_GPU3D group`, `RESET_CHIPID group`, `RESET_CPU group`, `RESET_SRAMI
group`, `RESET_DMAC group`, `RESET_GPIO group`, `RESET_BISP group`, `RESET_CSI0 group`, `RESET_CSI1
group`, `RESET_DE group`, `RESET_DSI group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 65 lines long. Notable source comments include `__DT_BINDINGS_ACTIONS_S900_RESET_H`.
Example value clusters are RESET_DDR: `RESET_DDR_CTL_PHY=3`, `RESET_DDR_CTL_PHY_AXI=49`;
RESET_GPU3D: `RESET_GPU3D_PA=11`, `RESET_GPU3D_PB=12`; RESET_CHIPID: `RESET_CHIPID=0`; RESET_CPU:
`RESET_CPU_SCNT=1`; RESET_SRAMI: `RESET_SRAMI=2`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_CHIPID`,
`RESET_CPU_SCNT`, `RESET_SRAMI`, `RESET_DDR_CTL_PHY`, `RESET_DMAC`, `RESET_GPIO`, `RESET_BISP_AXI`,
`RESET_CSI0`. Test signals include DTS compile checks, reset-controller probe, driver reset/deassert
paths, and peripheral reinitialization after module or runtime-PM cycles.
