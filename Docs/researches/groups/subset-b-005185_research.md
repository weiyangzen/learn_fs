# subset-b-005185 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/renesas-usb-vbus-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/renesas-usb-vbus-regulator.c

Purpose: provides a single fixed 5 V USB VBUS regulator for Renesas RZ/G2L-style USB blocks. It is a tiny platform child driver that exposes the parent MFD/syscon regmap bit as a regulator named `vbus`.

Important APIs/types/functions: `rzg2l_usb_vbus_reg_ops` delegates enable, disable, and status to the regulator regmap helpers. `rzg2l_usb_vbus_rdesc` describes one fixed voltage with `enable_reg = 0`, `enable_mask = BIT(0)`, and inverted enable polarity. `rzg2l_usb_vbus_regulator_probe()` fetches the parent regmap, locates the `regulator-vbus` child node, and registers the regulator with `devm_regulator_register()`.

Control flow: platform probe obtains the parent regmap, takes an OF node reference for the child regulator node, registers the regulator, drops the OF reference, and returns probe status. No runtime callbacks are implemented beyond the generic regulator ops.

State and persistence: all mutable state is in the parent hardware register and regulator core state; this driver keeps no private data. Settings are not persisted by the driver beyond whatever the parent register retains.

Dependencies and integration: depends on a parent device that supplies a regmap and an OF child node named `regulator-vbus`. It integrates with the regulator framework and platform bus, using asynchronous preferred probing.

Risks and test signals: the inverted enable bit is the primary hardware-contract risk. Probe should be tested with missing regmap, missing child node, successful registration, and consumer enable/disable reads against the parent register bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/renesas-usb-vbus-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rk808-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rk808-regulator.c

Purpose: implements the regulator child driver for Rockchip RK80x/RK81x PMIC families. One platform driver supports RK801, RK805, RK806, RK808, RK809, RK816, RK817, and RK818 variants by selecting variant-specific `regulator_desc` tables and common helper ops for bucks, LDOs, boost outputs, and switches.

Important APIs/types/functions: descriptor macros such as `RK8XX_DESC_COM`, `RK806_REGULATOR`, `RK817_DESC`, and switch/boost helpers build large regulator tables. `rk808_regulator_probe()` selects the table based on `struct rk808->variant` from the parent MFD and registers each regulator against the parent regmap. Ops families include `rk801_*`, `rk806_ops_dcdc/nldo/pldo`, `rk808_buck1_2_ops`, `rk816_*`, and `rk817_*`. DVS support is handled by `struct rk808_regulator_data` and `rk808_regulator_dt_parse_pdata()`.

Control flow: probe attaches the child OF node to the parent, fetches the regmap, allocates driver data, optionally parses RK808 DVS GPIOs and polarity bits, chooses descriptors, then loops through `devm_regulator_register()`. Runtime control is largely regmap-backed: enable bits, voltage selectors, suspend selectors, ramp tables, and mode bits are written through regulator helpers or small variant adapters. RK806 has custom ramp handling because the DCDC ramp selector MSB lives in separate registers. RK808 DCDC1/2 can switch between ON and DVS voltage registers by toggling GPIOs; without GPIOs, voltage increases are stepped to reduce overshoot.

State and persistence: persistent hardware state lives in PMIC registers. The only driver-owned state is the optional DVS GPIO array. Suspend voltage and enable/disable settings are programmed into PMIC sleep registers and survive until overwritten or reset.

Dependencies and integration: depends on `linux/mfd/rk808.h` definitions, the parent MFD regmap, OF regulator nodes, optional `dvs` GPIOs, and the regulator framework. Probe is forced synchronous, which likely reflects consumers needing these rails early.

Risks and test signals: table/register drift across variants is the largest risk. Sleep-enable polarity differs by family, write-mask enable registers need correct `enable_val`/`disable_val`, and DVS GPIO polarity changes both register programming and selected voltage source. Test signals include compile coverage for all variants, DT matching of every regulator node, voltage selector boundary tests, suspend voltage/mode writes, RK806 ramp MSB writes, RK808 DVS toggling, and missing/invalid variant handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rk808-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rn5t618-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rn5t618-regulator.c

Purpose: registers voltage regulators for Ricoh RN5T567, RN5T618, and RC5T619 PMIC variants. The driver maps each variant to DCDC, LDO, and RTC LDO descriptor arrays with linear voltage selectors.

Important APIs/types/functions: `rn5t618_reg_ops` uses regmap helpers for enable, disable, status, voltage selection, and linear voltage listing. The `REG()` macro creates `regulator_desc` entries from RN5T618 register constants. `rn5t618_regulator_probe()` reads `struct rn5t618->variant`, chooses the descriptor table, and registers each regulator.

