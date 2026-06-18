# sources/distributed-fs/ceph-client/drivers/regulator/tps65910-regulator.c

Purpose: Platform child regulator driver for TPS65910/TPS65911 PMICs, registering all chip-specific voltage rails with custom DCDC/LDO selector logic and external sleep-control configuration.

Important APIs/types/functions: `struct tps_info` describes rail names, input supplies, voltage tables/counts, and enable times. `struct tps65910_reg` owns dynamic descriptors, rdevs, chip ops, and external sleep-control tables. Custom ops implement mode control, DCDC voltage selectors, TPS65910 table selectors, TPS65911 computed LDO voltages, VDD3 fixed voltage, and VBB mapping. `tps65910_set_ext_sleep_config` programs EN1/EN2/EN3/SLEEP assignment registers.

Control flow: probe obtains board or DT data, gives register control to I2C, selects TPS65910 vs TPS65911 rail tables and control-register mapper, applies a TPS65910 DCDC clock-sync erratum workaround, allocates descriptors/info/rdev arrays, configures external sleep per rail, registers each regulator, and saves rdevs for shutdown. Shutdown clears external sleep control for every registered rail so reboot does not depend on external control pin state before bootloader setup.

State and persistence: regulator state is in parent regmap. Driver dynamically builds descriptors and stores board external-control configuration. DCDC OP/SR registers and gain fields encode selectors; external sleep assignment persists until cleared.

Dependencies and integration points: TPS65910 MFD, regmap, OF regulator matching, platform data, regulator core, and PMIC-specific sleep-control definitions.

Risks: external sleep config is complex and only warns on per-rail failure during probe. The function restricts a regulator to one external control input. DCDC selector math must preserve gain/OP/SR semantics. Shutdown clearing is important for reboot reliability.

Test signals: TPS65910 and TPS65911 variants, DCDC selector list/get/set, TPS65911 LDO voltage mapping, invalid multi-input sleep control, EN assignment register writes, erratum bit clearing, and shutdown cleanup.
