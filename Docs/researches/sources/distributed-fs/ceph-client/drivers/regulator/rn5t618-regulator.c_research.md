# sources/distributed-fs/ceph-client/drivers/regulator/rn5t618-regulator.c

Purpose: registers voltage regulators for Ricoh RN5T567, RN5T618, and RC5T619 PMIC variants. The driver maps each variant to DCDC, LDO, and RTC LDO descriptor arrays with linear voltage selectors.

Important APIs/types/functions: `rn5t618_reg_ops` uses regmap helpers for enable, disable, status, voltage selection, and linear voltage listing. The `REG()` macro creates `regulator_desc` entries from RN5T618 register constants. `rn5t618_regulator_probe()` reads `struct rn5t618->variant`, chooses the descriptor table, and registers each regulator.

Control flow: platform probe obtains parent MFD driver data, switches on variant, fills `regulator_config` with the parent device and regmap, and loops through the selected descriptor table. Registration failure aborts probe at the first failed rail.

State and persistence: no private runtime state is allocated. Voltage selections and enables are held in PMIC registers via the parent regmap. Device-tree integration comes from each descriptor's `of_match` under the `regulators` node.

Dependencies and integration: integrates with the RN5T618 MFD core, regmap, OF regulator matching, and regulator framework. The platform alias is `rn5t618-regulator`, so it is normally instantiated by the MFD cell.

Risks and test signals: variant table accuracy is the main concern because rail count and voltage minima differ, especially `LDORTC1`. Tests should cover all three variants, missing/unknown variants returning `-EINVAL`, OF node matching, voltage selector min/max boundaries, and failure cleanup on partial registration.
