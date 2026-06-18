# subset-b-005180 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max20086-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max20086-regulator.c

Purpose: implements the MAX20086/MAX20087/MAX20088/MAX20089 camera power protector regulator driver. It exposes two or four switch-style voltage outputs as regulator framework devices and uses one optional global enable GPIO for chip power/shutdown.

Important APIs/types/functions: `struct max20086_chip_info` selects device ID and output count; `struct max20086` owns the regmap, enable GPIO, chip match data, and per-output regulator metadata. `max20086_parse_regulators_dt()` matches child regulators under `regulators`; `max20086_detect()` verifies `MAX20086_REG_ID`; `max20086_regulators_register()` calls `devm_regulator_register()` for each output. Regulator ops are generic regmap enable/disable/is_enabled against `MAX20086_REG_CONFIG`.

Control flow: I2C probe allocates state, initializes an 8-bit regmap, parses DT, verifies the chip ID, masks all interrupts because IRQ support is absent, requests the optional `enable` GPIO high if any output is boot-on/always-on, then registers each output descriptor.

State and persistence: runtime state is devm-managed and non-persistent. Regulator enable state lives in the chip config register; the global enable GPIO state is chosen from DT constraints to avoid dropping boot-critical rails.

Dependencies and integration: depends on I2C, regmap, GPIO descriptors, OF regulator matching, and regulator core. Compatible strings and I2C IDs map to fixed `chip_info` records.

Risks and test signals: no IRQ handling means faults are masked and invisible to Linux. DT must provide a `regulators` subnode with valid output names. Test signals include chip-ID mismatch, 2-output versus 4-output variants, boot-on GPIO preservation, interrupt mask write failure, and all output enable bits toggling only their own mask.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max20086-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max20411-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max20411-regulator.c

Purpose: provides a single regulator for the MAX20411 high-efficiency step-down converter, with linear voltage selection, slew metadata, enable-time estimation, and an optional enable GPIO.

Important APIs/types/functions: `struct max20411` stores the local descriptor, regmap, and registered `regulator_dev`. `max20411_enable_time()` reads the programmed voltage selector and slew-rate register and computes microseconds from `max20411_slew_rates`. `max20411_ops` delegates voltage get/set/list to regmap helpers and exposes `.enable_time`.

Control flow: I2C probe allocates state, creates an 8-bit regmap, copies the static descriptor, obtains regulator init data from the device node, acquires an `"enable"` GPIO with `GPIOD_ASIS`, and registers the regulator.

State and persistence: the driver keeps only devm-managed probe state. Voltage and slew configuration persist in chip registers while powered. Enable GPIO lifetime is handed to the regulator core through `config.ena_gpiod`.

Dependencies and integration: uses I2C, regmap, GPIO descriptors, OF regulator init data, and regulator core. It binds through `maxim,max20411` and the `max20411` I2C ID.

Risks and test signals: probe fails if no regulator init data is parsed, which makes DT completeness mandatory. `gpiod_get()` is not devm-managed in the driver but is passed to the regulator core. Test voltage selector bounds, slew-rate-derived enable times, missing/invalid enable GPIO, and DT constraints mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max20411-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max5970-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max5970-regulator.c

Purpose: implements regulator, hwmon, and fault-notifier support for MAX5970/MAX5978 hot-swap switch controllers. Each switch is a voltage regulator with voltage/current ADC telemetry and configurable UV/OV/OCP protections.

Important APIs/types/functions: `struct max5970_regulator` carries per-switch ADC ranges, shunt resistance, cached current limit, and shared regmap. `max5970_read()` and `max5970_is_visible()` back hwmon voltage/current inputs. `max597x_set_uvp()`, `max597x_set_ovp()`, and `max597x_set_ocp()` implement regulator protection callbacks. `max597x_irq_handler()` maps latched fault registers to regulator events and error flags.

Control flow: platform probe obtains the parent MFD regmap and I2C client, determines switch count from compatible string, allocates per-switch state, decodes ADC ranges, registers regulators, optionally registers hwmon, and attaches a regulator IRQ helper if the parent I2C IRQ exists.

