# subset-b-005175 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/ab8500.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/ab8500.c

Purpose: implements the ST-Ericsson AB8500/AB8505 MFD child regulator driver. It exposes AB8500 VAUX, VINTCORE, TVOUT, AUDIO, ANAMIC, DMIC, and ANA rails, plus the larger AB8505 rail set, through the regulator framework.

Important APIs/types/functions: `struct ab8500_regulator_info` holds regulator descriptors and ABx500 bank/register/mask metadata; `struct ab8500_shared_mode` coordinates the AB8505 analog microphone rails. Ops include `ab8500_regulator_enable()`, `disable()`, `is_enabled()`, `set_mode()`, `get_mode()`, `get_voltage_sel()`, and `set_voltage_sel()`. Static voltage tables and `ab8500_regulator_info[]`/`ab8505_regulator_info[]` define all rails.

Control flow: `subsys_initcall()` registers a platform driver. Probe gets the parent `struct ab8500`, selects AB8500 versus AB8505 tables via `is_ab8505()`, parses DT regulator nodes with `of_regulator_match()`, and registers each descriptor with `devm_regulator_register()`. Runtime operations map regulator framework calls into `abx500_get_register_interruptible()` and `abx500_mask_and_set_register_interruptible()`.

State and persistence: driver state is static descriptor metadata plus per-info `update_val` mode cache, `dev`, and AB8505 shared-mode booleans protected by `shared_mode_mutex`. Hardware register writes persist until PMIC reset or later firmware/kernel changes; the driver has no filesystem persistence.

Dependencies and integration: depends on ABx500/AB8500 MFD APIs, regulator core, OF regulator matching, and platform bus ordering. AB8500 hardware revision handling changes AUX3 voltage table/mask for pre-v2.0 chips.

Risks and test signals: risks concentrate in register table accuracy and shared low-power mode arbitration for ANAMIC1/2. Tests should cover AB8500 and AB8505 DT matching, enable/disable bit writes, voltage selector round trips, mode changes while disabled/enabled, old AB8500 AUX3 behavior, and failure unwind on registration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/ab8500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/act8865-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/act8865-regulator.c

Purpose: supports Active-Semi ACT8600, ACT8846, and ACT8865 PMIC regulators over I2C, with optional ACT8600 charger status reporting and system-power-off integration for ACT8846/ACT8865.

Important APIs/types/functions: `struct act8865` stores regmap and shutdown register data. `act8865_set_mode()`, `act8865_get_mode()`, and suspend helpers program ACT8865 control/suspend registers; descriptor arrays `act8600_regulators[]`, `act8846_regulators[]`, `act8865_regulators[]`, and `act8865_alt_regulators[]` define rails. `act8600_charger_probe()` registers a `power_supply`.

Control flow: probe identifies the chip from OF or I2C ID, chooses descriptor and regmap configuration tables, optionally installs `pm_power_off`, registers all regulators, adds the ACT8600 charger device if applicable, stores client data, and unlocks ACT8865 expert registers. Regulator ops use generic regmap helpers for voltage, enable, pull-down, and linear-range mapping.

State and persistence: device state is devm-managed `struct act8865`, a global `act8865_i2c_client` for power-off, and hardware registers. `active-semi,vsel-high` selects the alternate ACT8865 DCDC VSET bank at probe only. Suspend settings and mode bits persist in PMIC registers until changed.

Dependencies and integration: integrates I2C, regmap access tables, OF bindings, regulator core, power-supply core, and global power-off handling. Platform-data fallback still exists for non-OF regulator init data.

Risks and test signals: global `pm_power_off` ownership can conflict with another power controller. ACT8600 has restricted readable/writable/volatile register tables, so bad ranges surface as regmap failures. Test ACT8600/8846/8865 descriptor counts, VSET-high selection, charger status decoding, suspend-enable writes, power-off register writes, and probe deferral from power-supply registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/act8865-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/act8945a-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/act8945a-regulator.c

Purpose: platform child regulator driver for the Active-Semi ACT8945A PMIC, exposing three DCDC and four LDO voltage rails behind a parent MFD regmap.

Important APIs/types/functions: `struct act8945a_pmic` keeps the parent regmap and cached `op_mode[]`. `act8945a_set_suspend_state()`, `set_suspend_enable()`, `set_suspend_disable()`, `set_mode()`, and `get_mode()` implement regulator-specific control. `ACT89xx_REG()` builds the normal and alternate descriptor tables.