Control flow: platform probe obtains parent MFD driver data, switches on variant, fills `regulator_config` with the parent device and regmap, and loops through the selected descriptor table. Registration failure aborts probe at the first failed rail.

State and persistence: no private runtime state is allocated. Voltage selections and enables are held in PMIC registers via the parent regmap. Device-tree integration comes from each descriptor's `of_match` under the `regulators` node.

Dependencies and integration: integrates with the RN5T618 MFD core, regmap, OF regulator matching, and regulator framework. The platform alias is `rn5t618-regulator`, so it is normally instantiated by the MFD cell.

Risks and test signals: variant table accuracy is the main concern because rail count and voltage minima differ, especially `LDORTC1`. Tests should cover all three variants, missing/unknown variants returning `-EINVAL`, OF node matching, voltage selector min/max boundaries, and failure cleanup on partial registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rn5t618-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rohm-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rohm-regulator.c

Purpose: supplies shared helper routines for ROHM PMIC regulator drivers rather than registering regulators itself. It programs device-tree-defined DVS voltage levels and provides a restricted voltage setter for rails that must be disabled before voltage changes.

Important APIs/types/functions: `rohm_regulator_set_dvs_levels()` iterates a `struct rohm_dvs_config` level map and applies properties such as `rohm,dvs-run-voltage`, `rohm,dvs-idle-voltage`, and suspend/deep-sleep variants. `set_dvs_level()` resolves a requested microvolt value against the descriptor's linear or linear-range voltage table, writes the selector, and optionally writes an enable mask. `rohm_regulator_set_voltage_sel_restricted()` returns `-EBUSY` when the target rail is enabled.

Control flow: callers pass a DVS config, OF node, descriptor, and regmap. For each enabled DVS level, the helper reads the DT property, treats zero as disable when an on-mask exists, maps the exact voltage to a selector, writes the selector register, then enables that DVS state if needed.

State and persistence: this file owns no state. It mutates PMIC registers supplied by caller drivers. DVS settings persist as PMIC register state until reset or reprogramming.

Dependencies and integration: exported symbols are consumed by ROHM PMIC regulator drivers sharing `include/linux/mfd/rohm-generic.h` DVS conventions. It relies on regulator descriptor voltage-list helpers and regmap.

Risks and test signals: exact-voltage matching rejects unsupported but nearby voltages, and pickable range selectors are explicitly unsupported. A property value of zero has special disable semantics. Tests should exercise absent properties, invalid properties, supported and unsupported voltages, enable-only DVS levels with no voltage mask, and enabled-rail restricted voltage writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rohm-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rpi-panel-attiny-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rpi-panel-attiny-regulator.c

Purpose: controls the Raspberry Pi 7-inch touchscreen panel's Atmel microcontroller, exposing panel power as a regulator, brightness as a backlight, and two reset lines as GPIOs.

Important APIs/types/functions: `struct attiny_lcd` stores the regmap, serialized port state cache, GPIO chip, and mutex. Regulator ops are `attiny_lcd_power_enable()`, `attiny_lcd_power_disable()`, and `attiny_lcd_power_is_enabled()`. Backlight updates use `attiny_update_status()`. GPIO output is handled by `attiny_gpio_set()`, including a bridge programming sequence after bridge reset release. `attiny_i2c_probe()` initializes all subsystems.

Control flow: probe allocates state, initializes a custom regmap, validates firmware ID `0xde` or `0xc3`, powers down PWM/power, registers the regulator, registers a raw backlight, and registers a sleeping GPIO chip. Enabling the regulator writes port registers in a timed sequence: resets held, orientation configured, panel power on, resets released after delays. Disable reverses PWM, ports, and resets.

State and persistence: `port_states[]` caches output register state because GPIO operations compose bit masks. `gpio_states[]` is allocated but not used for reads. Hardware state is volatile microcontroller register state; driver does not persist settings across unload or reset.

Dependencies and integration: integrates I2C, regmap, regulator, backlight, gpiochip, OF matching, and panel/bridge consumers. The regulator constraints permit status changes only.

Risks and test signals: timing and cached port state are critical. `attiny_lcd_power_is_enabled()` reads live hardware while other operations use cached state, and several regmap writes ignore return values in sequencing paths. Test signals include probe ID rejection, repeated I2C transient failures, regulator enable/disable sequencing, GPIO reset behavior, bridge post-reset programming, backlight writes, and concurrent backlight/GPIO/regulator access under the mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rpi-panel-attiny-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rpi-panel-v2-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rpi-panel-v2-regulator.c

Purpose: supports the Raspberry Pi 7-inch V2 touchscreen microcontroller as an I2C-backed GPIO and PWM provider. Despite the filename, it does not register a regulator; power/reset bits are exposed through `gpio-regmap` and backlight control through a PWM chip.

