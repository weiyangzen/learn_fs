# sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt8189-power.h

Purpose: `mediatek,mt8189-power.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 26 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT8189 (26). Representative
constants are `MT8189_POWER_DOMAIN_CONN`, `MT8189_POWER_DOMAIN_AUDIO`,
`MT8189_POWER_DOMAIN_ADSP_TOP_DORMANT`, `MT8189_POWER_DOMAIN_ADSP_INFRA`,
`MT8189_POWER_DOMAIN_ADSP_AO`, `MT8189_POWER_DOMAIN_MM_INFRA`, `MT8189_POWER_DOMAIN_ISP_IMG1`,
`MT8189_POWER_DOMAIN_ISP_IMG2`, `...`, `MT8189_POWER_DOMAIN_SSUSB`, `MT8189_POWER_DOMAIN_MFG0`,
`MT8189_POWER_DOMAIN_MFG1`, `MT8189_POWER_DOMAIN_MFG2`, `MT8189_POWER_DOMAIN_MFG3`,
`MT8189_POWER_DOMAIN_EDP_TX_DORMANT`, `MT8189_POWER_DOMAIN_PCIE`, `MT8189_POWER_DOMAIN_PCIE_PHY`.
Function-like helpers are none. Value shape: literal numeric range 0..25 across 26 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT8189_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`SPM`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 38 lines long. Notable source comments include `SPM`,
`_DT_BINDINGS_POWER_MT8189_POWER_H`. Example value clusters are MT8189:
`MT8189_POWER_DOMAIN_CONN=0`, `MT8189_POWER_DOMAIN_AUDIO=1`,
`MT8189_POWER_DOMAIN_ADSP_TOP_DORMANT=2`, `MT8189_POWER_DOMAIN_ADSP_INFRA=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT8189_POWER_DOMAIN_CONN`, `MT8189_POWER_DOMAIN_AUDIO`, `MT8189_POWER_DOMAIN_ADSP_TOP_DORMANT`,
`MT8189_POWER_DOMAIN_ADSP_INFRA`, `MT8189_POWER_DOMAIN_ADSP_AO`, `MT8189_POWER_DOMAIN_MM_INFRA`,
`MT8189_POWER_DOMAIN_ISP_IMG1`, `MT8189_POWER_DOMAIN_ISP_IMG2`. Test signals include
dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and
device runtime-PM smoke tests.