State and persistence: per-switch state stores shunt micro-ohms from each regulator DT node and ADC scaling sampled at probe. Hardware registers hold enable, threshold, and fault latch state; latched faults are read and cleared in the IRQ path.

Dependencies and integration: depends on the MAX5970 MFD header/regmap, OF regulator parsing, optional hwmon, and regulator IRQ helpers.

Risks and test signals: current telemetry and OCP require `shunt-resistor-micro-ohms`; missing properties fail regulator parsing. UV/OV mode depends on POR soft straps, so unsupported severity returns `-EOPNOTSUPP`. Test ADC conversion math, MAX5970 versus MAX5978 switch counts, latched fault clearing, IRQ defer behavior, and OCP out-of-range handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max5970-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77503-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max77503-regulator.c

Purpose: provides a compact single-buck regulator driver for ADI/MAX77503 with voltage selection, current-limit switching, soft-start, active discharge, and enable control.

Important APIs/types/functions: `max77503_buck_ops` uses regulator core regmap helpers for enable, voltage selector, current limit, active discharge, and soft-start. `max77503_regulators_desc` defines the two-register hardware layout: `MAX77503_REG_CFG` for enable/current/soft-start/discharge and `MAX77503_REG_VOUT` for voltage.

Control flow: I2C probe initializes an 8-bit regmap, fills `regulator_config` with the device node and regmap, and registers the single static descriptor.

State and persistence: there is no private driver state after probe beyond devm-managed objects. Hardware registers persist the operating settings as long as the chip is powered.

Dependencies and integration: integrates I2C, regmap, OF matching (`adi,max77503`), and regulator framework generic operations.

Risks and test signals: the regmap max register is `0x2` while only registers `0x00` and `0x01` are used, so tests should check no accidental out-of-range access. Current-limit table has only two entries. Test enable bit, voltage range endpoint mapping, current limit selection, soft-start mask writes, active-discharge polarity, and missing DT constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77503-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77541-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max77541-regulator.c

Purpose: registers the two buck regulators exposed by MAX77540/MAX77541 MFD devices, selecting voltage tables according to the parent chip ID.

Important APIs/types/functions: `max77541_buck_ops` uses pickable linear-range voltage helpers. `MAX77540_BUCK()` and `MAX77541_BUCK()` build descriptors with shared enable register and per-buck VOUT/CFG range registers. `max77541_regulator_probe()` obtains `struct max77541` from the parent and chooses the correct descriptor array.

Control flow: platform probe uses parent driver data to distinguish `MAX77540` from `MAX77541`, then registers `MAX77541_MAX_REGULATORS` descriptors through `devm_regulator_register()`.

State and persistence: no private mutable state is stored in this child driver. The parent MFD owns regmap access, while regulator voltage and enable state reside in PMIC registers.

Dependencies and integration: depends on `linux/mfd/max77541.h`, platform-device MFD instantiation, and regulator core pickable range helpers. Platform IDs are `max77540-regulator` and `max77541-regulator`.

Risks and test signals: incorrect parent chip IDs fail probe. Pickable range tables and selector bitfields must match hardware encoding for both variants. Test buck1/buck2 registration, variant-specific minimum voltages, range selector writes, enable masks, and parent-driver-data absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77541-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77620-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max77620-regulator.c

Purpose: implements regulators for MAX77620, MAX20024, and MAX77663 PMICs. It covers SD buck and LDO rails, flexible power sequencer slots, power modes, ramp rates, active discharge, and suspend/resume FPS reconfiguration.

Important APIs/types/functions: `struct max77620_regulator_info` describes per-rail registers and masks; `struct max77620_regulator_pdata` stores DT-derived FPS and mode options; `struct max77620_regulator` tracks active FPS sources and current/enable power modes. Key helpers include `max77620_regulator_set_fps_src()`, `max77620_regulator_set_fps_slots()`, `max77620_regulator_set_power_mode()`, `max77620_init_pmic()`, and `max77620_of_parse_cb()`.

Control flow: platform probe selects a static rail table by parent chip ID, reuses the parent OF node, initializes per-rail defaults, reads current slew rates, and registers all supported rails. The OF parse callback applies per-rail FPS, power-ok, and ramp settings during registration. PM sleep callbacks switch to suspend FPS slots/sources and restore active settings on resume.