Important APIs/types/functions: `rpi_panel_v2_pwm_apply()` maps PWM enable and relative duty cycle to `REG_PWM` bits. `rpi_panel_v2_i2c_probe()` allocates a one-channel `pwm_chip`, initializes the I2C regmap, clears `REG_POWERON`, registers a two-line gpio-regmap, stores regmap client data, and adds the PWM chip. `rpi_panel_v2_i2c_shutdown()` clears PWM and power/reset state.

Control flow: PWM apply rejects non-normal polarity, writes zero when disabled, or writes `PWM_BL_ENABLE | duty` when enabled. Probe creates regmap-backed GPIOs for LCD and CTP reset bits, then exposes PWM after GPIO registration succeeds. Shutdown always turns backlight and power/reset bits off.

State and persistence: no private state beyond regmap pointer storage in the PWM chip and I2C client data. Hardware register state is volatile and reset on shutdown.

Dependencies and integration: depends on I2C, regmap, `gpio-regmap`, PWM framework, and OF compatible `raspberrypi,touchscreen-panel-regulator-v2`. Display and touch drivers consume GPIO and PWM resources.

Risks and test signals: because GPIO and PWM share one regmap, probe order and shutdown behavior matter. There is no firmware ID validation despite a defined `REG_ID`. Tests should cover PWM duty scaling, polarity rejection, GPIO set/clear through gpio-regmap, shutdown clearing, and missing regmap/GPIO registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rpi-panel-v2-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt4801-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rt4801-regulator.c

Purpose: implements the Richtek RT4801 display bias regulator with positive and negative DSV outputs. Each output has a voltage selector and optional dedicated enable GPIO.

Important APIs/types/functions: `struct rt4801_priv` tracks enable GPIOs, a software enable bitmask, and cached voltage selectors. `rt4801_of_parse_cb()` lets child regulator nodes override or provide per-rail enable GPIOs. Custom ops cache voltage while disabled and write voltage on enable.

Control flow: I2C probe assumes outputs were enabled by firmware, initializes regmap, obtains optional indexed `enable` GPIOs, reads current VOP/VON selector values, and registers DSVP and DSVN descriptors. `set_voltage_sel()` writes hardware only when the rail is marked enabled; otherwise it updates the cached selector. `enable()` asserts GPIO, writes the cached selector to the rail register, and marks enabled. `disable()` deasserts GPIO and clears the software bit.

State and persistence: enable state is software-only and initialized to both rails enabled. Voltage selection is cached per rail so disabled rails can accept regulator-core voltage changes before the next enable. Hardware does not provide an enable status register in this implementation.

Dependencies and integration: depends on I2C, regmap, GPIO descriptors, regulator OF matching for `DSVP` and `DSVN`, and optional per-regulator `enable-gpios`.

Risks and test signals: software enable state can diverge from hardware if GPIOs are absent or external logic changes power. `of_parse_cb()` silently ignores failed child GPIO lookups. Tests should check bootloader-enabled assumption, voltage changes while disabled, GPIO present/absent cases, duplicate enable GPIO properties, and regmap read/write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt4801-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt4803.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rt4803.c

Purpose: provides an I2C regulator driver for the Richtek RT4803 buck/boost regulator, including voltage selection, operating mode, suspend voltage, and error flag reporting.

Important APIs/types/functions: `rt4803_set_mode()` and `rt4803_get_mode()` map regulator normal/fast modes to AUTO/FPWM bits. `rt4803_get_error_flags()` reads fault, thermal, and power-good status. `rt4803_set_suspend_voltage()` writes the inactive VSEL register. Probe dynamically allocates and fills a `regulator_desc` based on `richtek,vsel-active-high`.

Control flow: probe initializes regmap, sets input current limit to maximum, chooses active VSEL register from firmware property, fills descriptor voltage range and `of_map_mode`, obtains init data, and registers one regulator. Runtime voltage operations use regmap helper selectors; suspend voltage writes the opposite VSEL register so hardware can switch levels externally.

State and persistence: no private runtime data is kept after descriptor registration. The hardware holds active and suspend VSEL registers, mode, current limit, and status flags.

Dependencies and integration: integrates I2C, regmap, regulator core, `of_get_regulator_init_data()`, and firmware property APIs. The OF binding controls active VSEL polarity and mode mapping.

Risks and test signals: current limit is unconditionally configured to max, which should match board expectations. `set_suspend_voltage()` computes a selector without checking exact range through regulator helpers. Test signals include VSEL polarity selection, mode mapping, invalid mode rejection, status-to-error mapping, suspend voltage boundaries, and ILIM write failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt4803.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt4831-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rt4831-regulator.c

Purpose: registers the Richtek RT4831 display supply regulators: DSVLCM, DSVP, and DSVN. It is a platform child using a parent regmap from the RT4831 MFD.

