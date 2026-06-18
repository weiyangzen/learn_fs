# sources/distributed-fs/ceph-client/include/dt-bindings/power/qcom-rpmpd.h

Purpose: `qcom-rpmpd.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 156 `#define`s covering power-domain IDs, power-
gate IDs, or performance-state constants. The main macro families are RPM_SMD (12), RPMPD (11),
MSM8998 (10), SDM660 (10), SM6375 (10), MSM8939 (8), QCM2290 (8), SM6115 (8), MSM8953 (7), MSM8994
(7). Representative constants are `RPMPD_VDDCX`, `RPMPD_VDDCX_AO`, `RPMPD_VDDCX_VFC`,
`RPMPD_VDDCX_VFL`, `RPMPD_VDDMX`, `RPMPD_VDDMX_AO`, `RPMPD_VDDMX_VFL`, `RPMPD_SSCCX`, `...`,
`RPM_SMD_LEVEL_SVS`, `RPM_SMD_LEVEL_SVS_PLUS`, `RPM_SMD_LEVEL_NOM`, `RPM_SMD_LEVEL_NOM_PLUS`,
`RPM_SMD_LEVEL_TURBO`, `RPM_SMD_LEVEL_TURBO_NO_CPR`, `RPM_SMD_LEVEL_TURBO_HIGH`,
`RPM_SMD_LEVEL_BINNING`. Function-like helpers are none. Value shape: literal numeric range 0..512
across 90 macros; 66 alias or symbol-derived values.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_QCOM_RPMPD_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`Generic RPM Power Domain Indexes`, `VFC and VFL are mutually exclusive and can not be present on
the same platform`, `MDM9607 Power Domains`, `MSM8226 Power Domain Indexes`, `MSM8939 Power
Domains`, `MSM8916 Power Domain Indexes`, `MSM8909 Power Domain Indexes`, `MSM8917 Power Domain
Indexes`, `MSM8937 Power Domain Indexes`, `QM215 Power Domain Indexes`, `MSM8953 Power Domain
Indexes`, `MSM8974 Power Domain Indexes`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are `dt-bindings/power/qcom,rpmhpd.h`. Integration points are generic power-domain
providers, device `power-domains` phandles, OPP/performance-state users, and SoC power-controller
drivers.

Local source signals: The file is 215 lines long. Notable source comments include `Generic RPM Power Domain Indexes`, `VFC
and VFL are mutually exclusive and can not be present on the same platform`, `Platform-specific
power domain bindings. Don't add new entries here, use RPMPD_* above.`, `MDM9607 Power Domains`,
`MSM8226 Power Domain Indexes`, `MSM8939 Power Domains`. Example value clusters are RPM_SMD:
`RPM_SMD_LEVEL_RETENTION=16`, `RPM_SMD_LEVEL_RETENTION_PLUS=32`, `RPM_SMD_LEVEL_MIN_SVS=48`,
`RPM_SMD_LEVEL_LOW_SVS=64`; RPMPD: `RPMPD_VDDCX=0`, `RPMPD_VDDCX_AO=1`, `RPMPD_VDDCX_VFC=2`,
`RPMPD_VDDCX_VFL=2`; MSM8998: `MSM8998_VDDCX=RPMPD_VDDCX`, `MSM8998_VDDCX_AO=RPMPD_VDDCX_AO`,
`MSM8998_VDDCX_VFL=RPMPD_VDDCX_VFL`, `MSM8998_VDDMX=RPMPD_VDDMX`; SDM660:
`SDM660_VDDCX=RPMPD_VDDCX`, `SDM660_VDDCX_AO=RPMPD_VDDCX_AO`, `SDM660_VDDCX_VFL=RPMPD_VDDCX_VFL`,
`SDM660_VDDMX=RPMPD_VDDMX`; SM6375: `SM6375_VDDCX=0`, `SM6375_VDDCX_AO=1`, `SM6375_VDDCX_VFL=2`,
`SM6375_VDDMX=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RPMPD_VDDCX`, `RPMPD_VDDCX_AO`, `RPMPD_VDDCX_VFC`, `RPMPD_VDDCX_VFL`, `RPMPD_VDDMX`,
`RPMPD_VDDMX_AO`, `RPMPD_VDDMX_VFL`, `RPMPD_SSCCX`. Test signals include dt_binding_check, boot-time
genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
