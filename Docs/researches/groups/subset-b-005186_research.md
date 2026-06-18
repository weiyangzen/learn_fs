# subset-b-005186 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rtq6752-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rtq6752-regulator.c

Purpose: implements the Richtek RTQ6752 I2C TFT LCD bias regulator driver. It exposes two voltage regulators, `rtq6752-pavdd` and `rtq6752-navdd`, with linear 5.0 V to 7.3 V selector programming, active discharge control, shared chip-enable GPIO handling, and fault reporting through the regulator framework.

Important APIs/types/functions: `struct rtq6752_priv` stores the regmap, optional `enable` GPIO, mutex, and bitmask of enabled rails. `rtq6752_set_vdd_enable()` and `rtq6752_set_vdd_disable()` coordinate the shared chip enable, regcache-only transitions, and per-rail `regulator_enable_regmap()`/`regulator_disable_regmap()`. `rtq6752_get_error_flags()` maps PAVDD/NAVDD fault bits to `REGULATOR_ERROR_REGULATION_OUT`. `rtq6752_init_device_properties()` programs minimum on-delay and soft-start values. The static `rtq6752_regulator_descs[]` defines voltage, enable, active-discharge, OF child names, and enable time for both rails.

Control flow: probe allocates state, obtains the optional GPIO as initially high, waits for I2C readiness, marks both rails logically enabled, initializes the I2C regmap with maple cache defaults, writes minimum delay/soft-start settings, then registers both regulator descriptors. When the first rail is enabled after the chip was fully off, the driver raises the GPIO, exits cache-only mode, syncs cached registers, marks the rail enabled, and writes the regulator enable bit. When the last rail is disabled, it switches regmap to cache-only, marks it dirty, and drops the GPIO.

State and persistence: runtime state is only the `enable_flag` bitmask, GPIO level, regmap cache, and hardware registers. Voltage settings and active discharge live in chip registers while powered; when the optional GPIO disables the chip, the dirty regcache is later restored on re-enable. No settings are persisted outside the chip.

Dependencies and integration: depends on I2C, regmap, optional GPIO descriptors, OF nodes under `regulators`, and regulator core helpers. It binds `richtek,rtq6752` and uses asynchronous I2C probe. Board DT must provide `pavdd`/`navdd` regulator child constraints and optionally an `enable` GPIO.

Risks and test signals: the shared GPIO/regcache path is concurrency-sensitive, so enable/disable interleavings across both rails should be tested. Probe assumes both rails are on after requesting `GPIOD_OUT_HIGH`, which can affect boot sequencing if constraints later disable one rail. Error-flag reporting depends on fault register availability while the chip is powered. Test with both rails enabled/disabled independently, regcache sync after full power-down, active-discharge writes, fault bit injection, missing GPIO, and probe failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rtq6752-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/s2dos05-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/s2dos05-regulator.c

Purpose: provides the regulator child driver for Samsung S2DOS05 PMICs, registering four LDOs and one buck regulator through the Samsung MFD parent regmap.

Important APIs/types/functions: `struct s2dos05_data` holds the parent PMIC regmap and device pointer. `BUCK_DESC()` and `LDO_DESC()` build `struct regulator_desc` entries with linear voltage tables, enable masks, enable times, and active discharge bits from `<linux/regulator/s2dos05.h>`. `s2dos05_ops` uses standard regmap-backed regulator helpers for voltage selection, enable/disable, enable state, voltage transition time, and active discharge. `s2dos05_pmic_probe()` performs all registration.

Control flow: the platform driver is created by the Samsung MFD core as `s2dos05-regulator`. Probe obtains `sec_pmic_dev` from the parent, adopts the parent's OF node if needed, stores the PMIC regmap, and iterates the static descriptor table registering `ldo1` to `ldo4` and `buck` against the platform device. Failures stop the loop and return through `dev_err_probe()`.

State and persistence: the driver has no mutable state beyond the allocated wrapper and hardware register contents. Regulator settings are stored in the S2DOS05 PMIC registers and managed through regmap; no suspend or software cache policy is implemented here.

Dependencies and integration: integrates with Samsung MFD core (`struct sec_pmic_dev`), the regulator core, OF regulator matching under `regulators`, and the S2DOS05 register/mask header. Consumers see standard regulator operations and child names matching the descriptor `of_match` strings.

Risks and test signals: descriptor macro correctness is the main risk because register, enable, and active-discharge fields come from header macros. The driver does not pass a `config.regmap` explicitly, relying on descriptor/regmap ownership through the parent setup path, so probe should be tested on actual MFD instantiation. Test all five regulators for voltage get/set, enable state, active discharge toggling, missing OF node fallback, and failure when parent regmap is unavailable or malformed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/s2dos05-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/s2mpa01.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/s2mpa01.c

Purpose: implements regulator support for Samsung S2MPA01 PMICs, exposing 26 LDOs and 10 bucks from the Samsung MFD parent as regmap-backed voltage regulators.

Important APIs/types/functions: `struct s2mpa01_info` tracks grouped ramp-delay state for buck rails. `get_ramp_delay()` converts a requested microvolt-per-microsecond delay into the PMIC two-bit selector. `s2mpa01_regulator_set_voltage_time_sel()` computes transition time based on the rail's configured ramp group. `s2mpa01_set_ramp_delay()` programs ramp enable bits and ramp selector fields in `S2MPA01_REG_RAMP1`/`RAMP2`. `s2mpa01_ldo_ops` and `s2mpa01_buck_ops` define common regulator ops, with buck ops adding custom ramp support.