Important APIs/types/functions: `rt4831_get_error_flags()` maps OTP, LCM overvoltage, and positive/negative short-circuit flags to regulator errors. `rt4831_dsvlcm_ops` supports voltage selection and bypass mode. `rt4831_dsvpn_ops` supports voltage selection, enable/disable, active discharge, and error flags. Descriptor tables define voltage ranges, mode bits, enable bits, and discharge bits.

Control flow: probe fetches the parent regmap, programs DSV mode to normal by default, then registers the three descriptors. DSVLCM bypass toggles the DSV mode field between normal and bypass; DSVP/DSVN use enable and discharge bits in `RT4831_REG_DSVEN`.

State and persistence: no private state. All state is represented by PMIC registers owned by the parent regmap. Error flags are read on demand from the flags register.

Dependencies and integration: depends on the RT4831 parent device creating a `rt4831-regulator` platform cell, a parent regmap, and OF regulator child nodes under `regulators`.

Risks and test signals: probe globally rewrites DSV mode to normal, which may override boot firmware state. Error mapping is rail-specific, so IDs must remain aligned with descriptor order. Tests should cover parent regmap absence, DSV mode initialization, bypass operations, active discharge bits, voltage range boundaries, and per-rail error flag mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt4831-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt5033-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rt5033-regulator.c

Purpose: registers the Richtek RT5033 PMIC buck, LDO, and safe LDO regulators from an MFD child platform device.

Important APIs/types/functions: `rt5033_buck_ranges` and `rt5033_ldo_ranges` describe selector ranges with a fixed 3.0 V plateau for high selectors. `rt5033_buck_ops` supports enable, voltage selection, and linear-range listing. `rt5033_safe_ldo_ops` supports only fixed voltage listing and enable state. `rt5033_regulator_probe()` loops over the descriptor table.

Control flow: probe obtains `struct rt5033_dev` from the parent, fills `regulator_config` with parent device and regmap, and registers all three descriptors. Any registration failure aborts probe with an error log.

State and persistence: the driver owns no private state. PMIC registers hold enable and selector state. The safe LDO is modeled as a one-voltage regulator.

Dependencies and integration: depends on RT5033 MFD headers and private register definitions, the platform ID `rt5033-regulator`, OF child names under `regulators`, and the regulator framework.

Risks and test signals: descriptor constants must match the MFD register map and enum IDs. SAFE_LDO has no voltage selector, so consumers must treat it as fixed. Tests should cover all rail registrations, selector-to-voltage mapping at range boundaries, enable bits in `RT5033_REG_CTRL`, and failures from parent regmap access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt5033-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt5120-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rt5120-regulator.c

Purpose: registers six regulators for the Richtek RT5120 PMIC child: four bucks, one LDO, and one external enable rail. Buck1 is adjustable through I2C, while other rails are modeled as fixed-voltage rails with enable, mode, discharge, suspend, and error support as applicable.

Important APIs/types/functions: `struct rt5120_priv` contains the parent regmap and dynamically filled descriptors. `rt5120_fillin_regulator_desc()` builds descriptors by rail ID. `rt5120_parse_regulator_dt_data()` matches DT children and validates fixed-voltage constraints. `rt5120_device_property_init()` configures under/overvoltage hiccup behavior. `rt5120_regulator_get_error_flags()` reads PG/UV/OV and hot-die status.

Control flow: probe obtains the parent regmap, applies board protection properties, parses the `regulators` node, fills fixed voltages from DT for non-buck1 rails, then registers all six regulators. Runtime mode operations update `RT5120_REG_MODECTL`; suspend enable/disable uses `RT5120_REG_SLPCTL`; buck1 suspend voltage writes `RT5120_REG_CH1SLPVID`.

State and persistence: descriptor fields are driver-owned and populated at probe. Hardware registers persist enable, mode, discharge, protection, sleep, and fault state. Non-buck1 fixed voltages are derived from DT constraints rather than read from hardware.

Dependencies and integration: platform child of an MFD with a parent regmap and regulator children named `buck1` through `exten`. Uses OF regulator matching and Richtek-specific DT booleans.

Risks and test signals: `regmap_raw_read(..., &stat, 3)` reads three bytes into an `unsigned int`, making endian/layout assumptions for bit macros spanning bits 1, 9, and 16. Fixed rails reject unequal min/max constraints. Tests should cover DT absence, fixed-voltage validation, hiccup booleans, mode mapping, suspend bits, buck1 voltage limits, and error flag mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt5120-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt5133-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rt5133-regulator.c

Purpose: supports Richtek RT5133/RT5133A multi-output LDO PMICs with a base rail, eight LDOs, GPIO outputs, CRC-protected I2C regmap access, and interrupt notifications.