Control flow: probe allocates state, fetches the parent regmap, chooses normal or `active-semi,vsel-high` DCDC VSET registers, mirrors the parent OF node onto the platform child, registers all regulators, stores drvdata, and writes `ACT8945A_SYS_UNLK_REGS` to unlock expert registers. PM suspend writes `ACT8945A_SYS_CTRL` to request suspend on the next PWRHLD transition; shutdown writes the same register to request full shutdown.

State and persistence: `op_mode[]` is an in-memory cache updated only through this driver’s `set_mode()` path; `get_mode()` does not reread hardware. Voltage, enable, suspend, and shutdown state are PMIC registers. No persistent kernel storage exists.

Dependencies and integration: depends on parent MFD regmap, platform bus, regulator core, OF regulator descriptors, and PM hooks. It assumes the parent node contains regulator child definitions.

Risks and test signals: cached mode can be stale if firmware, bootloader, or another path changes mode bits. Suspend/shutdown programming is board-sensitive because it acts on PWRHLD transitions. Tests should cover both VSET banks, mode cache behavior, suspend register writes, shutdown path, parent-regmap absence, and regulator registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/act8945a-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/ad5398.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/ad5398.c

Purpose: exposes AD5398 and AD5821 current-output devices as a single regulator-current sink named `isink`.

Important APIs/types/functions: `struct ad5398_chip_info` stores I2C client, current range, selector mask/offset, and registered regulator. `ad5398_read_reg()`/`ad5398_write_reg()` exchange big-endian 16-bit values. Current ops are `ad5398_get_current_limit()`, `ad5398_set_current_limit()`, `ad5398_enable()`, `ad5398_disable()`, and `ad5398_is_enabled()`.

Control flow: `subsys_initcall()` registers the I2C driver. Probe obtains platform or OF regulator init data, allocates chip state, derives selector geometry from `ad5398_current_data_format`, registers the regulator, and stores client data. Runtime current changes compute the smallest selector satisfying `min_uA`, verify it fits `max_uA`, preserve the software power-down bit, and write the new 16-bit value.

State and persistence: current selector and enable state live in the chip register; `AD5398_SW_POWER_DOWN` is preserved across current writes and toggled by enable/disable. The driver has no cache except fixed format/range data.

Dependencies and integration: depends on I2C master send/receive, regulator machine/OF init data, and regulator-current APIs rather than voltage APIs.

Risks and test signals: `i2c_master_recv()` accepts any nonnegative byte count as success, so a short read could leave bad data; writes correctly require exactly two bytes. Tests should cover short I2C transfers, selector boundary math, min/max clamping, power-down preservation during current updates, OF init-data absence, and both device IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/ad5398.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/adp5055-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/adp5055-regulator.c

Purpose: I2C regulator driver for Analog Devices ADP5055, exposing three buck regulators with voltage selection, enable, active discharge, ramp delay, and power-save mode control.

Important APIs/types/functions: `struct adp5055` stores regmap, global timing, optional enable GPIOs, DVS limits, fast-transient settings, and power-good masks. `adp5055_of_parse_cb()` parses per-buck properties, `adp5055_parse_fw()` writes global/per-channel configuration, and `adp5055_set_mode()`/`get_mode()` control pulse-skipping mode bits.

Control flow: probe requires OF regulator init data, allocates state, initializes regmap, chooses each descriptor’s ramp delay table from `tset`, registers three regulators, then applies parsed firmware settings to DVS limit, enable-mode, OCP blanking, fast-transient, and power-good registers. Per-regulator OF callbacks run during registration and populate channel state.

State and persistence: driver state records GPIOs and parsed configuration; PMIC registers hold active voltage, enable mode, discharge, ramp, and DVS settings. The selected `adi,tset-us` is stored in memory and used to encode register values.

Dependencies and integration: depends on I2C, regmap access table for `0xd1..0xe0`, OF regulator parsing, GPIO descriptors, bitfield helpers, and regulator regmap ops.

Risks and test signals: `adi,tset-us` is parsed after descriptors are registered, so non-default timing may not affect the ramp-delay table exposed to regulator core. Error returns pass positive out-of-range values into `dev_err_probe()`. Tests should cover default and 20800 us `tset`, GPIO versus software enable, all DVS limit bounds, fast-transient string matching, mode bit shifts per channel, and probe deferral on GPIO/regmap errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/adp5055-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/anatop-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/anatop-regulator.c