Control flow: probe obtains the parent `sec_pmic_dev`, allocates ramp-delay state, builds a `regulator_config` using the parent device and PMIC regmap, then registers every descriptor in static order. Descriptor macros compute LDO and buck voltage selector, enable, min voltage, step, and ramp defaults from Samsung PMIC register definitions. Runtime voltage changes go through regulator core helpers; ramp changes update both software state and PMIC ramp registers before voltage transition timing is reported.

State and persistence: software state holds the maximum selected ramp delay for shared ramp groups such as buck2/4, buck1/6, and buck8/9/10. Hardware state lives in PMIC voltage, enable, and ramp registers. There is no persistent state outside the PMIC and no explicit suspend handling in this file.

Dependencies and integration: depends on the Samsung MFD core, `linux/mfd/samsung/s2mpa01.h`, regmap, platform devices, and regulator OF child nodes named `LDO#` and `BUCK#` under `regulators`. The platform ID is `s2mpa01-pmic` and probe is asynchronous.

Risks and test signals: ramp groups share hardware fields, so setting a lower ramp on one rail may retain a larger previously requested group value. `get_ramp_delay()` clamps values above the supported selector range. Test signals include all regulator registrations, buck ramp enable/disable for buck1-4, shared ramp behavior for grouped bucks, voltage transition timing, invalid regulator IDs, and standard LDO/buck voltage and enable operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/s2mpa01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/s2mps11.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/s2mps11.c

Purpose: is the large Samsung PMIC regulator driver for S2MPG10, S2MPG11, S2MPS11, S2MPS13, S2MPS14, S2MPS15, S2MPU02, and S2MPU05 variants. It turns MFD child devices into regulator-core registrations for many LDO and buck rails, including variant-specific voltage ranges, ramp control, suspend disable modes, and optional external GPIO/control-signal enable paths.

Important APIs/types/functions: `struct s2mps11_info` stores device type, ramp-delay groups, and suspend-state bitmap. `struct s2mpg10_regulator_desc` extends `struct regulator_desc` with enable ramp rate and external-control selector registers. Shared helpers include `get_ramp_delay()`, `s2mps11_regulator_enable()`, `s2mps11_regulator_set_suspend_disable()`, `s2mps11_of_parse_gpiod()`, `s2mpg10_of_parse_cb()`, `s2mps11_handle_ext_control()`, and `s2mps11_pmic_probe()`. Variant-specific ops handle S2MPS11 ramp groups, S2MPG10/11 asymmetric voltage ramp timing, S2MPS14 GPIO control, and S2MPU02 ramp selector programming.

Control flow: probe identifies the PMIC variant from the platform ID, selects the matching descriptor table, duplicates S2MPG10/11 extended descriptors because their parse callback mutates ops and enable values, adopts the parent's OF node, then registers each regulator against the parent PMIC regmap. OF parse callbacks may request `enable` GPIOs or parse `samsung,ext-control`, switch descriptors to no-op enable ops, store PCTRL selector values, and set `enable_val`. After registration, `s2mps11_handle_ext_control()` writes PCTRL selector fields and enables the hardware bit for external-control rails. Standard runtime paths are regulator-core callbacks for enable, disable, voltage selection, ramp delay, and suspend-disable.

State and persistence: runtime state includes ramp group values, selected device type, and a bitmap of rails that should use suspend-disable encoding once enabled. S2MPG descriptor copies hold per-instance external-control state derived from DT. Persistent electrical state is in PMIC registers; software state is rebuilt on probe and is not stored across reboots.

Dependencies and integration: depends on Samsung MFD core, many Samsung PMIC register headers, `dt-bindings/regulator/samsung,s2mpg10-regulator.h`, GPIO descriptors, OF regulator child nodes, regmap, and the regulator framework. Integration is broad: regulator consumers use variant-specific child names such as lowercase S2MPG/S2MPU names and uppercase S2MPS names, and board DT can request external control on selected rails.

Risks and test signals: the mutable descriptor-copy path for S2MPG10/11 is subtle; using static descriptors directly would leak parsed external-control state across devices. External control requires correct mapping from DT enum to PCTRL selector and careful handling of valid zero selector values. Suspend-disable state can intentionally delay hardware writes until a rail is enabled. Test all platform IDs, descriptor counts, S2MPG10/11 external-control validation, GPIO probe defer, S2MPS14 LDO10-12 GPIO control, ramp timing for rising and falling DVS, suspend-disable on unsupported always-on rails, and registration failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/s2mps11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/s5m8767.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/s5m8767.c

Purpose: implements regulator support for Samsung S5M8767 PMICs, including 28 LDOs, 9 buck regulators, per-regulator operating modes, BUCK2/3/4 GPIO-DVS voltage selection, ramp configuration, and BUCK9 external-control GPIO support.

