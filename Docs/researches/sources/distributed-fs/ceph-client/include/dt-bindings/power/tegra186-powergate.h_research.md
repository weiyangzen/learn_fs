# sources/distributed-fs/ceph-client/include/dt-bindings/power/tegra186-powergate.h

Purpose: `tegra186-powergate.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 18 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are TEGRA186 (18). Representative
constants are `TEGRA186_POWER_DOMAIN_AUD`, `TEGRA186_POWER_DOMAIN_DFD`,
`TEGRA186_POWER_DOMAIN_DISP`, `TEGRA186_POWER_DOMAIN_DISPB`, `TEGRA186_POWER_DOMAIN_DISPC`,
`TEGRA186_POWER_DOMAIN_ISPA`, `TEGRA186_POWER_DOMAIN_NVDEC`, `TEGRA186_POWER_DOMAIN_NVJPG`, `...`,
`TEGRA186_POWER_DOMAIN_SAX`, `TEGRA186_POWER_DOMAIN_VE`, `TEGRA186_POWER_DOMAIN_VIC`,
`TEGRA186_POWER_DOMAIN_XUSBA`, `TEGRA186_POWER_DOMAIN_XUSBB`, `TEGRA186_POWER_DOMAIN_XUSBC`,
`TEGRA186_POWER_DOMAIN_GPU`, `TEGRA186_POWER_DOMAIN_MAX`. Function-like helpers are none. Value
shape: literal numeric range 0..44 across 18 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_TEGRA186_POWERGATE_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `TEGRA186 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 28 lines long. Notable source comments include none. Example value clusters are
TEGRA186: `TEGRA186_POWER_DOMAIN_AUD=0`, `TEGRA186_POWER_DOMAIN_DFD=1`,
`TEGRA186_POWER_DOMAIN_DISP=2`, `TEGRA186_POWER_DOMAIN_DISPB=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`TEGRA186_POWER_DOMAIN_AUD`, `TEGRA186_POWER_DOMAIN_DFD`, `TEGRA186_POWER_DOMAIN_DISP`,
`TEGRA186_POWER_DOMAIN_DISPB`, `TEGRA186_POWER_DOMAIN_DISPC`, `TEGRA186_POWER_DOMAIN_ISPA`,
`TEGRA186_POWER_DOMAIN_NVDEC`, `TEGRA186_POWER_DOMAIN_NVJPG`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