State and persistence: driver state shadows current power mode, enable mode, active FPS source, and per-rail policy. Hardware registers persist programmed power sequencing and voltage settings.

Dependencies and integration: integrates the MAX77620 MFD regmap, OF regulator nodes, regulator core mode/ramp helpers, and PM sleep ops.

Risks and test signals: rails under FPS control report enabled and software enable/disable becomes a no-op. Error returns in suspend/resume helper calls are ignored. Test all three chip tables, SD4 omission on MAX77620, FPS default readback, invalid mode rejection, ramp override behavior, and suspend/resume register updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77620-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77650-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max77650-regulator.c

Purpose: exposes the LDO and three SIMO buck-boost regulators in MAX77650/MAX77651 PMICs, with variant-specific voltage ranges for SBB1/SBB2.

Important APIs/types/functions: `struct max77650_regulator_desc` wraps a regulator descriptor with A/B register addresses. Custom enable ops interpret multi-bit enable fields in the B registers. `max77651_SBB1_regulator_ops` uses pickable linear ranges for the special MAX77651 SBB1 encoding.

Control flow: platform probe inherits the parent OF node if needed, allocates an array of descriptor pointers, obtains the parent regmap, reads the chip ID, picks MAX77650 or MAX77651 SBB descriptors, and registers four regulators.

State and persistence: no persistent private state exists after probe. The parent regmap-backed registers hold enable, voltage, current limit, and active-discharge state.

Dependencies and integration: depends on the MAX77650 MFD core/header, parent regmap, OF regulator nodes, and regulator core current-limit and active-discharge helpers.

Risks and test signals: enable semantics are custom because disabled is a specific multi-bit code, not simply zero. Probe fails on unknown chip IDs. Test MAX77650A/C versus MAX77651A/B descriptor selection, SBB1 pickable range selectors, current-limit table ordering, active discharge bits, and device-tree node inheritance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77650-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77675-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max77675-regulator.c

Purpose: implements the MAX77675 four-channel SIMO buck-boost regulator. It configures global chip behavior from DT, registers present SBB child regulators, supports active discharge, and reports channel/thermal error flags.

Important APIs/types/functions: `struct max77675_regulator` stores regmap, parsed global config, and per-SBB FPS/slew settings. `max77675_parse_config()` validates global DT properties; `max77675_apply_config()` writes global registers; `max77675_of_parse_cb()` parses per-regulator `adi,fps-slot` and `adi,fixed-slew-rate`; `max77675_get_error_flags()` maps global interrupt bits to regulator errors.

Control flow: I2C probe initializes regmap, logs reset/fault events, parses and applies global config, locates the `regulators` subnode, and registers only SBB child nodes found in DT.

State and persistence: parsed global/per-regulator settings are kept in driver memory and programmed into hardware. Error and status registers are volatile under maple cache.

Dependencies and integration: depends on I2C, regmap with volatile-register policy, OF child-node parsing, bitfield helpers, and regulator core.

Risks and test signals: duplicate macro definitions and many DT property encodings raise maintenance risk. Missing individual SBB nodes are warnings, not fatal; missing `regulators` is fatal. Test invalid enum properties, fixed versus DVS slew selection, FPS default readback, per-channel fault flags, thermal alarm mapping, and partial regulator registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77675-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77686-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max77686-regulator.c

Purpose: registers 26 LDOs and 9 buck regulators for the MAX77686 PMIC, including suspend opmodes, DVS ramp tables, and optional GPIO control for selected rails.

Important APIs/types/functions: `struct max77686_data` holds a GPIO-enabled bitmap and per-regulator `opmode` shadow. `max77686_get_opmode_shift()` handles rail-specific enable-bit placement; `max77686_map_normal_mode()` maps normal mode to GPIO-control where applicable; suspend helpers update PWRREQ/low-power modes; `max77686_of_parse_cb()` obtains optional `maxim,ena` GPIOs.

Control flow: platform probe obtains the parent MFD regmap, initializes every opmode to normal, and registers all descriptors. During OF parsing, eligible rails can be switched to GPIO-control mode and given a nonexclusive enable GPIO.

