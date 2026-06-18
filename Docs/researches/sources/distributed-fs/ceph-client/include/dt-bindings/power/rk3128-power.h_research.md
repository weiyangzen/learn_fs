# sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3128-power.h

Purpose: `rk3128-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 5 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3128 (5). Representative
constants are `RK3128_PD_CORE`, `RK3128_PD_VIO`, `RK3128_PD_VIDEO`, `RK3128_PD_GPU`,
`RK3128_PD_MSCH`, `RK3128_PD_CORE`, `RK3128_PD_VIO`, `RK3128_PD_VIDEO`, `RK3128_PD_GPU`,
`RK3128_PD_MSCH`. Function-like helpers are none. Value shape: literal numeric range 0..4 across 5
macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3128_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `VD_CORE`, `VD_LOGIC`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 14 lines long. Notable source comments include `VD_CORE`, `VD_LOGIC`. Example value
clusters are RK3128: `RK3128_PD_CORE=0`, `RK3128_PD_VIO=1`, `RK3128_PD_VIDEO=2`, `RK3128_PD_GPU=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3128_PD_CORE`, `RK3128_PD_VIO`, `RK3128_PD_VIDEO`, `RK3128_PD_GPU`, `RK3128_PD_MSCH`. Test
signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
