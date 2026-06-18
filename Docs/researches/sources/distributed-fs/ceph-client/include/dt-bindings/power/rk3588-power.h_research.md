# sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3588-power.h

Purpose: `rk3588-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 44 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3588 (44). Representative
constants are `RK3588_PD_CPU_0`, `RK3588_PD_CPU_1`, `RK3588_PD_CPU_2`, `RK3588_PD_CPU_3`,
`RK3588_PD_CPU_4`, `RK3588_PD_CPU_5`, `RK3588_PD_CPU_6`, `RK3588_PD_CPU_7`, `...`, `RK3588_PD_NVM0`,
`RK3588_PD_SDIO`, `RK3588_PD_AUDIO`, `RK3588_PD_SECURE`, `RK3588_PD_SDMMC`, `RK3588_PD_CRYPTO`,
`RK3588_PD_BUS`, `RK3588_PD_PMU1`. Function-like helpers are none. Value shape: literal numeric
range 0..43 across 44 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3588_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `VD_LITDSU`, `VD_BIGCORE0`, `VD_BIGCORE1`, `VD_NPU`, `VD_GPU`, `VD_VCODEC`, `VD_DD01`,
`VD_DD23`, `VD_LOGIC`, `VD_PMU`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 69 lines long. Notable source comments include `VD_LITDSU`, `VD_BIGCORE0`,
`VD_BIGCORE1`, `VD_NPU`, `VD_GPU`, `VD_VCODEC`. Example value clusters are RK3588:
`RK3588_PD_CPU_0=0`, `RK3588_PD_CPU_1=1`, `RK3588_PD_CPU_2=2`, `RK3588_PD_CPU_3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3588_PD_CPU_0`, `RK3588_PD_CPU_1`, `RK3588_PD_CPU_2`, `RK3588_PD_CPU_3`, `RK3588_PD_CPU_4`,
`RK3588_PD_CPU_5`, `RK3588_PD_CPU_6`, `RK3588_PD_CPU_7`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