Important APIs/types/functions: `struct s5m8767_info` stores parent PMIC, opmode array, GPIO-DVS tables, ramp flags, and GPIO descriptors. `s5m8767_get_register()` maps regulator IDs to enable registers and mode-specific enable values. `s5m8767_get_vsel_reg()` maps regulators to voltage selector registers, including GPIO-DVS indexed BUCK2/3/4 slots. `s5m8767_set_voltage_sel()` either writes a selector through regmap or changes DVS GPIO index. `s5m8767_pmic_dt_parse_pdata()` translates DT regulators, op modes, DVS voltage arrays, ramp settings, and external-control GPIOs into Samsung platform data.

Control flow: probe requires parent platform data, optionally populates it from OF, rejects configurations that enable GPIO-DVS on more than one of BUCK2/3/4, initializes BUCK2-4 default DVS registers, converts configured DVS voltages to selectors, obtains DVS and discharge GPIOs, enables DVS mode bits, fills all DVS selector slots, configures ramp bits, then registers only regulators listed in platform data. For each registered regulator it patches the global descriptor with voltage range, vsel register, enable register, enable mask, and enable value before calling `devm_regulator_register()`. BUCK9 can be handed an enable GPIO and switched to PMIC GPIO control after registration.

State and persistence: software tracks the currently selected DVS GPIO index and voltage selector tables for the active GPIO-DVS buck. PMIC register programming stores voltage, enable, DVS, opmode, and ramp state. The descriptor table is static and mutated at probe time, so multi-instance use would share descriptor mutations.

Dependencies and integration: depends on the Samsung MFD core, S5M8767 register definitions, OF regulator matching, GPIO descriptors, and regmap. Board DT supplies `regulators`, per-rail `op_mode`, optional `s5m8767,pmic-ext-control`, BUCK DVS voltage arrays, default DVS index, ramp-enable properties, and DVS/DS GPIOs.

Risks and test signals: `s5m8767_set_voltage_sel()` scans GPIO-DVS voltage arrays until a matching selector without an explicit bound, so invalid selectors are risky. Static descriptor mutation is fragile if more than one PMIC instance is possible. Several `regmap_write()`/`update_bits()` calls during probe do not check return values. Test DT parsing, invalid DVS index fallback, mutually exclusive DVS validation, missing GPIO errors, opmode-to-enable mapping, BUCK9 external control, DVS selector changes in both GPIO ordering directions, and ramp-delay programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/s5m8767.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sc2731-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/sc2731-regulator.c

Purpose: registers Spreadtrum SC2731 PMIC buck and LDO regulators as simple linear, regmap-backed regulators after unlocking the PMIC regulator write-protect register.

Important APIs/types/functions: `enum sc2731_regulator_id` names three DCDC bucks and fourteen LDOs. `SC2731_REGU_LINEAR()` builds descriptors with inverted enable semantics, voltage selector registers, masks, min/max/step values, and child OF names. `sc2731_regu_linear_ops` uses standard regmap enable, disable, state, list, get, and set voltage helpers. `sc2731_regulator_unlock()` writes `SC2731_WR_UNLOCK_VALUE` to `SC2731_PWR_WR_PROT`.

Control flow: probe obtains the parent regmap with `dev_get_regmap()`, writes the unlock value, then iterates the static descriptor array and registers every regulator. Runtime enable/disable writes PD bits with `enable_is_inverted = true`, so clearing a power-down bit enables the rail.

State and persistence: there is no private mutable software state. All regulator state is in SC2731 PMIC registers. The unlock write is a probe-time hardware side effect and is not represented in software after registration.

Dependencies and integration: depends on a parent MFD/regmap device named by the platform driver `sc27xx-regulator`, regulator core helpers, and DT child nodes matching names such as `BUCK_CPU0`, `LDO_CAMA0`, and `LDO_SRAM`.

Risks and test signals: unlock failure prevents all regulators. Inverted enable fields must match hardware power-down semantics or rails will be reversed. Test with parent regmap absent, write-protect failure, every descriptor's voltage limits, enable/disable polarity, and all child regulator constraints from the SC2731 binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sc2731-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/scmi-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/scmi-regulator.c

Purpose: exposes ARM SCMI Voltage Protocol domains as Linux regulators. It maps SCMI voltage-domain metadata and DT `regulators` child nodes into fixed, linear, or discrete regulator descriptors.

Important APIs/types/functions: global `voltage_ops` holds SCMI voltage protocol operations. `struct scmi_regulator` owns the SCMI domain id, protocol handle, OF node, descriptor, config, and registered regulator. `scmi_reg_enable()`, `scmi_reg_disable()`, and `scmi_reg_is_enabled()` wrap SCMI `config_set/get`. `scmi_reg_get_voltage_sel()` and `scmi_reg_set_voltage_sel()` translate between SCMI absolute microvolts and regulator selectors. `scmi_config_linear_regulator_mappings()` and `scmi_config_discrete_regulator_mappings()` build descriptor voltage maps from firmware-reported levels.

Control flow: probe gets the SCMI voltage protocol, queries domain count, allocates a slot array for all domains, scans the SCMI platform node's `regulators` child for entries with a `reg` domain number, rejects duplicate or out-of-range mappings, then initializes and registers each valid domain. Initialization skips domains that support negative voltages, names the descriptor from firmware, sets OF matching to the full child node name, selects fixed/linear/table ops, and stores driver data. Remove drops OF node references.

State and persistence: software state is a per-domain descriptor/config and OF node reference. Persistent regulator state is owned by SCMI firmware; Linux only sends on/off and level commands through the protocol. No local caching of voltage or enable state is kept.

