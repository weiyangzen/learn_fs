# sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt6735-power-controller.h

Purpose: `mediatek,mt6735-power-controller.h` is a Devicetree binding header for a power-domain provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 7 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT6735 (7). Representative
constants are `MT6735_POWER_DOMAIN_MD1`, `MT6735_POWER_DOMAIN_CONN`, `MT6735_POWER_DOMAIN_DIS`,
`MT6735_POWER_DOMAIN_MFG`, `MT6735_POWER_DOMAIN_ISP`, `MT6735_POWER_DOMAIN_VDE`,
`MT6735_POWER_DOMAIN_VEN`, `MT6735_POWER_DOMAIN_MD1`, `MT6735_POWER_DOMAIN_CONN`,
`MT6735_POWER_DOMAIN_DIS`, `MT6735_POWER_DOMAIN_MFG`, `MT6735_POWER_DOMAIN_ISP`,
`MT6735_POWER_DOMAIN_VDE`, `MT6735_POWER_DOMAIN_VEN`. Function-like helpers are none. Value shape:
literal numeric range 0..6 across 7 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT6735_POWER_CONTROLLER_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `MT6735 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 14 lines long. Notable source comments include none. Example value clusters are MT6735:
`MT6735_POWER_DOMAIN_MD1=0`, `MT6735_POWER_DOMAIN_CONN=1`, `MT6735_POWER_DOMAIN_DIS=2`,
`MT6735_POWER_DOMAIN_MFG=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT6735_POWER_DOMAIN_MD1`, `MT6735_POWER_DOMAIN_CONN`, `MT6735_POWER_DOMAIN_DIS`,
`MT6735_POWER_DOMAIN_MFG`, `MT6735_POWER_DOMAIN_ISP`, `MT6735_POWER_DOMAIN_VDE`,
`MT6735_POWER_DOMAIN_VEN`. Test signals include dt_binding_check, boot-time genpd attachment, power-
domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
