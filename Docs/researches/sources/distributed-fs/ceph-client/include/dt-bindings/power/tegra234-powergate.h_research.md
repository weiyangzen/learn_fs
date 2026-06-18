# sources/distributed-fs/ceph-client/include/dt-bindings/power/tegra234-powergate.h

Purpose: `tegra234-powergate.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 31 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are TEGRA234 (31). Representative
constants are `TEGRA234_POWER_DOMAIN_OFA`, `TEGRA234_POWER_DOMAIN_AUD`,
`TEGRA234_POWER_DOMAIN_DISP`, `TEGRA234_POWER_DOMAIN_PCIEX8A`, `TEGRA234_POWER_DOMAIN_PCIEX4A`,
`TEGRA234_POWER_DOMAIN_PCIEX4BA`, `TEGRA234_POWER_DOMAIN_PCIEX4BB`, `TEGRA234_POWER_DOMAIN_PCIEX1A`,
`...`, `TEGRA234_POWER_DOMAIN_VI`, `TEGRA234_POWER_DOMAIN_VIC`, `TEGRA234_POWER_DOMAIN_PVA`,
`TEGRA234_POWER_DOMAIN_DLAA`, `TEGRA234_POWER_DOMAIN_DLAB`, `TEGRA234_POWER_DOMAIN_CV`,
`TEGRA234_POWER_DOMAIN_GPU`, `TEGRA234_POWER_DOMAIN_NVJPGB`. Function-like helpers are none. Value
shape: 31 alias or symbol-derived values.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__ABI_MACH_T234_POWERGATE_T234_H_`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`TEGRA234 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 39 lines long. Notable source comments include none. Example value clusters are
TEGRA234: `TEGRA234_POWER_DOMAIN_OFA=1U`, `TEGRA234_POWER_DOMAIN_AUD=2U`,
`TEGRA234_POWER_DOMAIN_DISP=3U`, `TEGRA234_POWER_DOMAIN_PCIEX8A=5U`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`TEGRA234_POWER_DOMAIN_OFA`, `TEGRA234_POWER_DOMAIN_AUD`, `TEGRA234_POWER_DOMAIN_DISP`,
`TEGRA234_POWER_DOMAIN_PCIEX8A`, `TEGRA234_POWER_DOMAIN_PCIEX4A`, `TEGRA234_POWER_DOMAIN_PCIEX4BA`,
`TEGRA234_POWER_DOMAIN_PCIEX4BB`, `TEGRA234_POWER_DOMAIN_PCIEX1A`. Test signals include
dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and
device runtime-PM smoke tests.
