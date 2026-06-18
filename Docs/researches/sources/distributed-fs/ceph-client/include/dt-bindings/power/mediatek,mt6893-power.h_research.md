# sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt6893-power.h

Purpose: `mediatek,mt6893-power.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 24 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT6893 (24). Representative
constants are `MT6893_POWER_DOMAIN_CONN`, `MT6893_POWER_DOMAIN_MFG0`, `MT6893_POWER_DOMAIN_MFG1`,
`MT6893_POWER_DOMAIN_MFG2`, `MT6893_POWER_DOMAIN_MFG3`, `MT6893_POWER_DOMAIN_MFG4`,
`MT6893_POWER_DOMAIN_MFG5`, `MT6893_POWER_DOMAIN_MFG6`, `...`, `MT6893_POWER_DOMAIN_DISP`,
`MT6893_POWER_DOMAIN_AUDIO`, `MT6893_POWER_DOMAIN_ADSP`, `MT6893_POWER_DOMAIN_CAM`,
`MT6893_POWER_DOMAIN_CAM_RAWA`, `MT6893_POWER_DOMAIN_CAM_RAWB`, `MT6893_POWER_DOMAIN_CAM_RAWC`,
`MT6893_POWER_DOMAIN_DP_TX`. Function-like helpers are none. Value shape: literal numeric range
0..23 across 24 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT6893_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT6893 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 35 lines long. Notable source comments include `AngeloGioacchino Del Regno
<angelogioacchino.delregno@collabora.com>`, `_DT_BINDINGS_POWER_MT6893_POWER_H`. Example value
clusters are MT6893: `MT6893_POWER_DOMAIN_CONN=0`, `MT6893_POWER_DOMAIN_MFG0=1`,
`MT6893_POWER_DOMAIN_MFG1=2`, `MT6893_POWER_DOMAIN_MFG2=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT6893_POWER_DOMAIN_CONN`, `MT6893_POWER_DOMAIN_MFG0`, `MT6893_POWER_DOMAIN_MFG1`,
`MT6893_POWER_DOMAIN_MFG2`, `MT6893_POWER_DOMAIN_MFG3`, `MT6893_POWER_DOMAIN_MFG4`,
`MT6893_POWER_DOMAIN_MFG5`, `MT6893_POWER_DOMAIN_MFG6`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
