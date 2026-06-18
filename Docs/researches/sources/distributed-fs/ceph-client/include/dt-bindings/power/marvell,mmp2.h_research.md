# sources/distributed-fs/ceph-client/include/dt-bindings/power/marvell,mmp2.h

Purpose: `marvell,mmp2.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 4 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MMP2 (3), MMP3 (1). Representative
constants are `MMP2_POWER_DOMAIN_GPU`, `MMP2_POWER_DOMAIN_AUDIO`, `MMP3_POWER_DOMAIN_CAMERA`,
`MMP2_NR_POWER_DOMAINS`, `MMP2_POWER_DOMAIN_GPU`, `MMP2_POWER_DOMAIN_AUDIO`,
`MMP3_POWER_DOMAIN_CAMERA`, `MMP2_NR_POWER_DOMAINS`. Function-like helpers are none. Value shape:
literal numeric range 0..3 across 4 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DTS_MARVELL_MMP2_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are `MMP2
group`, `MMP3 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 11 lines long. Notable source comments include none. Example value clusters are MMP2:
`MMP2_POWER_DOMAIN_GPU=0`, `MMP2_POWER_DOMAIN_AUDIO=1`, `MMP2_NR_POWER_DOMAINS=3`; MMP3:
`MMP3_POWER_DOMAIN_CAMERA=2`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MMP2_POWER_DOMAIN_GPU`, `MMP2_POWER_DOMAIN_AUDIO`, `MMP3_POWER_DOMAIN_CAMERA`,
`MMP2_NR_POWER_DOMAINS`. Test signals include dt_binding_check, boot-time genpd attachment, power-
domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
