# sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun55i-a523-pck-600.h

Purpose: `allwinner,sun55i-a523-pck-600.h` is a Devicetree binding header for a power-domain provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 8 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PD_VE (1), PD_GPU (1), PD_VI (1),
PD_VO0 (1), PD_VO1 (1), PD_DE (1), PD_NAND (1), PD_PCIE (1). Representative constants are `PD_VE`,
`PD_GPU`, `PD_VI`, `PD_VO0`, `PD_VO1`, `PD_DE`, `PD_NAND`, `PD_PCIE`, `PD_VE`, `PD_GPU`, `PD_VI`,
`PD_VO0`, `PD_VO1`, `PD_DE`, `PD_NAND`, `PD_PCIE`. Function-like helpers are none. Value shape:
literal numeric range 0..7 across 8 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_SUN55I_A523_PCK600_H_`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `PD_VE group`, `PD_GPU group`, `PD_VI group`, `PD_VO0 group`, `PD_VO1 group`, `PD_DE
group`, `PD_NAND group`, `PD_PCIE group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 15 lines long. Notable source comments include
`_DT_BINDINGS_POWER_SUN55I_A523_PCK600_H_`. Example value clusters are PD_VE: `PD_VE=0`; PD_GPU:
`PD_GPU=1`; PD_VI: `PD_VI=2`; PD_VO0: `PD_VO0=3`; PD_VO1: `PD_VO1=4`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PD_VE`, `PD_GPU`, `PD_VI`, `PD_VO0`, `PD_VO1`, `PD_DE`, `PD_NAND`, `PD_PCIE`. Test signals include
dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and
device runtime-PM smoke tests.
