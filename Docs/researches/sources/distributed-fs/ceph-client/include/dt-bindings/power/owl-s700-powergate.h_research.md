# sources/distributed-fs/ceph-client/include/dt-bindings/power/owl-s700-powergate.h

Purpose: `owl-s700-powergate.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 8 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are S700 (8). Representative constants
are `S700_PD_VDE`, `S700_PD_VCE_SI`, `S700_PD_USB2_1`, `S700_PD_HDE`, `S700_PD_DMA`, `S700_PD_DS`,
`S700_PD_USB3`, `S700_PD_USB2_0`, `S700_PD_VDE`, `S700_PD_VCE_SI`, `S700_PD_USB2_1`, `S700_PD_HDE`,
`S700_PD_DMA`, `S700_PD_DS`, `S700_PD_USB3`, `S700_PD_USB2_0`. Function-like helpers are none. Value
shape: literal numeric range 0..7 across 8 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDINGS_POWER_OWL_S700_POWERGATE_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `S700 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 19 lines long. Notable source comments include `Actions Semi S700 SPS`. Example value
clusters are S700: `S700_PD_VDE=0`, `S700_PD_VCE_SI=1`, `S700_PD_USB2_1=2`, `S700_PD_HDE=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`S700_PD_VDE`, `S700_PD_VCE_SI`, `S700_PD_USB2_1`, `S700_PD_HDE`, `S700_PD_DMA`, `S700_PD_DS`,
`S700_PD_USB3`, `S700_PD_USB2_0`. Test signals include dt_binding_check, boot-time genpd attachment,
power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