Dependencies and integration: depends on the SCMI bus, voltage protocol, OF regulator children, and regulator framework. It integrates with firmware-defined voltage domains rather than direct hardware registers, so supported operations are intentionally limited to enable state and voltage level.

Risks and test signals: the file-scoped `voltage_ops` pointer is shared, which assumes one effective SCMI voltage ops table. Firmware can provide malformed ranges; negative intervals are rejected but zero step in a nonzero linear range would be dangerous if firmware allowed it. Registration failures are skipped rather than aborting all domains. Test fixed, linear, and discrete domains; negative-voltage skip; duplicate `reg` entries; out-of-range domain IDs; SCMI command failures; remove path OF reference balancing; and DT nodes whose full names must match descriptor OF matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/scmi-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sky81452-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/sky81452-regulator.c

Purpose: implements the regulator child for the Skyworks SKY81452 MFD, exposing the `LOUT` output as a voltage regulator.

Important APIs/types/functions: `sky81452_reg_ops` uses regmap-backed voltage selection and enable helpers. `sky81452_reg_ranges[]` defines two linear ranges, 4.5 V to 8.0 V in 250 mV steps and 9.0 V to 25.0 V in 1 V steps. `sky81452_reg` binds selector bits in register 3 and enable bit `SKY81452_LEN` in register 1. `sky81452_reg_probe()` registers the regulator using the parent-provided regmap and optional platform init data.

Control flow: the platform device is created by the SKY81452 MFD. Probe points `config.dev` at the parent, reads init data from platform data, uses the child's OF node, gets the regmap from parent driver data, and calls `devm_regulator_register()`. Runtime behavior is entirely delegated to regulator core regmap helpers.

State and persistence: no private mutable state is stored beyond the registered regulator device. Voltage and enable state live in the parent chip registers.

Dependencies and integration: depends on the SKY81452 MFD parent to provide a regmap as driver data, regulator child node `lout` under `regulator`, and optional board constraints. The driver name is `sky81452-regulator`.

Risks and test signals: parent-driver-data must be a valid regmap or registration will later fail through regmap operations. The unusual `regulators_node = "regulator"` singular must match binding/MFD child structure. Test voltage selector mapping across the range boundary, enable bit writes, missing platform data, OF child matching, and MFD probe ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sky81452-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/slg51000-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/slg51000-regulator.c

Purpose: implements the Dialog/Renesas SLG51000 I2C high-PSRR multi-output regulator driver, registering seven LDO outputs, deriving their voltage limits from chip MIN/MAX registers, supporting optional GPIO enables, and reporting over-current/over-temperature events.

Important APIs/types/functions: `struct slg51000` owns device, regmap, regulator descriptors/devices, optional chip-select GPIO, and IRQ. `slg51000_regmap_config` constrains 16-bit register access using writable/readable/volatile tables from `slg51000-regulator.h`. `slg51000_of_parse_cb()` captures optional `enable` GPIOs. `slg51000_regulator_init()` reads per-LDO MIN/MAX ranges and mode bits, adjusts `regulator_desc` fields, switches LDO5/6 to switch ops when bypass mode is selected, and registers all LDOs. `slg51000_irq_handler()` reads event/status/mask registers and sends regulator notifier events.

Control flow: I2C probe allocates state, asserts optional `dlg,cs` GPIO, waits 10 ms, initializes regmap, registers regulators, logs fault state, and optionally requests a threaded IRQ. During regulator initialization, LDO1/2 use their voltage-range bit to choose low or high base voltage; LDO5/6 may become non-voltage switches; all others use OTP-programmed min/max selector windows. IRQ handling bulk-reads event/status/mask triplets for every LDO plus system control, reports unmasked over-current for specific rails, reports high-temperature warning to rails whose status looks otherwise valid, and handles OTP CRC events.

State and persistence: descriptor fields are mutated at probe according to OTP/config registers. Runtime state holds regulator device pointers for notifier delivery and optional GPIO/IRQ handles. Actual voltage windows, bypass mode, events, masks, and enable matrix bits are stored in SLG51000 registers/OTP.

Dependencies and integration: depends on I2C, regmap access tables, GPIO descriptors, regulator OF child nodes under `regulators`, threaded IRQs, and notifier integration. The header provides all register and bitfield constants used by access control, voltage setup, fault logging, and IRQ decoding.

Risks and test signals: `regls_desc` is static and mutated at probe, so multiple devices could share adjusted descriptor state. `slg51000_of_parse_cb()` ignores GPIO errors, including defer, which can mask incomplete GPIO providers. IRQ event interpretation depends on three adjacent event/status/mask registers per rail. Test OTP/min/max-derived voltage windows, LDO1/2 high/low range, LDO5/6 bypass-as-switch, optional chip-select timing, optional enable GPIOs, regmap access denials, no-IRQ probe, over-current notifier delivery, high-temperature notifier delivery, and fault-log reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/slg51000-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/slg51000-regulator.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/slg51000-regulator.h

Purpose: defines the SLG51000 register map and bitfield masks consumed by `slg51000-regulator.c`. It is a hardware contract header rather than executable driver logic.

