# sources/distributed-fs/ceph-client/include/dt-bindings/reset/canaan,k230-rst.h

Purpose: `canaan,k230-rst.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 80 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RST_SHRM (3), RST_ISP (3), RST_CPU0 (2), RST_CPU1
(2), RST_HISYS (2), RST_USB0 (2), RST_USB1 (2), RST_WDT0 (2), RST_WDT1 (2), RST_GPIO (2).
Representative constants are `RST_CPU0`, `RST_CPU1`, `RST_CPU0_FLUSH`, `RST_CPU1_FLUSH`, `RST_AI`,
`RST_VPU`, `RST_HISYS`, `RST_HISYS_AHB`, `...`, `RST_CSI1`, `RST_CSI2`, `RST_CSI_DPHY`,
`RST_ISP_AHB`, `RST_M0`, `RST_M1`, `RST_M2`, `RST_SPI2AXI`. Function-like helpers are none. Value
shape: literal numeric range 0..79 across 80 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_CANAAN_K230_RST_H_`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`RST_SHRM group`, `RST_ISP group`, `RST_CPU0 group`, `RST_CPU1 group`, `RST_HISYS group`, `RST_USB0
group`, `RST_USB1 group`, `RST_WDT0 group`, `RST_WDT1 group`, `RST_GPIO group`, `RST_ADC group`,
`RST_AI group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 90 lines long. Notable source comments include none. Example value clusters are
RST_SHRM: `RST_SHRM_AXIM=23`, `RST_SHRM_AXIS=24`, `RST_SHRM_APB=70`; RST_ISP: `RST_ISP=27`,
`RST_ISP_DW=28`, `RST_ISP_AHB=75`; RST_CPU0: `RST_CPU0=0`, `RST_CPU0_FLUSH=2`; RST_CPU1:
`RST_CPU1=1`, `RST_CPU1_FLUSH=3`; RST_HISYS: `RST_HISYS=6`, `RST_HISYS_AHB=7`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RST_CPU0`, `RST_CPU1`,
`RST_CPU0_FLUSH`, `RST_CPU1_FLUSH`, `RST_AI`, `RST_VPU`, `RST_HISYS`, `RST_HISYS_AHB`. Test signals
include DTS compile checks, reset-controller probe, driver reset/deassert paths, and peripheral
reinitialization after module or runtime-PM cycles.
