# sources/distributed-fs/ceph-client/include/dt-bindings/power/marvell,pxa1908-power.h

Purpose: `marvell,pxa1908-power.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 6 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PXA1908 (6). Representative
constants are `PXA1908_POWER_DOMAIN_VPU`, `PXA1908_POWER_DOMAIN_GPU`, `PXA1908_POWER_DOMAIN_GPU2D`,
`PXA1908_POWER_DOMAIN_DSI`, `PXA1908_POWER_DOMAIN_ISP`, `PXA1908_POWER_DOMAIN_AUDIO`,
`PXA1908_POWER_DOMAIN_VPU`, `PXA1908_POWER_DOMAIN_GPU`, `PXA1908_POWER_DOMAIN_GPU2D`,
`PXA1908_POWER_DOMAIN_DSI`, `PXA1908_POWER_DOMAIN_ISP`, `PXA1908_POWER_DOMAIN_AUDIO`. Function-like
helpers are none. Value shape: literal numeric range 0..5 across 6 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DTS_MARVELL_PXA1908_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PXA1908 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 18 lines long. Notable source comments include `Marvell PXA1908 power domains`. Example
value clusters are PXA1908: `PXA1908_POWER_DOMAIN_VPU=0`, `PXA1908_POWER_DOMAIN_GPU=1`,
`PXA1908_POWER_DOMAIN_GPU2D=2`, `PXA1908_POWER_DOMAIN_DSI=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PXA1908_POWER_DOMAIN_VPU`, `PXA1908_POWER_DOMAIN_GPU`, `PXA1908_POWER_DOMAIN_GPU2D`,
`PXA1908_POWER_DOMAIN_DSI`, `PXA1908_POWER_DOMAIN_ISP`, `PXA1908_POWER_DOMAIN_AUDIO`. Test signals
include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