Important APIs/types/functions: the header exports register addresses for system control, GPIO configuration/status, LUT and mux arrays, power sequencer settings, LDO1-LDO7 voltage/control/event/status/IRQ registers, OTP event/mask/lock registers, and global lock control. It also defines bit shift/mask pairs for pattern IDs, matrix/resource control, fault logs, high-temperature events, GPIO status, power-sequencer timing, voltage selector/min/max fields, LDO event/status flags, bypass mode bits, OTP CRC, and global LDO lock bits.

Control flow: there is no runtime control flow. The C file uses these constants to construct regmap access tables, read OTP-configured voltage windows, detect LDO5/6 bypass mode, clear/log fault state, and decode IRQ events into regulator notifications.

State and persistence: the header itself has no state. The named registers correspond to hardware state, some of which is volatile event/status state and some of which is OTP or configuration-backed.

Dependencies and integration: guarded by `__SLG51000_REGISTERS_H__` and included only by the SLG51000 regulator driver. It integrates with the Linux regmap and regulator code indirectly by providing stable addresses/masks for descriptor construction and event handling.

Risks and test signals: any incorrect address or mask silently corrupts voltage programming, IRQ decoding, or regmap access permissions. The readable/writable/volatile tables in the C file must stay aligned with this header. Test signals include compile coverage, regmap reads/writes to every descriptor field, fault and event decoding against datasheet traces, and review of lock/OTP masks before enabling future write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/slg51000-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/spacemit-p1.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/spacemit-p1.c

Purpose: provides regulator support for the SpacemiT P1 PMIC, registering six bucks, four analog LDOs, and seven digital LDOs using the parent PMIC regmap.

Important APIs/types/functions: `enum p1_regulator_id` names all rails. `p1_regulator_ops` uses linear-range voltage selection, regmap enable/disable, enable state, and voltage transition timing helpers. `p1_buck_ranges[]` covers two buck voltage segments with selector 255 reserved for sleep disable. `p1_ldo_ranges[]` starts at selector 11, with selector 0 reserved for suspend. `P1_REG_DESC()` and wrapper macros derive register offsets, selector masks, supply names, and OF names.

Control flow: the platform driver `spacemit-p1-regulator` is probed by the parent PMIC. Probe sets `config.dev` to the parent so the regulator core can use the parent regmap, then registers each static descriptor. Runtime operations are standard regmap helper callbacks.

State and persistence: this file stores no private state. Voltage selectors and enables live in PMIC registers. Sleep/suspend-reserved selector values are documented by the ranges but no custom suspend callback is implemented here.

Dependencies and integration: depends on the parent PMIC platform device/regmap, OF child nodes named `buck1`-`buck6`, `aldo1`-`aldo4`, and `dldo1`-`dldo7`, and regulator consumers for `vin#`, `aldoin`, `dldoin1`, and `dldoin2` supplies.

Risks and test signals: register offset math is macro-driven and should be checked against the PMIC datasheet. Buck `n_voltages = 255` intentionally excludes selector 255; LDO ranges expose 128 selectors while valid output starts at selector 11. Test all descriptors for vsel/en register addresses, voltage list/map around range boundaries, parent regmap lookup, and board constraints that avoid sleep/suspend selector misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/spacemit-p1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stm32-booster.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/stm32-booster.c

Purpose: exposes STM32 embedded analog booster blocks as fixed 3.3 V regulators backed by SYSCFG regmap bits. It supports both STM32H7 single set/clear-by-update behavior and STM32MP1 separate set/clear registers.

Important APIs/types/functions: `stm32h7_booster_desc` uses standard regmap enable/disable/is_enabled helpers on `STM32H7_SYSCFG_PMCR`. `stm32mp1_booster_enable()` writes `STM32MP1_SYSCFG_PMCSETR`; `stm32mp1_booster_disable()` writes `STM32MP1_SYSCFG_PMCCLRR`; `stm32mp1_booster_desc` uses those custom ops. `stm32_booster_probe()` looks up the `st,syscfg` phandle and picks the descriptor from OF match data.

Control flow: probe resolves the syscon regmap, obtains the variant descriptor from `device_get_match_data()`, populates regulator config from the platform node and `of_get_regulator_init_data()`, and registers one regulator. Runtime enable/disable either update the H7 PMCR bit through regmap helpers or write MP1 set/clear registers.

State and persistence: no private mutable state is stored. The booster enable state is in the STM32 SYSCFG register block and is reset according to SoC reset behavior.

Dependencies and integration: depends on OF compatibles `st,stm32h7-booster` and `st,stm32mp1-booster`, a `st,syscfg` phandle, regulator constraints, and the `vdda` supply.

Risks and test signals: MP1 `is_enabled` reads from the set register address, so correctness depends on that register reflecting state rather than being write-only. Test both compatibles, missing syscfg phandle, enable/disable register writes, fixed-voltage reporting, `vdda` supply constraints, and boot-time state readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stm32-booster.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stm32-pwr.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/stm32-pwr.c

Purpose: registers fixed-voltage STM32MP PWR internal regulators for 1.1 V, 1.8 V, and USB 3.3 V rails using memory-mapped PWR control bits.

Important APIs/types/functions: `struct stm32_pwr_reg` stores the mapped base address and ready bit. `stm32_pwr_reg_enable()` sets a regulator enable bit in `REG_PWR_CR3` and polls the matching ready bit. `stm32_pwr_reg_disable()` clears the enable bit and polls until disabled. `stm32_pwr_reg_is_enabled()` and `stm32_pwr_reg_is_ready()` read the same register. `stm32_pwr_desc[]` defines the three fixed regulators and supplies.

