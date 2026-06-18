# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7779-sysc.h

Purpose: `r8a7779-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 7 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A7779 (7). Representative
constants are `R8A7779_PD_ARM1`, `R8A7779_PD_ARM2`, `R8A7779_PD_ARM3`, `R8A7779_PD_SGX`,
`R8A7779_PD_VDP`, `R8A7779_PD_IMP`, `R8A7779_PD_ALWAYS_ON`, `R8A7779_PD_ARM1`, `R8A7779_PD_ARM2`,
`R8A7779_PD_ARM3`, `R8A7779_PD_SGX`, `R8A7779_PD_VDP`, `R8A7779_PD_IMP`, `R8A7779_PD_ALWAYS_ON`.
Function-like helpers are none. Value shape: literal numeric range 1..32 across 7 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A7779_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 24 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A7779_SYSC_H__`. Example value clusters are R8A7779: `R8A7779_PD_ARM1=1`,
`R8A7779_PD_ARM2=2`, `R8A7779_PD_ARM3=3`, `R8A7779_PD_SGX=20`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A7779_PD_ARM1`, `R8A7779_PD_ARM2`, `R8A7779_PD_ARM3`, `R8A7779_PD_SGX`, `R8A7779_PD_VDP`,
`R8A7779_PD_IMP`, `R8A7779_PD_ALWAYS_ON`. Test signals include dt_binding_check, boot-time genpd
attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
