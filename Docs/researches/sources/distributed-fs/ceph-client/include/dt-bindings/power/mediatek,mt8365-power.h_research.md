# sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt8365-power.h

Purpose: `mediatek,mt8365-power.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 9 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT8365 (9). Representative
constants are `MT8365_POWER_DOMAIN_MM`, `MT8365_POWER_DOMAIN_CONN`, `MT8365_POWER_DOMAIN_MFG`,
`MT8365_POWER_DOMAIN_AUDIO`, `MT8365_POWER_DOMAIN_CAM`, `MT8365_POWER_DOMAIN_DSP`,
`MT8365_POWER_DOMAIN_VDEC`, `MT8365_POWER_DOMAIN_VENC`, `MT8365_POWER_DOMAIN_CONN`,
`MT8365_POWER_DOMAIN_MFG`, `MT8365_POWER_DOMAIN_AUDIO`, `MT8365_POWER_DOMAIN_CAM`,
`MT8365_POWER_DOMAIN_DSP`, `MT8365_POWER_DOMAIN_VDEC`, `MT8365_POWER_DOMAIN_VENC`,
`MT8365_POWER_DOMAIN_APU`. Function-like helpers are none. Value shape: literal numeric range 0..8
across 9 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT8365_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT8365 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 19 lines long. Notable source comments include `_DT_BINDINGS_POWER_MT8365_POWER_H`.
Example value clusters are MT8365: `MT8365_POWER_DOMAIN_MM=0`, `MT8365_POWER_DOMAIN_CONN=1`,
`MT8365_POWER_DOMAIN_MFG=2`, `MT8365_POWER_DOMAIN_AUDIO=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT8365_POWER_DOMAIN_MM`, `MT8365_POWER_DOMAIN_CONN`, `MT8365_POWER_DOMAIN_MFG`,
`MT8365_POWER_DOMAIN_AUDIO`, `MT8365_POWER_DOMAIN_CAM`, `MT8365_POWER_DOMAIN_DSP`,
`MT8365_POWER_DOMAIN_VDEC`, `MT8365_POWER_DOMAIN_VENC`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
