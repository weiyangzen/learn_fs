# sources/distributed-fs/ceph-client/drivers/regulator/cpcap-regulator.c

## Purpose
This file is the Motorola CPCAP PMIC regulator provider. It describes CPCAP rails for several SoC/product configurations and registers the supported rails with the regulator core using regmap-backed operations.

## Important APIs, Types, And Functions
`struct cpcap_regulator` wraps `struct regulator_desc` with resource-assignment register metadata. `struct cpcap_ddata` stores the parent regmap, platform device, and SoC-specific descriptor table. `CPCAP_REG()` builds descriptors with `volt_table`, `vsel_reg`, `enable_reg`, masks, enable/disable values, ramp delay, `of_match`, and `of_map_mode`.

The operational hooks are `cpcap_regulator_enable()`, `cpcap_regulator_disable()`, `cpcap_regulator_get_mode()`, `cpcap_regulator_set_mode()`, and `cpcap_map_mode()`. The `cpcap_regulator_ops` table combines those hooks with standard regmap helpers for enable, voltage selector, and voltage table mapping.

## Control Flow
Probe obtains SoC-specific match data from the OF compatible string, allocates driver data, fetches the parent CPCAP regmap, initializes a shared `regulator_config`, and iterates up to `CPCAP_NR_REGULATORS`. Entries with the sentinel name end the loop; entries using `unknown_val_tbl` are skipped because their voltage tables are not known. Each real entry is passed to `devm_regulator_register()` with the entry as `driver_data`.

Enable first calls `regulator_enable_regmap()`. For descriptors whose `enable_val` contains `CPCAP_REG_OFF_MODE_SEC`, it also sets the assignment bit so off mode uses the primary assignment while enabled; if assignment update fails, it disables the rail again. Disable reverses the assignment bit first, then calls `regulator_disable_regmap()`, restoring the assignment bit if disable fails.

## State And Persistence
The driver stores no dynamic per-rail state beyond `driver_data`; rail state lives in CPCAP registers and in the regulator core. Static state is encoded in voltage tables and three SoC-specific descriptor arrays: `omap4_regulators`, `mot_regulators`, and `xoom_regulators`. Some rails share registers or assignment masks, notably VSIM and VSIMCARD.

## Dependencies And Integration Points
It depends on the Motorola CPCAP MFD for register definitions and parent regmap, OF match data for board variant selection, and regulator core regmap helpers. DT nodes are expected under a `regulators` child node with names matching descriptor `of_match` strings.

## Risks
Unknown voltage tables are intentionally skipped, so DT references to those rails will not resolve. Incorrect SoC match data can program wrong enable values or assignment bits. Shared VSIM/VSIMCARD masks and off-mode assignment logic need board-specific validation. `cpcap_regulator_get_mode()` ignores `regmap_read()` failure and defaults through the returned value path, so read errors may be hidden.

## Test Signals
Check probe success per compatible, number of registered rails, regulator debugfs/sysfs voltage lists, enable/disable register transitions, off-mode assignment bit behavior for SW5-style rails, standby/normal mode mapping, and failures from parent regmap access.
