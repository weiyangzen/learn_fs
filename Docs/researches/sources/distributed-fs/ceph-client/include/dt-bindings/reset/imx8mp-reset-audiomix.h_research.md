# sources/distributed-fs/ceph-client/include/dt-bindings/reset/imx8mp-reset-audiomix.h

Purpose: `imx8mp-reset-audiomix.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are IMX8MP (3). Representative constants are
`IMX8MP_AUDIOMIX_EARC_RESET`, `IMX8MP_AUDIOMIX_EARC_PHY_RESET`, `IMX8MP_AUDIOMIX_DSP_RUNSTALL`,
`IMX8MP_AUDIOMIX_EARC_RESET`, `IMX8MP_AUDIOMIX_EARC_PHY_RESET`, `IMX8MP_AUDIOMIX_DSP_RUNSTALL`.
Function-like helpers are none. Value shape: literal numeric range 0..2 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDING_RESET_IMX8MP_AUDIOMIX_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `IMX8MP group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 13 lines long. Notable source comments include `DT_BINDING_RESET_IMX8MP_AUDIOMIX_H`.
Example value clusters are IMX8MP: `IMX8MP_AUDIOMIX_EARC_RESET=0`,
`IMX8MP_AUDIOMIX_EARC_PHY_RESET=1`, `IMX8MP_AUDIOMIX_DSP_RUNSTALL=2`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`IMX8MP_AUDIOMIX_EARC_RESET`, `IMX8MP_AUDIOMIX_EARC_PHY_RESET`, `IMX8MP_AUDIOMIX_DSP_RUNSTALL`. Test
signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
