# sources/distributed-fs/ceph-client/include/dt-bindings/power/qcom,rpmhpd.h

Purpose: `qcom,rpmhpd.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 229 `#define`s covering power-domain IDs, power-
gate IDs, or performance-state constants. The main macro families are RPMH (40), RPMHPD (23),
SA8775P (17), SC8280XP (17), SM8550 (14), SM8350 (13), SM8450 (13), SM8150 (11), SC8180X (11),
SM8250 (10). Representative constants are `RPMHPD_CX`, `RPMHPD_CX_AO`, `RPMHPD_EBI`, `RPMHPD_GFX`,
`RPMHPD_LCX`, `RPMHPD_LMX`, `RPMHPD_MMCX`, `RPMHPD_MMCX_AO`, `...`, `SC8280XP_MSS`, `SC8280XP_MX`,
`SC8280XP_MXC`, `SC8280XP_MX_AO`, `SC8280XP_NSP`, `SC8280XP_QPHY`, `SC8280XP_XO`, `SC8280XP_MXC_AO`.
Function-like helpers are none. Value shape: literal numeric range 0..480 across 222 macros; 7 alias
or symbol-derived values.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_QCOM_RPMHPD_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`Generic RPMH Power Domain Indexes`, `RPMh Power Domain performance levels`, `SA8775P Power Domain
Indexes`, `SDM670 Power Domain Indexes`, `SDM845 Power Domain Indexes`, `SDX55 Power Domain
Indexes`, `SDX65 Power Domain Indexes`, `SM6350 Power Domain Indexes`, `SM8150 Power Domain
Indexes`, `SA8155P is a special case, kept for backwards compatibility`, `SM8250 Power Domain
Indexes`, `SM8350 Power Domain Indexes`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 281 lines long. Notable source comments include `Generic RPMH Power Domain Indexes`,
`RPMh Power Domain performance levels`, `Platform-specific power domain bindings. Don't add new
entries here, use RPMHPD_* above.`, `SA8775P Power Domain Indexes`, `SDM670 Power Domain Indexes`,
`SDM845 Power Domain Indexes`. Example value clusters are RPMH: `RPMH_REGULATOR_LEVEL_RETENTION=16`,
`RPMH_REGULATOR_LEVEL_MIN_SVS=48`, `RPMH_REGULATOR_LEVEL_LOW_SVS_D3_0=49`,
`RPMH_REGULATOR_LEVEL_LOW_SVS_D3=50`; RPMHPD: `RPMHPD_CX=0`, `RPMHPD_CX_AO=1`, `RPMHPD_EBI=2`,
`RPMHPD_GFX=3`; SA8775P: `SA8775P_CX=0`, `SA8775P_CX_AO=1`, `SA8775P_DDR=2`, `SA8775P_EBI=3`;
SC8280XP: `SC8280XP_CX=0`, `SC8280XP_CX_AO=1`, `SC8280XP_DDR=2`, `SC8280XP_EBI=3`; SM8550:
`SM8550_CX=0`, `SM8550_CX_AO=1`, `SM8550_EBI=2`, `SM8550_GFX=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RPMHPD_CX`, `RPMHPD_CX_AO`, `RPMHPD_EBI`, `RPMHPD_GFX`, `RPMHPD_LCX`, `RPMHPD_LMX`, `RPMHPD_MMCX`,
`RPMHPD_MMCX_AO`. Test signals include dt_binding_check, boot-time genpd attachment, power-domain
on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
