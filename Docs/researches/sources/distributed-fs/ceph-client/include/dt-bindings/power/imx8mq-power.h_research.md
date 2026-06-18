# sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8mq-power.h

Purpose: `imx8mq-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 13 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are IMX8M (11), IMX8MQ (2).
Representative constants are `IMX8M_POWER_DOMAIN_MIPI`, `IMX8M_POWER_DOMAIN_PCIE1`,
`IMX8M_POWER_DOMAIN_USB_OTG1`, `IMX8M_POWER_DOMAIN_USB_OTG2`, `IMX8M_POWER_DOMAIN_DDR1`,
`IMX8M_POWER_DOMAIN_GPU`, `IMX8M_POWER_DOMAIN_VPU`, `IMX8M_POWER_DOMAIN_DISP`,
`IMX8M_POWER_DOMAIN_GPU`, `IMX8M_POWER_DOMAIN_VPU`, `IMX8M_POWER_DOMAIN_DISP`,
`IMX8M_POWER_DOMAIN_MIPI_CSI1`, `IMX8M_POWER_DOMAIN_MIPI_CSI2`, `IMX8M_POWER_DOMAIN_PCIE2`,
`IMX8MQ_VPUBLK_PD_G1`, `IMX8MQ_VPUBLK_PD_G2`. Function-like helpers are none. Value shape: literal
numeric range 0..10 across 13 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_IMX8MQ_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`IMX8M group`, `IMX8MQ group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 24 lines long. Notable source comments include none. Example value clusters are IMX8M:
`IMX8M_POWER_DOMAIN_MIPI=0`, `IMX8M_POWER_DOMAIN_PCIE1=1`, `IMX8M_POWER_DOMAIN_USB_OTG1=2`,
`IMX8M_POWER_DOMAIN_USB_OTG2=3`; IMX8MQ: `IMX8MQ_VPUBLK_PD_G1=0`, `IMX8MQ_VPUBLK_PD_G2=1`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`IMX8M_POWER_DOMAIN_MIPI`, `IMX8M_POWER_DOMAIN_PCIE1`, `IMX8M_POWER_DOMAIN_USB_OTG1`,
`IMX8M_POWER_DOMAIN_USB_OTG2`, `IMX8M_POWER_DOMAIN_DDR1`, `IMX8M_POWER_DOMAIN_GPU`,
`IMX8M_POWER_DOMAIN_VPU`, `IMX8M_POWER_DOMAIN_DISP`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
