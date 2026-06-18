# sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8mp-power.h

Purpose: `imx8mp-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 45 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are IMX8MP (45). Representative
constants are `IMX8MP_POWER_DOMAIN_MIPI_PHY1`, `IMX8MP_POWER_DOMAIN_PCIE_PHY`,
`IMX8MP_POWER_DOMAIN_USB1_PHY`, `IMX8MP_POWER_DOMAIN_USB2_PHY`, `IMX8MP_POWER_DOMAIN_MLMIX`,
`IMX8MP_POWER_DOMAIN_AUDIOMIX`, `IMX8MP_POWER_DOMAIN_GPU2D`, `IMX8MP_POWER_DOMAIN_GPUMIX`, `...`,
`IMX8MP_HDMIBLK_PD_TRNG`, `IMX8MP_HDMIBLK_PD_HDMI_TX`, `IMX8MP_HDMIBLK_PD_HDMI_TX_PHY`,
`IMX8MP_HDMIBLK_PD_HDCP`, `IMX8MP_HDMIBLK_PD_HRV`, `IMX8MP_VPUBLK_PD_G1`, `IMX8MP_VPUBLK_PD_G2`,
`IMX8MP_VPUBLK_PD_VC8000E`. Function-like helpers are none. Value shape: literal numeric range 0..18
across 45 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_IMX8MP_POWER_DOMAIN_POWER_H__`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `IMX8MP group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 59 lines long. Notable source comments include none. Example value clusters are IMX8MP:
`IMX8MP_POWER_DOMAIN_MIPI_PHY1=0`, `IMX8MP_POWER_DOMAIN_PCIE_PHY=1`,
`IMX8MP_POWER_DOMAIN_USB1_PHY=2`, `IMX8MP_POWER_DOMAIN_USB2_PHY=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`IMX8MP_POWER_DOMAIN_MIPI_PHY1`, `IMX8MP_POWER_DOMAIN_PCIE_PHY`, `IMX8MP_POWER_DOMAIN_USB1_PHY`,
`IMX8MP_POWER_DOMAIN_USB2_PHY`, `IMX8MP_POWER_DOMAIN_MLMIX`, `IMX8MP_POWER_DOMAIN_AUDIOMIX`,
`IMX8MP_POWER_DOMAIN_GPU2D`, `IMX8MP_POWER_DOMAIN_GPUMIX`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