Control flow: probe maps the MMIO resource, then allocates one small private object per regulator with the common base and a per-regulator ready mask. Each descriptor is registered with its private data. Enable writes the bit and polls up to 20 ms; disable clears the bit and polls up to 20 ms.

State and persistence: private state only points at MMIO and records the ready mask. Hardware register bits hold enable/ready state. There is no suspend/resume or software persistence.

Dependencies and integration: depends on platform MMIO resources, OF compatibles `st,stm32mp1,pwr-reg` and `st,stm32mp13-pwr-reg`, regulator core, and consumers of `reg11`, `reg18`, and `usb33`.

Risks and test signals: direct read-modify-write on `REG_PWR_CR3` has no explicit locking, so concurrent regulator operations could race if the regulator core does not serialize them. Timeout values are arbitrary. Test MMIO mapping failure, each rail enable/disable timeout path, ready bit polarity, fixed voltage reporting, and simultaneous operations on different rails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stm32-pwr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stm32-vrefbuf.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/stm32-vrefbuf.c

Purpose: implements the STM32 voltage-reference buffer regulator. It exposes selectable VREF output voltages, manages the VREFBUF clock with runtime PM, and waits for hardware readiness when enabling.

Important APIs/types/functions: `struct stm32_vrefbuf` stores MMIO base, clock, and device. `stm32_vrefbuf_enable()` resumes runtime PM, clears high impedance, sets enable, and polls `STM32_VRR`. `stm32_vrefbuf_disable()` clears enable. `stm32_vrefbuf_set_voltage_sel()` and `stm32_vrefbuf_get_voltage_sel()` manipulate the `STM32_VRS` field. Runtime PM callbacks prepare/disable the clock. The descriptor `stm32_vrefbuf_regu` exposes four table voltages: 2.5 V, 2.048 V, 1.8 V, and 1.5 V.

Control flow: probe allocates private state, maps MMIO, obtains the clock, sets up runtime PM autosuspend, enables the clock, registers the regulator with OF init data, stores the regulator device as platform data, and drops the runtime PM reference. Runtime operations resume the device for register access and autosuspend afterward. Remove unregisters the regulator, disables the clock, and shuts down runtime PM.

State and persistence: private state tracks clock/MMIO handles. Hardware CSR bits store enable, high-Z, readiness, and voltage selection. Runtime PM state controls the clock and is rebuilt on probe.

Dependencies and integration: depends on platform MMIO, `st,stm32-vrefbuf` OF node, a clock, `vdda` supply, runtime PM, and regulator consumers such as ADC/DAC reference users.

Risks and test signals: probe uses non-devm `regulator_register()`, making remove cleanup mandatory. Enable failure attempts to restore disabled/high-Z state. Runtime suspend/resume uses the regulator device from driver data, so ordering around remove should be tested. Test voltage selector get/set, enable timeout and rollback, autosuspend clock transitions, system sleep PM force suspend/resume, missing clock/resource errors, and regulator unregister on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stm32-vrefbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stpmic1_regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/stpmic1_regulator.c

Purpose: implements regulator support for STPMIC1 PMICs, covering four bucks, six LDOs, VREF_DDR, boost, VBUS_OTG switch, and SW_OUT switch. It also supports buck operating modes, LDO3 bypass, pull-down control, over-current protection configuration, mask-reset behavior, and over-current IRQ notifications.

Important APIs/types/functions: `struct stpmic1_regulator_cfg` wraps a regulator descriptor plus mask-reset and over-current registers/masks. Descriptor macros `REG_BUCK`, `REG_LDO`, `REG_LDO3`, `REG_LDO4`, `REG_VREF_DDR`, `REG_BOOST`, `REG_VBUS_OTG`, and `REG_SW_OUT` build the static `stpmic1_regulator_cfgs[]`. `stpmic1_map_mode()`, `stpmic1_set_mode()`, and `stpmic1_get_mode()` translate buck normal/standby mode. `stpmic1_set_icc()` enables switch-off-on-over-current protection. `stpmic1_regulator_register()` registers one regulator, applies `st,mask-reset`, and requests optional over-current IRQs.

Control flow: probe matches DT regulator child nodes with `of_regulator_match()`, then registers every configured regulator ID. Each registration uses the parent `struct stpmic1` regmap, descriptor/init data/OF node from the match table, and configuration pointer as driver data. Optional `st,mask-reset` sets a PMIC mask-reset bit. If the child node provides an IRQ, the driver requests a shared threaded handler that emits `REGULATOR_EVENT_OVER_CURRENT`.

State and persistence: no dynamic per-regulator state is allocated here beyond regulator devices and IRQ registrations. Hardware registers hold voltage, enable, mode, bypass, pull-down, active-discharge, mask-reset, and OCP state. Mask-reset and OCP settings are persistent only according to PMIC hardware behavior.

Dependencies and integration: depends on STPMIC1 MFD parent, `<dt-bindings/mfd/st,stpmic1.h>`, OF regulator child names such as `buck1`, `ldo3`, `boost`, and `pwr_sw1`, regmap, regulator core, and OF IRQs.

