# sources/distributed-fs/ceph-client/include/dt-bindings/power/rockchip,rv1126b-power-controller.h

Purpose: `rockchip,rv1126b-power-controller.h` is a Devicetree binding header for a power-domain provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RV1126B (3). Representative
constants are `RV1126B_PD_NPU`, `RV1126B_PD_VDO`, `RV1126B_PD_AIISP`, `RV1126B_PD_NPU`,
`RV1126B_PD_VDO`, `RV1126B_PD_AIISP`. Function-like helpers are none. Value shape: literal numeric
range 0..2 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RV1126B_POWER_CONTROLLER_H__`; after preprocessing, DTS C-preprocessor users
and C drivers see only the constants and any packing helpers. Comment-delimited groups or observed
macro clusters are `VD_NPU`, `VD_LOGIC`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 17 lines long. Notable source comments include `VD_NPU`, `VD_LOGIC`. Example value
clusters are RV1126B: `RV1126B_PD_NPU=0`, `RV1126B_PD_VDO=1`, `RV1126B_PD_AIISP=2`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RV1126B_PD_NPU`, `RV1126B_PD_VDO`, `RV1126B_PD_AIISP`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