Important APIs/types/functions: `struct rt5133_priv` stores regmap, enable GPIO, regulator devices, GPIO chip, selected chip data, GPIO output cache, and CRC table. `rt5133_regmap_hw_read()` and `rt5133_regmap_hw_write()` implement custom CRC8 SMBus transfers. `rt5133_validate_vendor_info()` selects RT5133 vs RT5133A descriptor tables. `rt5133_intr_handler()` reports LDO over-current and power-good failures through regulator notifiers.

Control flow: probe populates CRC tables, optionally asserts hardware enable, initializes the CRC regmap bus, validates vendor info, performs a software reset, registers base plus eight LDO regulators from the selected descriptor table, applies shutdown policy DT booleans, registers a three-line GPIO chip, clears and unmasks interrupts, and requests a threaded IRQ. Runtime regulator ops are mostly regmap-backed voltage-table and enable operations.

State and persistence: descriptor choice and GPIO output flags are driver state. Hardware registers hold LDO enables, voltage selections, active discharge, base enable, shutdown policy, GPIO control, and interrupt latches. Reset during probe reinitializes device register state.

Dependencies and integration: depends on I2C/SMBus block transfers, CRC8, regmap custom bus, GPIO framework, regulator framework, optional enable GPIO, IRQ line, and OF regulator children.

Risks and test signals: CRC framing and one-byte raw access limits are central risks. The probe logs enable GPIO acquisition errors but continues even for non-deferred failures. Interrupt handling reads three bytes into a `u32`, requiring byte order expectations. Tests should cover CRC mismatch, vendor detection, reset, descriptor-table differences for LDO8, GPIO set/get caching, DT shutdown booleans, IRQ clear/unmask, and notifier delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt5133-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt5190a-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rt5190a-regulator.c

Purpose: registers five Richtek RT5190A rails: fixed buck1, adjustable buck2/buck3, fixed buck4, and fixed LDO, with interrupt reporting for voltage and thermal events.

Important APIs/types/functions: `struct rt5190a_priv` holds descriptors and registered regulator devices. `rt5190a_fillin_regulator_desc()` builds per-rail descriptors. `rt5190a_parse_regulator_dt_data()` matches the `regulators` node and validates fixed-rail constraints. `rt5190a_device_initialize()` applies a register patch and optional mute property. `rt5190a_irq_handler()` maps OV/UV/OT event bits to regulator notifier calls.

Control flow: probe initializes regmap, checks the manufacturer/device register, applies initialization patch, parses regulator DT data and protection mode, registers all five regulators, then optionally requests IRQ. Runtime fixed-buck mode changes update `RT5190A_REG_DCDCCNTL`; adjustable buck voltage selection uses regmap helpers.

State and persistence: descriptors are constructed at probe, including fixed voltages from DT constraints. Hardware stores enable, discharge, mode, protection, mute, fault, and voltage selector state. Interrupt latches are write-cleared by the handler.

Dependencies and integration: depends on I2C regmap, DT binding mode constants from `dt-bindings/regulator/richtek,rt5190a-regulator.h`, OF regulator matching, and optional IRQ.

Risks and test signals: `rt5190a_device_check()` expects a zero 16-bit manufacture value, a tight hardware assumption. Event handling uses `REGULATOR_ERROR_*` constants in notifier calls for some cases rather than `REGULATOR_EVENT_*`, which deserves review. Tests should cover fixed-rail min/max validation, latchup property polarity, register patch application, mute property, IRQ OV/UV/OT delivery, and absent IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt5190a-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt5739.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rt5739.c

Purpose: provides a single buck regulator driver for Richtek RT5733/RT5739. It supports dual VSEL registers for active/suspend levels, mode control, active discharge, ramp delay, and optional hardware enable GPIO.

Important APIs/types/functions: `rt5739_init_regulator_desc()` fills a dynamic descriptor based on `richtek,vsel-active-high` and chip die ID. `rt5739_set_mode()`, `rt5739_get_mode()`, and `rt5739_set_suspend_mode()` select AUTO/FPWM bits for active or inactive VSEL. `rt5739_set_suspend_voltage()`, `_enable()`, and `_disable()` operate on the inactive VSEL path.

Control flow: probe optionally asserts an enable GPIO and waits for I2C readiness, initializes a cached regmap, reads and validates VID/DID, determines VSEL polarity, configures descriptor voltage range for RT5733 or RT5739, obtains init data, and registers one regulator. Runtime ops write the current VSEL register for active operations and the opposite register for suspend configuration.

State and persistence: no private state after descriptor registration. Regmap cache is enabled with the monitor register volatile. Hardware stores VSEL, enable, mode, discharge, ramp, and monitor state.