Risks and test signals: `stpmic1_get_mode()` ignores `regmap_read()` errors, so bus failures can be misreported as normal mode. `stpmic1_set_icc()` only supports enabling protection with severity `REGULATOR_SEVERITY_PROT`, not programmable limits or warnings. Probe registers all static entries even if a match lacks init data, which relies on regulator core handling. Test every voltage range including LDO3 DDR-mode selector, bypass, buck mode mapping, pull-down, active discharge on switches, `st,mask-reset`, optional IRQ notification, and parent regmap error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stpmic1_regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stw481x-vmmc.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/stw481x-vmmc.c

Purpose: registers the STw4810/STw4811 internal VMMC regulator as a voltage-table regulator and disables external VMMC selection before exposing the internal rail.

Important APIs/types/functions: `stw481x_vmmc_voltages[]` defines eight selector values, including duplicate 1.8 V entries. `stw481x_vmmc_ops` uses table voltage listing and regmap-backed enable, disable, is_enabled, get selector, and set selector helpers. `vmmc_regulator` describes enable and vsel fields in `STW_CONF1`. `stw481x_vmmc_regulator_probe()` obtains parent platform data and registers the regulator.

Control flow: probe receives `struct stw481x` through platform data, clears `STW_CONF2_VMMC_EXT` to disable external VMMC, builds regulator config with parent regmap and OF init data, registers `VMMC`, and logs success. Runtime operations are standard regmap helper callbacks.

State and persistence: no private driver state is stored. Voltage and enable state live in the STw481x registers. Clearing external VMMC is a probe-time hardware side effect.

Dependencies and integration: depends on the STw481x MFD parent, `linux/mfd/stw481x.h`, platform data, parent regmap, OF compatible `st,stw481x-vmmc`, and regulator constraints.

Risks and test signals: the enable mask combines power-down and level-shifter status bits, so polarity and status interaction need hardware validation. `enable_time` is marked FIXME. Test disabling external VMMC, voltage table selector behavior, enable/disable polarity, missing platform data/regmap assumptions, and board constraints for MMC consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stw481x-vmmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sun20i-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/sun20i-regulator.c

Purpose: exposes the Allwinner D1/T113 internal system LDOA and LDOB regulators in the system-control block.

Important APIs/types/functions: `sun20i_d1_system_ldo_list_voltage()` implements custom rounded voltage calculation for a repeating 13.333 mV step. `sun20i_d1_system_ldo_ops` uses this custom listing, ascending map, and regmap selector get/set. `sun20i_d1_system_ldo_descs[]` describes LDOA and LDOB selector masks in `SUN20I_SYS_LDO_CTRL_REG`. `sun20i_regulator_get_regmap()` tries syscon lookup first and falls back to the parent platform regmap for DT backward compatibility.

Control flow: probe obtains match data, gets the parent regmap through syscon or fallback, builds regulator config, and registers each descriptor. Runtime voltage operations only read/write selector fields; there are no enable/disable callbacks.

State and persistence: the driver stores no private state. Selector state is in the system-control register. These LDOs are assumed controlled by voltage selection rather than explicit enable bits.

Dependencies and integration: depends on the parent system-control device, OF compatible `allwinner,sun20i-d1-system-ldos`, regmap/syscon, and regulator child nodes `ldoa` and `ldob` with `ldo-in` supply.

Risks and test signals: custom voltage rounding must match hardware's fractional step encoding. The fallback regmap path is intentionally compatibility-driven and should be kept while old DTs exist. Test selector-to-voltage values around 1.606667 V threshold, map_voltage behavior, both regmap acquisition paths, missing match data, and real DTS consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sun20i-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sy7636a-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/sy7636a-regulator.c

Purpose: implements the SY7636A VCOM regulator child for e-paper power systems, exposing VCOM voltage readback, enable/disable, and power-good status.

Important APIs/types/functions: `struct sy7636a_data` stores parent regmap and GPIOs. `sy7636a_get_vcom_voltage_op()` reads low/high VCOM adjust registers, combines selector bits, and scales to microvolts. `sy7636a_get_status()` reads the `epd-pwr-good` GPIO. `sy7636a_vcom_volt_ops` provides get_voltage, regmap enable/disable/is_enabled, and get_status. `sy7636a_regulator_probe()` obtains resources and registers the `vcom` descriptor.

Control flow: probe gets the parent regmap, adopts the parent OF node, requires `epd-pwr-good`, allocates state, enables optional `vin` supply using `devm_regulator_get_enable_optional()`, obtains optional `enable` and `vcom-en` GPIOs with initial levels, waits if the chip enable GPIO was used, stores state, writes zero power-on delay, and registers the VCOM regulator. Runtime status comes from GPIO; enable state comes from the operation-mode register.

State and persistence: private state holds GPIO/regmap handles. The VCOM voltage is read-only from hardware adjustment registers; this driver does not implement set_voltage. Power sequencing side effects include enabling `vin`, optional enable GPIO, optional VCOM GPIO default low, and clearing power-on delay.

Dependencies and integration: depends on the SY7636A MFD parent, parent regmap, GPIO descriptors, regulator supply `vin`, OF child `vcom` under `regulators`, and e-paper panel consumers.