State and persistence: the opmode array is runtime shadow state used by enable and suspend paths. Register settings persist in PMIC hardware; GPIO descriptor lifecycle is mediated through regulator core config.

Dependencies and integration: depends on MAX77686 MFD headers, platform MFD child binding, OF regulator nodes named `voltage-regulators`, GPIO descriptors, and regulator mode/suspend callbacks.

Risks and test signals: only selected rails support GPIO-control remapping, and failed GPIO-control register writes discard the GPIO. BUCK5-9 suspend mode requests are ignored. Test all descriptor IDs, DVS ramp selection, suspend-disable versus suspend-mode behavior, GPIO-control rails, and registration failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77686-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77693-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max77693-regulator.c

Purpose: provides SAFEOUT and charger regulators for MAX77693 and MAX77843 MFD devices. It supports voltage-table SAFEOUT rails and a current regulator for charger input/fast-charge limits.

Important APIs/types/functions: `struct chg_reg_data` abstracts charger register differences. `max77693_chg_get_current_limit()` and `max77693_chg_set_current_limit()` translate linear selector fields to current limits using regulator constraints. `max77693_get_regmap()` chooses the system or charger regmap based on chip type and regulator ID.

Control flow: platform probe reads the platform device ID to select MAX77693 or MAX77843 descriptor arrays and charger data, then registers each descriptor with the appropriate regmap.

State and persistence: there is no private state allocation. The driver passes a static `chg_reg_data` pointer through `config.driver_data`; hardware registers retain enable/current/voltage state.

Dependencies and integration: depends on MAX77693/MAX77843 MFD private headers, parent regmaps, platform child IDs, and regulator core current/voltage APIs.

Risks and test signals: comments note MAX77693 charger handling manipulates maximum input current rather than fast charge current. `config.driver_data` points to charger data for all regulators, but only charger ops consume it. Test regmap routing, SAFEOUT voltage table selection, current constraint boundaries, selector saturation, and both platform IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77693-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77802-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max77802-regulator.c

Purpose: registers MAX77802 buck and LDO regulators, preserving operating modes across enable/suspend operations and exposing ramp tables for DVS-capable bucks.

Important APIs/types/functions: `struct max77802_regulator_prv` stores an `opmode` shadow indexed by regulator ID. `max77802_get_opmode_shift()`, `max77802_set_suspend_disable()`, `max77802_set_mode()`, `max77802_get_mode()`, `max77802_set_suspend_mode()`, and `max77802_enable()` implement mode semantics. Descriptor macros encode separate LDO logic groups and buck families.

Control flow: platform probe gets the parent MAX77686-compatible MFD regmap, allocates private state, reads each regulator's current enable register to seed `opmode`, normalizes hardware OFF to normal for warm reboot cases, and registers all descriptors.

State and persistence: opmode shadow state is important because disabling for suspend changes future enable behavior. Hardware registers contain actual voltage, enable, and ramp settings.

Dependencies and integration: depends on MAX77686/MAX77802 MFD definitions, DT binding IDs, platform child binding, OF regulator nodes, and regulator core suspend/mode/ramp helpers.

Risks and test signals: unsupported suspend-mode transitions deliberately warn and return success in some cases to avoid blocking other regulators. Descriptor count and `MAX77802_REG_MAX` must stay aligned. Test boot readback fallback, OFF-to-normal warm reboot handling, LDO logic groups, buck ramp masks, and mode mapping through OF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77802-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77826-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max77826-regulator.c

Purpose: standalone I2C regulator driver for MAX77826, registering 15 LDOs, one buck, and one buck-boost regulator.

Important APIs/types/functions: descriptor macros `MAX77826_LDO()` and `MAX77826_BUCK()` encode voltage ranges, enable registers, and VSEL registers. `max77826_set_voltage_time_sel()` estimates buck ramp time for upward voltage changes. `max77826_read_device_id()` reads and logs the device ID after registration.

Control flow: I2C probe allocates simple driver info, creates an 8-bit regmap spanning through the device ID register, registers every descriptor, and finally reads the device ID.

State and persistence: private state only stores regmap for driver data. Hardware registers hold all regulator state. The device ID read is diagnostic and occurs after regulator registration.

