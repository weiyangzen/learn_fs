# sources/distributed-fs/ceph-client/include/dt-bindings/power/owl-s900-powergate.h

Purpose: `owl-s900-powergate.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 12 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are S900 (12). Representative constants
are `S900_PD_GPU_B`, `S900_PD_VCE`, `S900_PD_SENSOR`, `S900_PD_VDE`, `S900_PD_HDE`, `S900_PD_USB3`,
`S900_PD_DDR0`, `S900_PD_DDR1`, `S900_PD_HDE`, `S900_PD_USB3`, `S900_PD_DDR0`, `S900_PD_DDR1`,
`S900_PD_DE`, `S900_PD_NAND`, `S900_PD_USB2_H0`, `S900_PD_USB2_H1`. Function-like helpers are none.
Value shape: literal numeric range 0..11 across 12 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDINGS_POWER_OWL_S900_POWERGATE_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `S900 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 23 lines long. Notable source comments include `Actions Semi S900 SPS`. Example value
clusters are S900: `S900_PD_GPU_B=0`, `S900_PD_VCE=1`, `S900_PD_SENSOR=2`, `S900_PD_VDE=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`S900_PD_GPU_B`, `S900_PD_VCE`, `S900_PD_SENSOR`, `S900_PD_VDE`, `S900_PD_HDE`, `S900_PD_USB3`,
`S900_PD_DDR0`, `S900_PD_DDR1`. Test signals include dt_binding_check, boot-time genpd attachment,
power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
