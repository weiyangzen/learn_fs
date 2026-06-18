# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a774b1-sysc.h

Purpose: `r8a774b1-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 9 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A774B1 (9). Representative
constants are `R8A774B1_PD_CA57_CPU0`, `R8A774B1_PD_CA57_CPU1`, `R8A774B1_PD_A3VP`,
`R8A774B1_PD_CA57_SCU`, `R8A774B1_PD_A3VC`, `R8A774B1_PD_3DG_A`, `R8A774B1_PD_3DG_B`,
`R8A774B1_PD_A2VC1`, `R8A774B1_PD_CA57_CPU1`, `R8A774B1_PD_A3VP`, `R8A774B1_PD_CA57_SCU`,
`R8A774B1_PD_A3VC`, `R8A774B1_PD_3DG_A`, `R8A774B1_PD_3DG_B`, `R8A774B1_PD_A2VC1`,
`R8A774B1_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 0..32
across 9 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A774B1_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 26 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A774B1_SYSC_H__`. Example value clusters are R8A774B1:
`R8A774B1_PD_CA57_CPU0=0`, `R8A774B1_PD_CA57_CPU1=1`, `R8A774B1_PD_A3VP=9`,
`R8A774B1_PD_CA57_SCU=12`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A774B1_PD_CA57_CPU0`, `R8A774B1_PD_CA57_CPU1`, `R8A774B1_PD_A3VP`, `R8A774B1_PD_CA57_SCU`,
`R8A774B1_PD_A3VC`, `R8A774B1_PD_3DG_A`, `R8A774B1_PD_3DG_B`, `R8A774B1_PD_A2VC1`. Test signals
include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