Dependencies and integration: depends on I2C, optional GPIO, regmap cache, OF properties, and regulator framework. The compatible table covers `richtek,rt5733` and `richtek,rt5739`.

Risks and test signals: VID validation requires `(VID & mask) == 0`, and DID controls voltage table selection. Suspend operations invert active VSEL selection, so property polarity errors program the wrong register. Tests should cover both compatibles/die IDs, GPIO absent/present timing, VSEL polarity, voltage boundaries, mode mapping, suspend enable/mode, and regcache behavior for volatile monitor register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt5739.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt5759-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rt5759-regulator.c

Purpose: implements the Richtek RT5759/RT5759A single buck regulator with voltage selection, enable, active discharge, mode, ramp delay, error flags, configurable OCP/OTP thresholds, and optional RT5759A watchdog input.

Important APIs/types/functions: `struct rt5759_priv` stores chip type, regmap, and descriptor. `rt5759_regulator_register()` fills descriptor fields and adjusts `uV_step` for RT5759A. `rt5759_manufacturer_check()` verifies vendor ID. `rt5759_set_ocp()` and `rt5759_set_otp()` map regulator protection requests to register levels.

Control flow: probe allocates state, obtains chip type from OF match data, initializes regmap with chip-type-aware accessible registers, checks manufacturer ID, applies the RT5759A watchdog property if applicable, then registers the buck regulator. Runtime mode and protection writes update DCDC control/status/set registers; status reads report overtemperature and undervoltage errors.

State and persistence: chip type and descriptor are driver state. Hardware registers store voltage, enable, discharge, ramp, mode, protection thresholds, watchdog enable, and status.

Dependencies and integration: depends on I2C, OF match data, regmap readable/writeable callbacks, regulator protection APIs, and OF regulator init data.

Risks and test signals: `rt5759_set_mode()` writes `RT5759_REG_STATUS` while `get_mode()` reads `RT5759_REG_DCDCCTRL`, a potential register mismatch to verify against datasheet. Protection setters ignore non-protection severities by returning success. Tests should cover both chip types, vendor mismatch, watchdog property access only on RT5759A, voltage step differences, ramp table, mode set/get consistency, and OCP/OTP threshold rounding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt5759-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt6160-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rt6160-regulator.c

Purpose: provides a Richtek RT6160/RT6166 buck-boost regulator driver with optional hardware enable GPIO, cached regmap power-down handling, voltage selection, mode, ramp delay, suspend voltage, and error flags.

Important APIs/types/functions: `struct rt6160_priv` stores descriptor, enable GPIO, regmap, software enable state, and device ID. `rt6160_enable()`/`disable()` control GPIO and regcache cache-only state. `rt6160_get_error_flags()` maps status bits for hot-die, under-voltage, over-current, thermal shutdown, and power-good failure. `rt6160_of_map_mode()` maps DT modes.

Control flow: probe reads VSEL polarity property, asserts optional enable GPIO, initializes regmap, validates vendor/device ID, fills descriptor min voltage based on RT6160 vs RT6166, selects active VSEL register, and registers the regulator. Disabling with GPIO marks regcache dirty/cache-only before powering hardware off; enabling reactivates hardware, exits cache-only mode, and synchronizes registers.

State and persistence: `enable_state` is software-owned and initialized true. Regmap cache preserves configuration across GPIO-controlled hardware disable. Hardware stores voltage, mode, ramp, and status while powered.

Dependencies and integration: depends on I2C, optional `enable` GPIO, property API, regcache, regulator framework, and OF regulator init data.

Risks and test signals: if no enable GPIO exists, `disable()` returns `-EINVAL` while `enable()` is a no-op, so consumers cannot software-disable. `get_mode()` returns raw I/O errors as regulator mode values. Tests should cover GPIO absent/present paths, regcache sync failure, vendor IDs, RT6166 min-voltage selection, VSEL active-low property, suspend voltage on inactive register, and error flag mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt6160-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt6190-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rt6190-regulator.c

Purpose: supports the Richtek RT6190 high-voltage output regulator with large voltage/current ranges, active discharge, mode selection, runtime PM, optional hardware enable GPIO, ADC-related initialization, and IRQ-based error notification.

Important APIs/types/functions: `struct rt6190_data` stores regmap, optional enable GPIO, runtime PM device, and cached alert events. Raw little-endian helpers implement 16-bit voltage/current selector reads and writes. `rt6190_out_enable()` preserves output configuration across enable because the IC restores defaults. `rt6190_irq_handler()` caches write-cleared alert bits and emits regulator notifications.

Control flow: probe asserts optional enable GPIO, initializes a cached regmap, validates Richtek VID, writes initialization registers for ADC, ratio, masks, OCP, and bus-current ADC, enables runtime PM, registers the regulator, and requests IRQ if present. Enable gets runtime PM, snapshots VOUT/current registers, enables PWM, restores snapshot, and enables charge pump. Disable turns off charge pump/output, clears cached alert state, and releases runtime PM. Runtime suspend/resume powers hardware by GPIO and syncs regcache.