Purpose: generic Freescale/NXP ANATOP syscon regulator driver, mainly for i.MX analog LDO-style regulators described entirely by DT bit offsets and voltage ranges.

Important APIs/types/functions: `struct anatop_regulator` stores dynamic descriptor, delay register geometry, cached selector, and bypass flag. Core ops implement enable/disable via selector values, bypass via FET full-on selector, cached set/get while disabled or bypassed, and `anatop_regmap_set_voltage_time_sel()` computes ramp-up delay from ANATOP delay bits.

Control flow: probe reads `regulator-name`, regulator init data, parent syscon regmap, voltage control offset/bit geometry, min selector, min/max voltage, and optional delay/enable fields. Core regulators with delay bits use `anatop_core_rops`; simpler regulators use `anatop_rops`, patched at runtime if an enable bit exists. It then registers one regulator device.

State and persistence: hardware selector zero means power gate and selector `0x1f` means full FET bypass for core regulators. The driver caches the intended voltage selector while disabled or bypassed. Register state persists in the syscon until changed.

Dependencies and integration: depends on OF-only platform data, parent syscon regmap, regulator core, and board-specific DT properties such as `anatop-reg-offset` and `anatop-vol-bit-width`.

Risks and test signals: `anatop_rops` is a mutable global ops table; once any instance adds enable ops, later simple instances share them. DT geometry errors can silently create wrong masks or invalid voltage counts. Tests should cover vddpu/vddpcie default selector fallbacks, bypass transitions, disabled voltage cache, missing required DT properties, ramp-delay calculation, and multi-instance behavior with mixed enable-bit support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/anatop-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/arizona-ldo1.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/arizona-ldo1.c

Purpose: registers the LDO1/DCVDD supply for Wolfson/Cirrus Arizona and Madera audio codecs, including variants where LDO1 powers the codec core itself.

Important APIs/types/functions: `struct arizona_ldo1` holds regulator, regmap, default init data, DCVDD consumer supply, and optional enable GPIO. High-current ops `arizona_ldo1_hc_set_voltage_sel()`/`get_voltage_sel()` treat the highest selector as a separate high-power bit. `arizona_ldo1_common_init()` handles shared OF/platform-data/GPIO registration.

Control flow: Arizona and Madera platform drivers allocate state from the parent MFD, choose a descriptor and default constraints based on chip type, parse optional `ldo1` child and `DCVDD-supply`, request `wlf,ldoena`, register the regulator, and update parent flags (`external_dcvdd` or `internal_dcvdd`). Remove releases the manually acquired GPIO.

State and persistence: parent MFD flags record whether DCVDD is external or internal. Regulator settings live in codec regmap registers; enable GPIO state is external hardware state. No persistent file state exists.

Dependencies and integration: depends on Arizona/Madera MFD regmaps, platform data, OF regulator init data, GPIO descriptors, and regulator core. Probe is forced synchronous because codec core power relationships are ordering-sensitive.

Risks and test signals: GPIO is intentionally non-devm and must be put on remove; probe failure after acquisition relies on manual cleanup only through remove not failure unwind. DCVDD external detection depends on phandle and consumer counts. Tests should cover chip-type descriptor selection, high-current selector behavior, `DCVDD-supply` external cases, missing GPIO, and parent flag updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/arizona-ldo1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/arizona-micsupp.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/arizona-micsupp.c

Purpose: provides the microphone supply regulator (`MICVDD`) for Arizona and Madera codec families, including charge-pump bypass and DAPM pin synchronization.

Important APIs/types/functions: `struct arizona_micsupp` stores regulator, regmap, DAPM pointer, descriptor, default init data, and a work item. `arizona_micsupp_enable()`, `disable()`, and `set_bypass()` wrap regmap regulator ops and schedule `arizona_micsupp_check_cp()`, which forces or disables the ASoC DAPM `MICSUPP` pin based on charge-pump state.

Control flow: platform probe chooses normal or extended voltage range descriptors by codec type, fills default constraints, optionally parses a `micvdd` child node, clears bypass to default regulated mode, registers the regulator, and stores driver data. Madera uses the extended descriptor with different register definitions and supply name.

State and persistence: state is devm-managed driver data plus pending work. Hardware state lives in codec regmap enable, bypass, and voltage-selector bits. DAPM state is updated asynchronously after successful regulator state changes.

Dependencies and integration: integrates regulator core, Arizona/Madera MFDs, ASoC DAPM, OF/platform init data, and workqueues. It assumes the parent codec provides a stable DAPM context pointer.

