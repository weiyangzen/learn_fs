# sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8ulp-power.h

Purpose: `imx8ulp-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 16 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are IMX8ULP (16). Representative
constants are `IMX8ULP_PD_DMA1`, `IMX8ULP_PD_FLEXSPI2`, `IMX8ULP_PD_USB0`, `IMX8ULP_PD_USDHC0`,
`IMX8ULP_PD_USDHC1`, `IMX8ULP_PD_USDHC2_USB1`, `IMX8ULP_PD_DCNANO`, `IMX8ULP_PD_EPDC`,
`IMX8ULP_PD_DMA2`, `IMX8ULP_PD_GPU2D`, `IMX8ULP_PD_GPU3D`, `IMX8ULP_PD_HIFI4`, `IMX8ULP_PD_ISI`,
`IMX8ULP_PD_MIPI_CSI`, `IMX8ULP_PD_MIPI_DSI`, `IMX8ULP_PD_PXP`. Function-like helpers are none.
Value shape: literal numeric range 0..15 across 16 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_IMX8ULP_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`IMX8ULP group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 26 lines long. Notable source comments include none. Example value clusters are IMX8ULP:
`IMX8ULP_PD_DMA1=0`, `IMX8ULP_PD_FLEXSPI2=1`, `IMX8ULP_PD_USB0=2`, `IMX8ULP_PD_USDHC0=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`IMX8ULP_PD_DMA1`, `IMX8ULP_PD_FLEXSPI2`, `IMX8ULP_PD_USB0`, `IMX8ULP_PD_USDHC0`,
`IMX8ULP_PD_USDHC1`, `IMX8ULP_PD_USDHC2_USB1`, `IMX8ULP_PD_DCNANO`, `IMX8ULP_PD_EPDC`. Test signals
include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