Risks and test signals: status read assumes `dev_get_drvdata(rdev->dev.parent)` returns the platform data set by this driver. The optional `vcom-en` GPIO is requested but not otherwise toggled. Test VCOM register combination/scaling, mandatory power-good GPIO absence, optional supply and GPIO behavior, regmap write of power-on delay, enable/disable bit, and status error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sy7636a-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sy8106a-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/sy8106a-regulator.c

Purpose: provides I2C regulator support for the Silergy SY8106A buck converter, focused on voltage programming through the VOUT1 selector register.

Important APIs/types/functions: `sy8106a_regmap_config` defines 8-bit registers and values. `sy8106a_ops` supports selector get/set, voltage transition time, and linear voltage listing; enable/disable are intentionally not implemented. `sy8106a_reg` describes 680 mV to 1.95 V in 10 mV steps, selector mask `0x7f`, and a conservative ramp delay. `sy8106a_i2c_probe()` validates DT fixed voltage and ensures `SY8106A_GO_BIT` is set.

Control flow: probe requires `silergy,fixed-microvolt`, validates it against the supported range, initializes regmap, obtains regulator init data, reads the VOUT selector register, and if GO_BIT is clear writes a selector derived from the fixed voltage plus GO_BIT. It then registers the regulator. Runtime voltage changes operate through `SY8106A_REG_VOUT1_SEL`.

State and persistence: no private state is stored. The hardware selector and GO bit carry runtime state. The regulator may behave like a fixed regulator if GO_BIT is not set, so probe forces I2C-controlled mode.

Dependencies and integration: depends on I2C, OF compatible `silergy,sy8106a`, required `silergy,fixed-microvolt`, regmap, and regulator constraints on the device node.

Risks and test signals: missing fixed-voltage property aborts probe. Enable/disable are unavailable, so consumers must treat it as always-on or externally controlled. Test GO_BIT initialization from fixed voltage, out-of-range fixed voltage rejection, voltage selector get/set, ramp timing, and behavior when regulator init data is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sy8106a-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sy8824x.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/sy8824x.c

Purpose: implements I2C regulator support for Silergy SY8824C, SY8824E, SY20276, and SY20278 buck converters, sharing a common driver with per-chip register and voltage configuration.

Important APIs/types/functions: `struct sy8824_config` records voltage, mode, enable register addresses, voltage range, selector count, and regmap config. `struct sy8824_device_info` holds the per-device descriptor and selected config. `sy8824_set_mode()` and `sy8824_get_mode()` map `REGULATOR_MODE_FAST` to the mode bit and normal mode to bit clear. `sy8824_regulator_register()` fills the descriptor dynamically from the chip config. `sy8824_i2c_probe()` selects match data, initializes regmap, and registers the regulator.

Control flow: probe requires OF regulator init data, stores config from `i2c_get_match_data()`, initializes an 8-bit regmap with chip-specific raw-default count/cache config, builds regulator config, and registers a single regulator. Runtime operations use regmap helpers for voltage and enable plus custom mode callbacks.

State and persistence: mutable state is the allocated per-device descriptor/config pointer. Hardware registers store voltage, enable, and mode. No suspend/resume logic exists here.

Dependencies and integration: depends on I2C, OF compatibles `silergy,sy8824c`, `silergy,sy8824e`, `silergy,sy20276`, and `silergy,sy20278`, regulator init data on the device node, and regmap cache.

Risks and test signals: `sy8824_set_mode()` does not check `regmap_update_bits()` return values, so mode write failures are hidden. Dynamic descriptor filling must match each chip's register layout, especially SY20276/SY20278 using register 1 for mode/enable. Test all compatibles, voltage range/count, enable bit, mode read/write failure paths, regmap cache behavior, and missing regulator init data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sy8824x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sy8827n.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/sy8827n.c

Purpose: implements I2C regulator support for the Silergy SY8827N buck regulator, including selectable VSEL register state, optional hardware enable GPIO, voltage programming, enable control, and fast/normal mode.

Important APIs/types/functions: `struct sy8827n_device_info` stores the dynamic descriptor, init data, optional enable GPIO, and selected VSEL register. `sy8827n_set_mode()` and `sy8827n_get_mode()` update/read the mode bit in the chosen VSEL register. `sy8827n_regulator_register()` fills a one-regulator descriptor for 600 mV to 1.3875 V in 12.5 mV steps. `sy8827n_volatile_reg()` marks `PGOOD` volatile.

Control flow: probe requires regulator init data, obtains optional `enable` GPIO as high, selects `SY8827N_VSEL1` when `silergy,vsel-state-high` is present or `VSEL0` otherwise, initializes an 8-bit cached regmap with PGOOD volatile, and registers one regulator. Runtime voltage, enable, and mode operations act on the selected VSEL register.

State and persistence: private state records chosen VSEL register and optional GPIO descriptor. Voltage/enable/mode live in hardware registers. The optional GPIO is set high at probe but not otherwise managed by regulator ops, which use the PMIC enable bit.

Dependencies and integration: depends on I2C, OF compatible `silergy,sy8827n`, optional `enable` GPIO, optional `silergy,vsel-state-high`, regmap, and regulator constraints/init data.

Risks and test signals: `sy8827n_set_mode()` also ignores regmap write errors. GPIO enable and register enable are independent, so board designs must understand which control path matters. Test both VSEL states, optional GPIO absence and probe defer, PGOOD volatility, voltage get/set, enable bit behavior, mode read/write errors, and missing regulator init data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sy8827n.c -->