Dependencies and integration: integrates directly with I2C, regmap, OF matching (`maxim,max77826`), and regulator core linear voltage helpers.

Risks and test signals: no chip-ID validation is performed beyond a debug read, so wrong compatible data may still register. Buck-boost lacks the buck voltage-time callback. Test all LDO voltage families, buck upward ramp timing, enable bit placement by LDO group, and probe failure in the middle of multi-regulator registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77826-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77838-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max77838-regulator.c

Purpose: standalone I2C regulator driver for MAX77838 PMIC, exposing four LDOs and one buck with linear voltage controls and active discharge.

Important APIs/types/functions: `MAX77838_LDO()` and `MAX77838_BUCK_DESC` build static descriptors. `max77838_regulator_ops` delegates enable, voltage, and active-discharge operations to regmap helpers. `max77838_read_device_id()` performs a diagnostic read of `MAX77838_REG_DEVICE_ID`.

Control flow: probe allocates info, initializes an 8-bit regmap through the buck VOUT register, registers five regulators, then reads the device ID.

State and persistence: the only private runtime state is the regmap pointer. Voltage, enable, and discharge settings live in hardware registers.

Dependencies and integration: depends on I2C, regmap, OF matching (`maxim,max77838`), and regulator core. The `regulators` OF subnode and per-rail names are encoded in descriptors.

Risks and test signals: device ID is not validated before registration. The descriptor table is static and assumes all five rails exist. Test LDO versus buck voltage ranges, active-discharge bit polarity, missing regulator child nodes, and regmap max-register coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77838-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77857-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max77857-regulator.c

Purpose: supports ADI/MAX77831, MAX77857, MAX77859, and MAX77859A buck-boost converters with variant-specific voltage encoding, mode control, ramp rates, status/error reporting, and optional MAX77859A current limits.

Important APIs/types/functions: `max77857_get_status()`, `max77857_get_mode()`, `max77857_set_mode()`, and `max77857_get_error_flags()` expose POK, FPWM, and fault bits. MAX77859 voltage setters use 16-bit bulk register access plus a DVS-start bit. `max77857_calc_range()` adjusts linear voltage ranges from feedback resistor properties.

Control flow: probe determines variant from I2C ID, stores it in device driver data for regmap volatile decisions, mutates the global descriptor for MAX77859/MAX77859A, adjusts ranges from DT, initializes regmap, optionally programs switch frequency and ramp table, parses regulator init data, and registers one regulator.

State and persistence: file-scope descriptor and linear-range arrays are mutated at probe time, while regmap cache uses volatile interrupt-source registers. Hardware stores voltage/mode/current settings.

Dependencies and integration: depends on I2C, regmap maple cache, OF properties `adi,rtop-ohms`, `adi,rbot-ohms`, `adi,switch-frequency-hz`, and regulator status/error APIs.

Risks and test signals: global descriptor mutation is unsafe for multiple simultaneous variants. `get_status()` and error flags read the MAX77857 interrupt register even for MAX77859 variants. Test mixed-device probes, big-endian voltage writes, current-limit clamping, switch-frequency selection, and resistor-derived range math.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max77857-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8649.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max8649.c

Purpose: legacy I2C driver for the MAX8649 DCDC regulator, configured by platform data with selectable VID mode register, optional external clock sync, ramp timing, ramp-down, and force-PWM mode.

Important APIs/types/functions: `struct max8649_regulator_info` stores platform-selected mode and regmap. `max8649_enable_time()` computes startup time from current voltage and ramp register. `max8649_set_mode()` and `max8649_get_mode()` toggle/read `MAX8649_FORCE_PWM`. `dcdc_desc` is a single mutable global descriptor whose `vsel_reg` is selected in probe.

Control flow: probe requires platform data, initializes regmap, selects VSEL register from `pdata->mode`, reads chip ID, enables VID0/VID1 controls, applies external clock and ramp options, then registers the regulator.

State and persistence: private state mirrors platform settings. Register state persists on hardware; enable uses an inverted power-down bit.

Dependencies and integration: uses I2C, regmap, legacy `linux/regulator/max8649.h` platform data, and subsys init registration.

