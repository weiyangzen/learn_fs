# sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun60i-a733-pck-600.h

Purpose: `allwinner,sun60i-a733-pck-600.h` is a Devicetree binding header for a power-domain provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 11 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PD_VE (2), PD_GPU (2), PD_VI (1),
PD_DE (1), PD_NPU (1), PD_PCIE (1), PD_USB2 (1), PD_VO (1), PD_VO1 (1). Representative constants are
`PD_VI`, `PD_DE_SYS`, `PD_VE_DEC`, `PD_VE_ENC`, `PD_NPU`, `PD_GPU_TOP`, `PD_GPU_CORE`, `PD_PCIE`,
`PD_VE_ENC`, `PD_NPU`, `PD_GPU_TOP`, `PD_GPU_CORE`, `PD_PCIE`, `PD_USB2`, `PD_VO`, `PD_VO1`.
Function-like helpers are none. Value shape: literal numeric range 0..10 across 11 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_SUN60I_A733_PCK600_H_`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `PD_VE group`, `PD_GPU group`, `PD_VI group`, `PD_DE group`, `PD_NPU group`, `PD_PCIE
group`, `PD_USB2 group`, `PD_VO group`, `PD_VO1 group`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 18 lines long. Notable source comments include
`_DT_BINDINGS_POWER_SUN60I_A733_PCK600_H_`. Example value clusters are PD_VE: `PD_VE_DEC=2`,
`PD_VE_ENC=3`; PD_GPU: `PD_GPU_TOP=5`, `PD_GPU_CORE=6`; PD_VI: `PD_VI=0`; PD_DE: `PD_DE_SYS=1`;
PD_NPU: `PD_NPU=4`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PD_VI`, `PD_DE_SYS`, `PD_VE_DEC`, `PD_VE_ENC`, `PD_NPU`, `PD_GPU_TOP`, `PD_GPU_CORE`, `PD_PCIE`.
Test signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
