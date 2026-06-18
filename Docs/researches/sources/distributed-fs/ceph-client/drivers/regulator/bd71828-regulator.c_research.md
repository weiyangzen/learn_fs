# sources/distributed-fs/ceph-client/drivers/regulator/bd71828-regulator.c

Purpose: This driver supports ROHM BD71828 and BD72720 PMIC regulator blocks. It registers table-driven buck and LDO descriptors, handles DVS voltage programming from device tree, applies initial mode-control writes that select I2C/register control, and implements a special BD72720 BUCK10 mode where voltage control is removed when BUCK10 follows LDO headroom.

Important APIs, types, and functions: `struct bd71828_regulator_data` contains the descriptor, `rohm_dvs_config`, and optional register initialization array. `struct reg_init` captures one masked write. `buck_set_hw_dvs_levels()` calls `rohm_regulator_set_dvs_levels()` for descriptors with state voltages. `bd71828_ldo6_parse_dt()` interprets DVS voltage properties as state enable/disable for fixed-voltage LDO6. `bd72720_buck10_ldon_head_mode()` parses `rohm,ldon-head-microvolt`, swaps BUCK10 ops to `bd72720_buck10_ldon_head_op`, and writes LDON_HEAD bits.

Control flow: `bd71828_probe()` gets the parent regmap and checks the platform chip type. For BD72720 or BD71828 it duplicates the relevant static regulator data using `devm_kmemdup()` so probe-time descriptor mutation is instance-local. BD72720 first parses BUCK10 LDON_HEAD mode under the parent `regulators` node. Probe then registers every descriptor with the regulator core and runs each descriptor's `reg_inits` masked writes after registration.

State and persistence behavior: Regulator state lives in PMIC enable, voltage, mode, ramp, and DVS-state registers. BD71828 DVS-capable bucks default their DVS control bits to I2C/register control through `bd71828_buck*_inits`. BD72720 disables RUN-level GPIO control for BUCK1 and LDO1 by default. BUCK10 may become enable/ramp-only when LDON_HEAD is configured, leaving automatic voltage adjustment to the PMIC.

Dependencies and integration points: The file depends on `rohm-bd71828.h`, `rohm-bd72720.h`, `rohm_regulator_set_dvs_levels()`, OF regulator nodes, regmap, and regulator core helpers for linear ranges, ramp delay, and voltage-time calculation. Platform IDs are `"bd71828-pmic"` and `"bd72720-pmic"`.

Risks: Most behavior is descriptor-table driven, so incorrect masks or range counts can affect rails silently. BD72720 has documented unsupported RUN0-RUN3 GPIO sub-state functionality; DT users requesting those modes will not get full support. BUCK10 LDON_HEAD parsing assumes a `buck10` child and clamps values above 300 mV with only a warning. Running `reg_inits` after registration means machine constraints may be applied before the final control-mode writes.

Test signals: Cover BD71828 and BD72720 probe selection, DVS DT parsing for run/idle/suspend/LPSR, fixed LDO6 enable-state parsing from zero/nonzero voltage properties, BUCK10 LDON_HEAD absent/present/clamped cases, post-registration initialization writes, ramp delay selectors, and failure paths for missing `regulators` node or regmap errors.