Risks and test signals: probe dereferences platform data without a null check, and the global descriptor is mutated per device, which is unsafe for multiple instances with different modes. Test missing pdata, all VID modes, inverted enable behavior, external clock frequency bits, ramp timing, and enable-time calculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8649.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8660.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max8660.c

Purpose: supports MAX8660/MAX8661 voltage regulators V3 through V7. The device is write-only, so the driver maintains shadow registers and exposes only regulators described by platform data or DT.

Important APIs/types/functions: `struct max8660` holds the I2C client and `shadow_regs`. `max8660_write()` applies masked writes to the shadow copy then writes the physical address. Separate ops handle DCDC V3/V4, LDO5, and LDO6/7 voltage and enable behavior. `max8660_pdata_from_dt()` maps OF regulator nodes into platform-style subdevices.

Control flow: probe builds platform data from DT when needed, validates regulator count and chip variant, initializes conservative shadow defaults, applies boot-on bits in shadows, and registers each requested regulator.

State and persistence: shadow registers are the only readback source. They are initialized to assumed defaults and do not reflect pre-Linux hardware state except for boot-on hints.

Dependencies and integration: depends on I2C SMBus writes, legacy platform data, optional OF regulator matching, and regulator core.

Risks and test signals: write-only hardware makes warm-boot accuracy dependent on assumptions. `max8660_dcdc_ops` is modified globally when EN34 can be software controlled. MAX8661 lacks V7 and must reject it. Test shadow updates, boot-on initialization, DT matching by regulator names, MAX8660 versus MAX8661, and multi-instance global ops mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8660.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8893.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max8893.c

Purpose: simple I2C regulator driver for MAX8893, registering one buck and five LDO regulators with fixed linear voltage ranges and regmap-backed enable/VSEL controls.

Important APIs/types/functions: `max8893_ops` uses standard regmap regulator helpers. `max8893_regulators[]` statically describes BUCK and LDO1-LDO5 names, supply names, OF matches, voltage ranges, VSEL registers, and enable bits. `max8893_probe()` initializes regmap and registers all descriptors.

Control flow: probe creates the regmap, then loops through the descriptor table registering each regulator with a shared `regulator_config` containing only `dev`. The regmap is associated with the device by the regulator core through regmap-backed descriptors.

State and persistence: no private state is stored. Hardware registers hold enable and voltage selector values.

Dependencies and integration: depends on I2C, regmap, OF compatible `maxim,max8893`, and the regulator core.

Risks and test signals: `config.regmap` is not explicitly assigned, so registration relies on dev/regmap lookup behavior. There is no chip-ID validation. Test all six rails, enable bit mapping in register 0, VSEL masks/ranges, OF child matching, and probe failure if regmap lookup is not available to regulator helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8893.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8907-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max8907-regulator.c

Purpose: registers the MAX8907 PMIC regulator set: main battery pseudo-rail, SD regulators, 20 LDOs, fixed rails, OUT5V/OUT33V, and backup battery charger voltage control.

Important APIs/types/functions: descriptor macros build the regulator table. `max8907_regulator_parse_dt()` matches child regulators. Probe copies descriptors into per-device storage so it can adjust MAX8907B SD1 voltage metadata and switch ops to hardware-control variants. `match_init_data()` and `match_of_node()` bridge DT parsing.

Control flow: platform probe parses DT, allocates per-device descriptors, reads the revision register, adjusts SD1 for revision B, establishes MBATT as a supply name for BBAT/SDBY/VRTC, detects hardware-controlled LDO/OUT5V rails by reading control registers, and registers every descriptor.

State and persistence: per-device descriptor copies are mutable state. Hardware control status determines whether software enable/disable ops are exposed.

Dependencies and integration: depends on MAX8907 MFD regmaps/platform data, OF regulator matching, and regulator core.

Risks and test signals: when no init data exists, BBAT/SDBY/VRTC paths dereference `idata` while assigning `supply_regulator`. Test DT-only configurations, revision B SD1 values, hardware-control op switching, MBATT naming, platform-data init data arrays, and all regulator registrations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8907-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8925-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max8925-regulator.c

Purpose: MFD child driver registering one MAX8925 regulator per platform device/resource. It supports SDV1-3 and LDO1-20, including SDV suspend/DVM voltage controls.

