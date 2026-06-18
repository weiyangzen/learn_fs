# sources/distributed-fs/ceph-client/include/dt-bindings/power/tegra194-powergate.h

Purpose: `tegra194-powergate.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 27 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are TEGRA194 (27). Representative
constants are `TEGRA194_POWER_DOMAIN_AUD`, `TEGRA194_POWER_DOMAIN_DISP`,
`TEGRA194_POWER_DOMAIN_DISPB`, `TEGRA194_POWER_DOMAIN_DISPC`, `TEGRA194_POWER_DOMAIN_ISPA`,
`TEGRA194_POWER_DOMAIN_NVDECA`, `TEGRA194_POWER_DOMAIN_NVJPG`, `TEGRA194_POWER_DOMAIN_NVENCA`,
`...`, `TEGRA194_POWER_DOMAIN_PCIEX8B`, `TEGRA194_POWER_DOMAIN_PVAA`, `TEGRA194_POWER_DOMAIN_PVAB`,
`TEGRA194_POWER_DOMAIN_DLAA`, `TEGRA194_POWER_DOMAIN_DLAB`, `TEGRA194_POWER_DOMAIN_CV`,
`TEGRA194_POWER_DOMAIN_GPU`, `TEGRA194_POWER_DOMAIN_MAX`. Function-like helpers are none. Value
shape: literal numeric range 1..27 across 27 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__ABI_MACH_T194_POWERGATE_T194_H_`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`TEGRA194 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 35 lines long. Notable source comments include none. Example value clusters are
TEGRA194: `TEGRA194_POWER_DOMAIN_AUD=1`, `TEGRA194_POWER_DOMAIN_DISP=2`,
`TEGRA194_POWER_DOMAIN_DISPB=3`, `TEGRA194_POWER_DOMAIN_DISPC=4`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`TEGRA194_POWER_DOMAIN_AUD`, `TEGRA194_POWER_DOMAIN_DISP`, `TEGRA194_POWER_DOMAIN_DISPB`,
`TEGRA194_POWER_DOMAIN_DISPC`, `TEGRA194_POWER_DOMAIN_ISPA`, `TEGRA194_POWER_DOMAIN_NVDECA`,
`TEGRA194_POWER_DOMAIN_NVJPG`, `TEGRA194_POWER_DOMAIN_NVENCA`. Test signals include
dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and
device runtime-PM smoke tests.