Risks and test signals: asynchronous DAPM work can race driver removal because there is no explicit cancel path. `regmap_update_bits()` clearing bypass during init is not checked for errors. Tests should cover enable/disable/bypass DAPM transitions, null DAPM pointer, normal versus extended ranges, Madera register mapping, and regulator registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/arizona-micsupp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/as3711-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/as3711-regulator.c

Purpose: platform child regulator driver for the AMS AS3711 PMIC, exposing four step-down and eight LDO regulators through the parent MFD regmap.

Important APIs/types/functions: descriptor macro `AS3711_REG()` builds `as3711_reg_desc[]`. `as3711_set_mode_sd()` and `as3711_get_mode_sd()` map regulator FAST/NORMAL/IDLE modes to AS3711 SD fast and low-noise bits. `as3711_regulator_parse_dt()` fills platform-data init arrays from OF matches.

Control flow: `subsys_initcall()` registers the platform driver. Probe requires `struct as3711_regulator_pdata`, optionally parses parent `regulators` child with `of_regulator_match()`, then registers each descriptor with the parent regmap and per-rail init data/of node.

State and persistence: no private runtime allocation beyond stack arrays; persistent state is PMIC register contents. Platform data carries init constraints and OF nodes during probe. SD mode bits are read/written directly each time.

Dependencies and integration: depends on AS3711 MFD definitions/register map, platform data supplied by the parent, OF regulator matching, regmap, and regulator core.

Risks and test signals: OF probing still fails without platform data, so the parent MFD must allocate/populate it even on DT systems. Step-up output is noted but not modeled. Tests should cover all SD mode mappings, LDO voltage range tables, OF node matching, missing platform data, parent regmap errors, and registration failures midway through the rail list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/as3711-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/as3722-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/as3722-regulator.c

Purpose: regulator driver for AMS AS3722 PMIC, supporting seven SD converters and eleven LDOs with current limits, external enable control, bypass, fast/normal mode, and optional LDO3 tracking.

Important APIs/types/functions: `as3722_reg_lookup[]` maps each regulator ID to register addresses, masks, supply names, and sleep-control fields. `struct as3722_regulators` owns generated descriptors and parsed config. Key functions include `as3722_get_regulator_dt_data()`, `as3722_sd_get_mode()`, `as3722_sd_set_mode()`, `as3722_extreg_init()`, `as3722_ldo3_set_tracking_mode()`, and `as3722_sd0_is_low_voltage()`.

Control flow: probe allocates state, parses the parent `regulators` node, then builds one descriptor per ID by combining lookup metadata with regulator-type-specific ops and voltage/current tables. It registers each regulator and, when `ams,ext-control` is present, enables the regulator and programs external control routing.

State and persistence: parsed per-rail config stores init data, tracking flag, and external control selection. Descriptors are runtime-generated but devm-owned. Persistent behavior is PMIC register state, including fuse-dependent SD0 low-voltage range and sleep-control routing.

Dependencies and integration: depends on AS3722 MFD helper APIs (`as3722_read/update_bits`), parent regmap, OF regulator parsing, and regulator core current-limit/bypass helpers.

Risks and test signals: invalid `ams,ext-control` values are only warned and ignored; external control forces an enable during probe. LDO6 bypass uses the same value for on and off, requiring hardware-specific validation. Tests should cover SD0 fuse variants, LDO3 tracking, ext-control routing 1..3, current-limit selectors, bypass, unsupported SD mode registers, malformed DT, and partial registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/as3722-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/atc260x-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/atc260x-regulator.c

Purpose: platform child regulator driver for Actions Semi ATC2603C and ATC2609A PMICs, exposing DCDC, LDO, switch-LDO, bypass, discharge, fixed, and range-based rails.

Important APIs/types/functions: descriptor macro families build `atc2603c_reg[]`, `atc2603c_reg_dcdc2_ver_b`, and `atc2609a_reg[]`. Ops tables select generic regmap helpers, pickable ranges, bypass, active discharge, or no ops. `struct atc260x_regulator_data` stores fixed voltage ramp times used by `atc260x_dcdc_set_voltage_time_sel()` and `atc260x_ldo_set_voltage_time_sel()`.

Control flow: probe gets the parent `struct atc260x`, allocates timing data, selects descriptor table by `ic_type`, applies ATC2603C revision-B DCDC2 override when needed, and registers every descriptor against the parent regmap.