State and persistence: cached alert events keep fault history after IRQ write-clear until output disable. Regmap cache preserves configuration during GPIO-powered runtime suspend. Hardware stores selectors, current limit, mode, discharge, ADC, and status.

Dependencies and integration: depends on I2C, optional GPIO, runtime PM, regmap cache, regulator current-limit APIs, optional IRQ, and OF regulator init data.

Risks and test signals: enable error paths after `pm_runtime_get_sync()` do not visibly unwind with `pm_runtime_put()`. Voltage/current selectors use little-endian raw transfers, so bus ordering is important. Tests should cover enable restore semantics, current limit rounding, runtime suspend/resume, IRQ caching and notifier calls, VID mismatch, and optional IRQ/GPIO absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt6190-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt6245-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rt6245-regulator.c

Purpose: implements the Richtek RT6245 single buck regulator, whose configuration is written through virtual regmap registers encoded as one-byte SMBus command codes with parity checksum.

Important APIs/types/functions: `struct rt6245_priv` tracks optional enable GPIO and software enable state. `rt6245_reg_write()` maps virtual register plus value to a command byte using `func_base[]` and bit-count checksum. `rt6245_init_device_properties()` applies optional properties for current limit, thermal level, power-good delay, and switching frequency. Regulator ops support voltage selection, ramp delay, and GPIO enable.

Control flow: probe initializes software state as enabled, obtains optional enable GPIO, waits for soft-start, creates a regmap with custom write-only encoding and defaults, applies DT properties, and registers the regulator. Disable enters cache-only mode and powers the chip down via GPIO; enable powers it up, exits cache-only, syncs cached virtual registers, and marks enabled.

State and persistence: enable state is software-only. Regmap cache holds virtual register values while hardware is off. Hardware stores only the encoded settings accepted over SMBus.

Dependencies and integration: depends on I2C SMBus byte write, optional GPIO, regmap custom `reg_write`, regulator OF init data, and Richtek DT properties.

Risks and test signals: no readable registers are modeled, so cache correctness is vital. If no enable GPIO exists, disable returns `-EINVAL`. Virtual register index bounds rely on regmap `max_register`; `func_base` includes a final zero for VOUT. Tests should cover checksum generation, property application, regcache sync after disable/enable, ramp table, voltage selector bounds, and GPIO absent behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt6245-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt8092.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rt8092.c

Purpose: provides a single Richtek RT8092 regulator with dual VOUT banks, VSEL-active-high selection, mode and suspend controls, and error reporting.

Important APIs/types/functions: `rt8092_get_vbank_index()` reads the voltage bank multiplier for active high/low VSEL. `rt8092_set_operating_mode()` and `rt8092_get_operating_mode()` update FPWM bits for the active selector. Suspend helpers write the opposite VSEL register for voltage, enable, disable, and mode. Probe dynamically calculates `min_uV` and `uV_step` from VBank.

Control flow: probe obtains optional enable GPIO, initializes regmap, reads `richtek,vsel-active-high`, fetches the relevant VBank index, computes linear voltage parameters, fills descriptor fields for the active VOUT register, and registers the regulator. Runtime operations use regmap-backed selector and enable helpers; suspend operations target the inactive VOUT register.

State and persistence: the driver stores only the dynamically allocated descriptor. Hardware registers retain active and suspend VOUT selectors, enable bits, mode bits, event flags, and VBank configuration.

Dependencies and integration: depends on I2C, optional enable GPIO, regmap, bitfield helpers, regulator OF init data, and firmware properties.

Risks and test signals: the optional enable GPIO is requested but not used after probe, so hardware enable lifecycle may be board-fixed. VBank scaling shifts requested suspend voltage before selector validation, making rounding important. Tests should cover both VSEL polarities, VBank indices, voltage min/step calculations, suspend register inversion, mode mapping, error flag reads, and enable-time behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rt8092.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rtmv20-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rtmv20-regulator.c

Purpose: supports the Richtek RTMV20 laser switch/current regulator. It exposes one current regulator named `rtmv20,lsw`, configures many timing/current/polarity properties, handles hardware enable GPIO power-down, and reports laser-driver fault interrupts.

Important APIs/types/functions: `struct rtmv20_priv` stores device, regmap, enable GPIO, and regulator device. `rtmv20_lsw_set_current_limit()` maps current limits to selector values. `rtmv20_properties_init()` clamps and writes DT properties, including multi-byte big-endian fields. `rtmv20_irq_handler()` maps OTP/OCP/fail events to regulator notifiers.

