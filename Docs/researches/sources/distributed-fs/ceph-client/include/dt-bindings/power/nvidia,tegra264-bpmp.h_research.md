# sources/distributed-fs/ceph-client/include/dt-bindings/power/nvidia,tegra264-bpmp.h

Purpose: `nvidia,tegra264-bpmp.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 15 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are TEGRA264 (15). Representative
constants are `TEGRA264_POWER_DOMAIN_DISP`, `TEGRA264_POWER_DOMAIN_AUD`,
`TEGRA264_POWER_DOMAIN_XUSB_SS`, `TEGRA264_POWER_DOMAIN_XUSB_DEV`,
`TEGRA264_POWER_DOMAIN_XUSB_HOST`, `TEGRA264_POWER_DOMAIN_MGBE0`, `TEGRA264_POWER_DOMAIN_MGBE1`,
`TEGRA264_POWER_DOMAIN_MGBE2`, `TEGRA264_POWER_DOMAIN_MGBE2`, `TEGRA264_POWER_DOMAIN_MGBE3`,
`TEGRA264_POWER_DOMAIN_VI`, `TEGRA264_POWER_DOMAIN_VIC`, `TEGRA264_POWER_DOMAIN_ISP0`,
`TEGRA264_POWER_DOMAIN_ISP1`, `TEGRA264_POWER_DOMAIN_PVA0`, `TEGRA264_POWER_DOMAIN_GPU`. Function-
like helpers are none. Value shape: literal numeric range 1..22 across 15 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDINGS_POWER_NVIDIA_TEGRA264_BPMP_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `reserved 3:9`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 24 lines long. Notable source comments include `reserved 3:9`,
`DT_BINDINGS_POWER_NVIDIA_TEGRA264_BPMP_H`. Example value clusters are TEGRA264:
`TEGRA264_POWER_DOMAIN_DISP=1`, `TEGRA264_POWER_DOMAIN_AUD=2`, `TEGRA264_POWER_DOMAIN_XUSB_SS=10`,
`TEGRA264_POWER_DOMAIN_XUSB_DEV=11`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`TEGRA264_POWER_DOMAIN_DISP`, `TEGRA264_POWER_DOMAIN_AUD`, `TEGRA264_POWER_DOMAIN_XUSB_SS`,
`TEGRA264_POWER_DOMAIN_XUSB_DEV`, `TEGRA264_POWER_DOMAIN_XUSB_HOST`, `TEGRA264_POWER_DOMAIN_MGBE0`,
`TEGRA264_POWER_DOMAIN_MGBE1`, `TEGRA264_POWER_DOMAIN_MGBE2`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
