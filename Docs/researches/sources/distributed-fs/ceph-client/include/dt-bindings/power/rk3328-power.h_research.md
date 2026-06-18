# sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3328-power.h

Purpose: `rk3328-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 10 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3328 (10). Representative
constants are `RK3328_PD_CORE`, `RK3328_PD_GPU`, `RK3328_PD_BUS`, `RK3328_PD_MSCH`,
`RK3328_PD_PERI`, `RK3328_PD_VIDEO`, `RK3328_PD_HEVC`, `RK3328_PD_SYS`, `RK3328_PD_BUS`,
`RK3328_PD_MSCH`, `RK3328_PD_PERI`, `RK3328_PD_VIDEO`, `RK3328_PD_HEVC`, `RK3328_PD_SYS`,
`RK3328_PD_VPU`, `RK3328_PD_VIO`. Function-like helpers are none. Value shape: literal numeric range
0..9 across 10 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3328_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RK3328 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 19 lines long. Notable source comments include `RK3328 idle id Summary.`. Example value
clusters are RK3328: `RK3328_PD_CORE=0`, `RK3328_PD_GPU=1`, `RK3328_PD_BUS=2`, `RK3328_PD_MSCH=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3328_PD_CORE`, `RK3328_PD_GPU`, `RK3328_PD_BUS`, `RK3328_PD_MSCH`, `RK3328_PD_PERI`,
`RK3328_PD_VIDEO`, `RK3328_PD_HEVC`, `RK3328_PD_SYS`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