Important APIs/types/functions: `struct max8925_regulator_info` embeds a descriptor plus voltage and enable register addresses. `max8925_set_voltage_sel()`/`get_voltage_sel()` use parent `max8925_set_bits()` and register reads. `max8925_enable()`, `max8925_disable()`, and `max8925_is_enabled()` manage I2C sequencing bits. SDV ops add suspend voltage/enable/disable callbacks.

Control flow: platform probe obtains the parent chip, finds the regulator descriptor whose `vol_reg` matches the platform `IORESOURCE_REG`, fills the parent I2C pointer, applies optional init data, registers one regulator, and stores the rdev as platform data.

State and persistence: descriptor table entries are static and get their `i2c` pointer filled at probe. Hardware registers store enable, sequencing, and voltage settings.

Dependencies and integration: depends on MAX8925 MFD APIs, platform resources created by the parent, and regulator core.

Risks and test signals: static descriptor entries are mutated with the parent I2C pointer, so multiple PMIC instances could conflict. Floating-point-looking macro arguments are multiplied by 1000 in C constants but deserve compile/test scrutiny. Test resource-to-regulator matching, I2C sequencing detection, SDV DVM suspend range, LDO enable semantics, and missing resource failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8925-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8952.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max8952.c

Purpose: legacy I2C driver for MAX8952 voltage regulator with four DVS voltage modes selected by optional VID0/VID1 GPIOs and an optional enable GPIO.

Important APIs/types/functions: `struct max8952_data` stores client, platform data, VID GPIO descriptors, and current VID bits. `max8952_parse_dt()` converts DT microvolt DVS values into chip selector values. `max8952_set_voltage_sel()` toggles VID GPIOs; `max8952_list_voltage()` maps selectors through platform DVS data.

Control flow: probe obtains platform data or parses DT, checks SMBus byte support, registers the regulator with optional `"max8952,en"` GPIO, acquires VID GPIOs, disables DVS if either VID GPIO is missing, programs MODE0-3, SYNC, and RAMP registers, and stores client data.

State and persistence: `vid0`/`vid1` are driver shadows of GPIO-selected mode. Programmed DVS tables and ramp/sync settings persist in chip registers while powered.

Dependencies and integration: depends on I2C SMBus byte access, GPIO descriptors, legacy platform data or OF properties, and regulator core.

Risks and test signals: DVS writes return `-EPERM` when either VID GPIO is unavailable. Register write/read return values are mostly unchecked during final programming. Test DT voltage range validation, enable GPIO boot-on state, missing VID GPIO fallback, MODE register programming, and selector-to-voltage mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8952.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8973-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max8973-regulator.c

Purpose: supports MAX8973 and MAX77621 step-down regulators with optional DVS GPIO selection between two VOUT registers, configurable control flags, current limit on MAX77621, and thermal-zone/IRQ support for MAX77621.

Important APIs/types/functions: `struct max8973_chip` owns a mutable descriptor, ops copy, regmap, DVS GPIO, LRU voltage-register state, thermal state, and chip ID. `find_voltage_set_register()` implements two-entry LRU caching. `max8973_init_dcdc()` programs CONTROL1/2 from platform/DT flags. `max8973_thermal_init()` registers a thermal zone and optional threaded IRQ.

Control flow: probe parses platform data or DT, gets optional DVS GPIO, initializes regmap, determines chip ID, reads CHIPID1, builds the descriptor/ops, configures DVS or fixed VSEL behavior, handles enable control differences for MAX8973/MAX77621, initializes hardware control registers, registers the regulator, then initializes thermal support.

State and persistence: LRU arrays and current GPIO/VOUT state track which VOUT register contains which voltage. Hardware stores control flags, voltage selectors, and mode/current-limit settings.

Dependencies and integration: depends on I2C, regmap, GPIO, OF/platform data, regulator core, thermal framework, and IRQ APIs.

Risks and test signals: LRU initialization mixes register addresses and indexes, requiring careful validation. Some final initialization paths log but do not always fail thermal setup. Test DVS and non-DVS paths, external enable GPIO lifecycle, MAX77621 current limit and thermal IRQ, control flag encoding, and multi-step voltage changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8973-regulator.c -->