Control flow: probe asserts required enable GPIO, waits for I2C readiness, initializes cached regmap, validates vendor ID, applies property defaults/overrides, then deliberately enters cache-only mode and disables hardware for low consumption. It registers the current regulator, unmasks events, and requests a threaded IRQ. Enabling reasserts GPIO, syncs cached registers, then sets regulator enable bits; disabling clears enable bits, cache-only marks dirty, and powers hardware off.

State and persistence: regcache preserves configuration while the chip is off. Hardware registers store timing, current, polarity, low-battery, FSIN/ES settings, masks, and event latches. No persistent state is written outside the chip.

Dependencies and integration: depends on I2C, required enable GPIO, regmap cache, regulator current APIs, IRQ, PM sleep hooks, and many Richtek DT properties.

Risks and test signals: probe disables hardware before writing `LDMASK`, then writes through a cache-only regmap; this should be checked against regmap semantics and intended unmask timing. IRQ request assumes a valid IRQ. Tests should cover property clamping and 16-bit writes, current limit rounding, enable/disable regcache sync, vendor mismatch, IRQ notifier mapping, and suspend/resume IRQ wake handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rtmv20-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rtq2134-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rtq2134-regulator.c

Purpose: registers three Richtek RTQ2134 buck regulators with voltage ranges, enable, active discharge, ramp delay, normal/suspend mode, suspend voltage/enable, and error flags.

Important APIs/types/functions: `struct rtq2134_regulator_desc` extends `regulator_desc` with mode, suspend, and DVS control register metadata. `RTQ2134_BUCK_DESC()` creates the three descriptors. `rtq2134_buck_of_parse_cb()` configures DVS control mode and UV hiccup/shutdown behavior from DT properties. `rtq2134_buck_get_error_flags()` reads chip and per-buck fault records.

Control flow: probe initializes the I2C regmap and registers the three static descriptors. During regulator registration, each descriptor's OF parse callback writes `richtek,use-vsel-dvs` and `richtek,uv-shutdown` policy to hardware. Runtime ops use the extended descriptor fields to update active mode, suspend mode, suspend enable, and suspend voltage registers.

State and persistence: no private state is allocated beyond the regmap. The static descriptors encode all per-rail register addresses. Hardware fault records and policy bits persist until cleared or reset according to chip behavior.

Dependencies and integration: depends on I2C, regmap readable/writeable callbacks, OF regulator child names `buck1` through `buck3`, and regulator linear-range APIs.

Risks and test signals: the custom descriptor is cast from `rdev->desc`, so it relies on `struct regulator_desc` being the first field. `rtq2134_is_accissible_reg` is misspelled but functionally referenced. Tests should cover each buck's register addresses, OF parse side effects, mode/suspend mode mapping, UV policy polarity, ramp table entries including zeros, and fault flag mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rtq2134-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rtq2208-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rtq2208-regulator.c

Purpose: supports the Richtek RTQ2208 PMIC by dynamically discovering which buck phases and LDO configurations are present, registering only the active regulators, and wiring IRQ notifications for buck UV/OV and hot-die events.

Important APIs/types/functions: `struct rtq2208_regulator_desc` extends descriptors with MTP, mode, and suspend fields. `rtq2208_regulator_check()` enters hidden pages, reads buck phase and LDO configuration, computes used regulators, fixed LDO voltages, and IRQ masks. `rtq2208_init_regulator_desc()` fills each descriptor according to regulator index and MTP selection. `rtq2208_irq_handler()` reads, clears, and reports fault records.

Control flow: probe allocates an `rtq2208_rdev_map`, initializes regmap, discovers active rails through hidden-page reads, parses the `richtek,mtp-sel-high` property, allocates descriptors for active rails, registers them, initializes IRQ masks, and requests a threaded IRQ. Buck ops support voltage, mode, ramp, active discharge, and suspend mode/enable. LDO ops are fixed or two-step adjustable depending on hidden configuration.

State and persistence: the rdev map persists regulator pointers for IRQ dispatch. Dynamic descriptors persist for the device lifetime. Hardware hidden configuration determines rail topology; operational state remains in PMIC registers.

Dependencies and integration: depends on I2C, regmap, OF regulator matching, machine constraints for fixed LDO voltage, IRQ, and bitfield helpers. There is no static full descriptor table because topology is hardware-configured.

Risks and test signals: hidden-page entry/exit must be correct or later register access could be affected. IRQ mask arrays are mutated according to active rails, so index mapping is critical. `cfg.regmap` is not explicitly assigned before registration, relying on regulator core lookup behavior may be risky. Tests should cover all buck phase encodings, fixed/adjustable LDO combinations, MTP high/low, ramp delay calculation, IRQ clear/unmask, and absent IRQ/hidden-page failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rtq2208-regulator.c -->
