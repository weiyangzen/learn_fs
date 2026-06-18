# sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt8196-power.h

Purpose: `mediatek,mt8196-power.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 42 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT8196 (42). Representative
constants are `MT8196_POWER_DOMAIN_MD`, `MT8196_POWER_DOMAIN_CONN`, `MT8196_POWER_DOMAIN_SSUSB_P0`,
`MT8196_POWER_DOMAIN_SSUSB_DP_PHY_P0`, `MT8196_POWER_DOMAIN_SSUSB_P1`,
`MT8196_POWER_DOMAIN_SSUSB_P23`, `MT8196_POWER_DOMAIN_SSUSB_PHY_P2`,
`MT8196_POWER_DOMAIN_PEXTP_MAC0`, `...`, `MT8196_POWER_DOMAIN_MM_INFRA0`,
`MT8196_POWER_DOMAIN_MM_INFRA1`, `MT8196_POWER_DOMAIN_MM_INFRA_AO`, `MT8196_POWER_DOMAIN_CSI_BS_RX`,
`MT8196_POWER_DOMAIN_CSI_LS_RX`, `MT8196_POWER_DOMAIN_DSI_PHY0`, `MT8196_POWER_DOMAIN_DSI_PHY1`,
`MT8196_POWER_DOMAIN_DSI_PHY2`. Function-like helpers are none. Value shape: literal numeric range
0..22 across 42 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT8196_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`SCPSYS Secure Power Manager - Direct Control`, `SCPSYS Secure Power Manager - HW Voter`, `HFRPSYS
MultiMedia Power Control (MMPC) - HW Voter`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 58 lines long. Notable source comments include `AngeloGioacchino Del Regno
<angelogioacchino.delregno@collabora.com>`, `SCPSYS Secure Power Manager - Direct Control`, `SCPSYS
Secure Power Manager - HW Voter`, `HFRPSYS MultiMedia Power Control (MMPC) - HW Voter`,
`_DT_BINDINGS_POWER_MT8196_POWER_H`. Example value clusters are MT8196: `MT8196_POWER_DOMAIN_MD=0`,
`MT8196_POWER_DOMAIN_CONN=1`, `MT8196_POWER_DOMAIN_SSUSB_P0=2`,
`MT8196_POWER_DOMAIN_SSUSB_DP_PHY_P0=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT8196_POWER_DOMAIN_MD`, `MT8196_POWER_DOMAIN_CONN`, `MT8196_POWER_DOMAIN_SSUSB_P0`,
`MT8196_POWER_DOMAIN_SSUSB_DP_PHY_P0`, `MT8196_POWER_DOMAIN_SSUSB_P1`,
`MT8196_POWER_DOMAIN_SSUSB_P23`, `MT8196_POWER_DOMAIN_SSUSB_PHY_P2`,
`MT8196_POWER_DOMAIN_PEXTP_MAC0`. Test signals include dt_binding_check, boot-time genpd attachment,
power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
