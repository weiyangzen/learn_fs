# sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8mm-power.h

Purpose: `imx8mm-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 19 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are IMX8MM (19). Representative
constants are `IMX8MM_POWER_DOMAIN_HSIOMIX`, `IMX8MM_POWER_DOMAIN_PCIE`, `IMX8MM_POWER_DOMAIN_OTG1`,
`IMX8MM_POWER_DOMAIN_OTG2`, `IMX8MM_POWER_DOMAIN_GPUMIX`, `IMX8MM_POWER_DOMAIN_GPU`,
`IMX8MM_POWER_DOMAIN_VPUMIX`, `IMX8MM_POWER_DOMAIN_VPUG1`, `...`, `IMX8MM_POWER_DOMAIN_MIPI`,
`IMX8MM_VPUBLK_PD_G1`, `IMX8MM_VPUBLK_PD_G2`, `IMX8MM_VPUBLK_PD_H1`, `IMX8MM_DISPBLK_PD_CSI_BRIDGE`,
`IMX8MM_DISPBLK_PD_LCDIF`, `IMX8MM_DISPBLK_PD_MIPI_DSI`, `IMX8MM_DISPBLK_PD_MIPI_CSI`. Function-like
helpers are none. Value shape: literal numeric range 0..11 across 19 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_IMX8MM_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`IMX8MM group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 31 lines long. Notable source comments include none. Example value clusters are IMX8MM:
`IMX8MM_POWER_DOMAIN_HSIOMIX=0`, `IMX8MM_POWER_DOMAIN_PCIE=1`, `IMX8MM_POWER_DOMAIN_OTG1=2`,
`IMX8MM_POWER_DOMAIN_OTG2=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`IMX8MM_POWER_DOMAIN_HSIOMIX`, `IMX8MM_POWER_DOMAIN_PCIE`, `IMX8MM_POWER_DOMAIN_OTG1`,
`IMX8MM_POWER_DOMAIN_OTG2`, `IMX8MM_POWER_DOMAIN_GPUMIX`, `IMX8MM_POWER_DOMAIN_GPU`,
`IMX8MM_POWER_DOMAIN_VPUMIX`, `IMX8MM_POWER_DOMAIN_VPUG1`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
