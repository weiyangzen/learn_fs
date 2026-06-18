# sources/distributed-fs/ceph-client/include/dt-bindings/reset/fsl,imx8ulp-sim-lpav.h

Purpose: `fsl,imx8ulp-sim-lpav.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 6 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are IMX8ULP (6). Representative constants are
`IMX8ULP_SIM_LPAV_HIFI4_DSP_DBG_RST`, `IMX8ULP_SIM_LPAV_HIFI4_DSP_RST`,
`IMX8ULP_SIM_LPAV_HIFI4_DSP_STALL`, `IMX8ULP_SIM_LPAV_DSI_RST_BYTE_N`,
`IMX8ULP_SIM_LPAV_DSI_RST_ESC_N`, `IMX8ULP_SIM_LPAV_DSI_RST_DPI_N`,
`IMX8ULP_SIM_LPAV_HIFI4_DSP_DBG_RST`, `IMX8ULP_SIM_LPAV_HIFI4_DSP_RST`,
`IMX8ULP_SIM_LPAV_HIFI4_DSP_STALL`, `IMX8ULP_SIM_LPAV_DSI_RST_BYTE_N`,
`IMX8ULP_SIM_LPAV_DSI_RST_ESC_N`, `IMX8ULP_SIM_LPAV_DSI_RST_DPI_N`. Function-like helpers are none.
Value shape: literal numeric range 0..5 across 6 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDING_RESET_IMX8ULP_SIM_LPAV_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `IMX8ULP group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 16 lines long. Notable source comments include `DT_BINDING_RESET_IMX8ULP_SIM_LPAV_H`.
Example value clusters are IMX8ULP: `IMX8ULP_SIM_LPAV_HIFI4_DSP_DBG_RST=0`,
`IMX8ULP_SIM_LPAV_HIFI4_DSP_RST=1`, `IMX8ULP_SIM_LPAV_HIFI4_DSP_STALL=2`,
`IMX8ULP_SIM_LPAV_DSI_RST_BYTE_N=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`IMX8ULP_SIM_LPAV_HIFI4_DSP_DBG_RST`, `IMX8ULP_SIM_LPAV_HIFI4_DSP_RST`,
`IMX8ULP_SIM_LPAV_HIFI4_DSP_STALL`, `IMX8ULP_SIM_LPAV_DSI_RST_BYTE_N`,
`IMX8ULP_SIM_LPAV_DSI_RST_ESC_N`, `IMX8ULP_SIM_LPAV_DSI_RST_DPI_N`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