State and persistence: runtime state is only the devm timing structure. Voltage, enable, bypass, and discharge state are PMIC register bits. Voltage ramp time is a conservative constant per regulator class/chip, returned only when selector increases.

Dependencies and integration: depends on ATC260x MFD register definitions, regmap, platform bus, OF regulator matching embedded in descriptors, and regulator core helpers.

Risks and test signals: large macro-generated descriptors make bitfield mistakes easy. LDO12 has no ops and only a fixed voltage, so consumers cannot enable/disable it through this driver. Tests should cover both chip families, ATC2603C revision-B DCDC2, switch-LDO inverted enable/discharge, pickable LDO ranges on ATC2609A, ramp-time reporting, and unsupported `ic_type`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/atc260x-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/aw37503-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/aw37503-regulator.c

Purpose: I2C regulator driver for the AWINIC AW37503 dual output device, exposing positive (`outp`) and negative (`outn`) 4.0 V to 6.0 V rails.

Important APIs/types/functions: `struct aw37503_regulator` stores per-output optional enable GPIO state. `aw37503_regulator_enable()`, `disable()`, and `is_enabled()` are GPIO-oriented, while voltage and active-discharge use regulator regmap helpers. `aw37503_of_parse_cb()` obtains per-regulator `enable` GPIOs from child nodes.

Control flow: probe initializes a regmap with an access table excluding holes, allocates chip state, then registers VPOS and VNEG descriptors. Each descriptor has its own voltage register and active-discharge bit in `AW37503_REG_APPS`. Enabling drives the GPIO high if present and disables hardware auto-discharge if constraints require active discharge off.

State and persistence: `ena_gpio_state` caches logical enable state when a GPIO is present; without GPIO, `is_enabled()` always reports enabled. Voltage and discharge are stored in chip registers.

Dependencies and integration: depends on I2C, regmap, regulator core, OF regulator child matching, and optional GPIO descriptors. Supply name is `vin` for both rails.

Risks and test signals: GPIO absence makes software unable to disable a rail but still report enabled. Active-discharge correction happens only on enable and depends on `rdev->constraints` being valid. Tests should cover both rails, GPIO probe defer and absent-GPIO paths, voltage selector limits, active discharge enable/disable, and regmap access-table holes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/aw37503-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/axp20x-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/axp20x-regulator.c

Purpose: shared regulator driver for many X-Powers AXP PMIC variants, including AXP20x/22x/313A/323/717/803/806/809/813/15060 families, exposing variant-specific DCDC, LDO, switch, RTC, boost, and GPIO-LDO rails.

Important APIs/types/functions: descriptor macros `AXP_DESC*()` generate large variant tables. `axp20x_set_ramp_delay()` handles AXP209 DCDC2/LDO3 slew settings; `axp20x_regulator_enable_regmap()` implements the AXP209 LDO3 soft-start quirk; `axp20x_set_dcdc_freq()` parses and clamps DCDC frequency; `axp20x_set_dcdc_workmode()` writes PWM/auto mode bits; `axp20x_is_polyphase_slave()` suppresses slave rails in multi-phase setups.

Control flow: probe selects a descriptor table from parent `axp20x->variant`, parses top-level regulator properties, then loops through regulators. It skips polyphase slave rails and unsupported AXP813 FLDO3, dynamically patches supply names for internally chained rails, registers each regulator, applies per-regulator `x-powers,dcdc-workmode`, and optionally registers a `drivevbus` regulator after configuring the N_VBUSEN pin.

State and persistence: runtime state is mostly parent `struct axp20x_dev` plus devm-cloned descriptors for dynamic supply names. Hardware register state persists for voltage, enable, workmode, frequency, ramp, and polyphase settings. There is no separate persistent kernel state.

Dependencies and integration: depends on AXP20x MFD register definitions/regmap, OF regulator bindings, regulator core, delay helpers, and platform bus. Variant tables encode hardware quirks and measured deviations from some datasheets.

Risks and test signals: descriptor table drift is the main risk because many variants share registers with subtle differences. `axp20x_regulator_parse_dt()` errors are intentionally ignored by probe. Tests should cover every variant table, AXP209 LDO3 soft-start, DCDC frequency clamping/fixed-frequency rejection, workmode property writes, polyphase skip logic, dynamic supply-name chaining, drive-vbus registration, and AXP813 FLDO3 omission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/axp20x-regulator.c -->
