# sources/distributed-fs/ceph-client/drivers/regulator/as3711-regulator.c

Purpose: platform child regulator driver for the AMS AS3711 PMIC, exposing four step-down and eight LDO regulators through the parent MFD regmap.

Important APIs/types/functions: descriptor macro `AS3711_REG()` builds `as3711_reg_desc[]`. `as3711_set_mode_sd()` and `as3711_get_mode_sd()` map regulator FAST/NORMAL/IDLE modes to AS3711 SD fast and low-noise bits. `as3711_regulator_parse_dt()` fills platform-data init arrays from OF matches.

Control flow: `subsys_initcall()` registers the platform driver. Probe requires `struct as3711_regulator_pdata`, optionally parses parent `regulators` child with `of_regulator_match()`, then registers each descriptor with the parent regmap and per-rail init data/of node.

State and persistence: no private runtime allocation beyond stack arrays; persistent state is PMIC register contents. Platform data carries init constraints and OF nodes during probe. SD mode bits are read/written directly each time.

Dependencies and integration: depends on AS3711 MFD definitions/register map, platform data supplied by the parent, OF regulator matching, regmap, and regulator core.

Risks and test signals: OF probing still fails without platform data, so the parent MFD must allocate/populate it even on DT systems. Step-up output is noted but not modeled. Tests should cover all SD mode mappings, LDO voltage range tables, OF node matching, missing platform data, parent regmap errors, and registration failures midway through the rail list.
