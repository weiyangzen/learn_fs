# subset-b-005184 grouped research

Work item `subset-b-005184` covers Qualcomm, Renesas, and Ricoh regulator/PMIC support files under `sources/distributed-fs/ceph-client/drivers/regulator/`. Each section preserves the source path and is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/qcom-rpmh-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/qcom-rpmh-regulator.c

## Purpose
This driver registers Qualcomm RPMh-managed PMIC regulators. It translates Linux regulator operations for LDO, SMPS, BOB, LVS, and XOB resources into RPMh VRM/TCS commands addressed through the RPMh command database, covering many PMIC families from PM8998 through PM660-era compatibility data.

## Important APIs, Types, and Functions
`struct rpmh_vreg_hw_data` describes regulator class behavior: regulator type, ops table, voltage ranges, mode map, OF mode mapper, and high-performance load threshold. `struct rpmh_vreg` stores the registered descriptor, RPMh address, cached enable/voltage/mode/bypass state, and `qcom,always-wait-for-ack`. Core functions are `rpmh_regulator_send_request()`, `_rpmh_regulator_vrm_set_voltage_sel()`, `rpmh_regulator_set_enable_state()`, `rpmh_regulator_vrm_set_mode_bypass()`, `rpmh_regulator_init_vreg()`, and `rpmh_regulator_probe()`. PMIC-specific arrays built with `RPMH_VREG()` map DT child names to RPMh resource names, hardware data, indices, and supply names.

## Control Flow
Probe reads `qcom,pmic-id`, gets the matched PMIC regulator table, and iterates available child nodes. Each child is matched by node name, converted into an RPMh command DB resource name, resolved with `cmd_db_read_addr()`, configured as a `regulator_desc`, and registered with `devm_regulator_register()`. Runtime enable/disable writes `RPMH_REGULATOR_REG_ENABLE`; voltage writes convert linear-range uV to millivolts and write `RPMH_REGULATOR_REG_VRM_VOLTAGE`; mode and bypass write `RPMH_REGULATOR_REG_VRM_MODE`. Enabling waits for acknowledgment; voltage increases wait, decreases may use async unless `qcom,always-wait-for-ack` is set.

## State and Persistence
The driver has no disk persistence. It caches the last successful voltage selector, enable state, regulator mode, bypass state, RPMh address, and always-ack policy in devm-managed memory. Initial hardware state is mostly unknown (`enabled = -EINVAL`, invalid mode, unrecoverable voltage selector), so voltage may be cached until the first enable/disable request. Hardware programming persists in RPMh/PMIC state until overwritten or reset.

## Dependencies and Integration Points
Integration points are the platform driver framework, OF match data, regulator core, `of_get_regulator_init_data()`, RPMh APIs (`rpmh_write()`, `rpmh_write_async()`), command DB resource lookup, and Qualcomm DT bindings for PMIC regulator child names and `qcom,pmic-id`. The driver exposes standard regulator ops, OF mode mapping, supplies, and constraints to consumers.

## Risks and Test Signals
Risk areas include PMIC table mistakes, command DB resource-name formatting for normal versus `_E` PMIC IDs, async writes racing consumers that expect completion, cached unknown enable/voltage state at boot, and mode-map incompatibilities across PMIC generations. Test signals include successful probe for each compatible, missing-resource failure paths, regulator enable/disable and voltage transitions with RPMh tracing, mode and bypass behavior, fixed-voltage XOB constraints, and DT validation for child names and supplies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/qcom-rpmh-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/qcom_rpm-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/qcom_rpm-regulator.c

## Purpose
This legacy Qualcomm RPM regulator driver supports pre-SMD RPM PMIC regulators. It encodes regulator state into RPM request words for PM8018, PM8058, PM8901, PM8921, and SMB208 resources and exposes voltage regulators, switches, and NCP resources through the regulator framework.

## Important APIs, Types, and Functions
`struct request_member` describes a bitfield inside an RPM request word. `struct rpm_reg_parts` groups bitfields for voltage, currents, pull-down, force mode, pin control, frequency, enable, and other PMIC-specific controls. `struct qcom_rpm_reg` holds the RPM handle, mutable request words, regulator descriptor, resource id, cached voltage and enable state, and force-mode capability flags. Key functions are `rpm_reg_write()`, `rpm_reg_set_mV_sel()`, `rpm_reg_set_uV_sel()`, the enable/disable variants, `rpm_reg_set_load()`, `rpm_reg_of_parse_freq()`, `rpm_reg_of_parse()`, and `rpm_reg_probe()`.

## Control Flow
Probe obtains the parent `qcom_rpm` handle, selects the compatible-specific regulator table, clones each template with `devm_kmemdup()`, fills resource id/name/supply/of_match, and registers the descriptor. The OF parse callback preloads request-word bits for pull-down, switch-mode frequency, hysteretic/PWM power mode, and force mode. Voltage setters update cached `uV` and write to RPM only if already enabled. Enable paths write voltage first for voltage regulators, then write enable/current fields; disable paths clear enable-related fields. Switch regulators only program enable state.

## State and Persistence
State is a mutex-protected pair of RPM request words plus cached `uV` and `is_enabled`. The cache is authoritative for `get_voltage()` and `is_enabled()` and is updated only after successful RPM writes. DT-derived options are packed into the same request words before registration. No persistent storage exists; RPM/PMIC hardware state outlives the driver only until reset or later RPM requests.

## Dependencies and Integration Points
The file depends on the regulator core, OF regulator parsing, `linux/mfd/qcom_rpm.h`, `dt-bindings/mfd/qcom-rpm.h`, and parent RPM MFD/platform setup. It integrates with DT compatibles such as `qcom,rpm-pm8921-regulators` and regulator child nodes named by the static tables. It registers during `subsys_initcall()` so consumers can resolve supplies early.

## Risks and Test Signals
Risk areas include bitfield packing overflow, unsupported force-mode values, mandatory frequency properties for regulators with frequency fields, cache divergence if RPM rejects a write, and template-table supply/resource mistakes. Test signals include bitfield boundary tests, probe against each compatible, DT parse errors for invalid force mode or frequency, enable/disable sequencing, voltage selection on disabled and enabled regulators, load programming, and RPM write fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/qcom_rpm-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/qcom_smd-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/qcom_smd-regulator.c

## Purpose
This driver registers regulators controlled by Qualcomm SMD RPM firmware. It converts regulator enable, voltage, and load requests into key/value SMD RPM messages for many PMIC families, including PM8916, PM8941, PM8994, PM8998, PM660, PM6125, PM2250, PMS405, PMR735A, and MP5496 variants.

## Important APIs, Types, and Functions
`struct qcom_rpm_reg` stores the SMD RPM resource type/id, descriptor, cached enable/voltage/load values, and dirty bits for each property. `struct rpm_regulator_req` is the packed key/nbytes/value message element using keys `"swen"`, `"uv"`, and `"ma"`. Important functions are `rpm_reg_write_active()`, `rpm_reg_enable()`, `rpm_reg_disable()`, `rpm_reg_set_voltage()`, `rpm_reg_set_load()`, `rpm_regulator_init_vreg()`, and `rpm_reg_probe()`. Descriptor templates encode voltage ranges and ops for SMPS/LDO, fixed regulators, switches, BOB, and MP5496-specific behavior.

## Control Flow
Probe obtains the parent `qcom_smd_rpm`, rejects a second distinct RPM instance through the global `smd_vreg_rpm`, selects match data, and iterates available child nodes. Each node is matched by name against the PMIC table, then a descriptor copy is registered with `devm_regulator_register()`. Runtime ops mark a field dirty, update the cache, and call `rpm_reg_write_active()`, which emits only dirty fields and only sends voltage/load values while the regulator is enabled. On successful SMD write, dirty bits are cleared; on failure, the changed cache field is rolled back by the caller.

## State and Persistence
Driver state is volatile per-regulator memory plus a global SMD RPM pointer. Cached `is_enabled`, `uV`, and `load` are what getter paths report. Dirty bits preserve pending changes across write attempts. Voltage and load changes while disabled are cached but not sent until enable causes a fresh active-state write. There is no on-disk persistence.

## Dependencies and Integration Points
The driver depends on `linux/soc/qcom/smd-rpm.h`, platform/OF match data, the regulator core, linear voltage range helpers, and parent SMD RPM device setup. It exposes child-node regulator names via PMIC tables and integrates with standard regulator supplies and constraints from DT.

## Risks and Test Signals
Risk areas include the single global RPM pointer preventing multiple independent RPM instances, cache-only voltage/load updates while disabled, broad PMIC table maintenance, and lack of locking around cached state changes. Test signals include probing all compatible tables, multi-PMIC mismatch handling, SMD write failure rollback, enable after deferred voltage/load changes, switch-only regulators, fixed-voltage descriptors, and userspace regulator summary consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/qcom_smd-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/qcom_spmi-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/qcom_spmi-regulator.c

## Purpose
This driver controls Qualcomm SPMI PMIC regulators directly through the parent PMIC regmap. It supports many regulator logical types, voltage range encodings, mode encodings, OCP retry behavior for voltage switches, optional SAW voltage delegation, and PMIC-specific register-base tables for PM6125, PM660, PM8916, PM8941, PM8994, PMP8074, and related chips.

## Important APIs, Types, and Functions
`struct spmi_voltage_range` and `struct spmi_voltage_set_points` describe hardware voltage ranges and software selector spaces. `struct spmi_regulator_mapping` maps type/subtype/revision tuples to logical type, set points, ops, and HPM load threshold. `struct spmi_regulator` stores the regmap, base address, descriptor, set points, slew rate, DT pin-control defaults, OCP work state, and list node. Key functions include `spmi_vreg_read()`, `spmi_vreg_write()`, `spmi_regulator_select_voltage()`, selector conversion helpers, voltage get/set/list/map functions, mode/load/pull-down/soft-start/current-limit helpers, `spmi_regulator_vs_ocp_isr()`, SAW helpers, `spmi_regulator_match()`, `spmi_regulator_init_registers()`, `spmi_regulator_of_parse()`, and `qcom_spmi_regulator_probe()`.

## Control Flow
Probe gets the parent regmap, PMIC match table, optional `qcom,saw-reg` syscon, and then iterates static regulator entries. For each entry it skips SAW slave nodes, allocates `spmi_regulator`, sets register base/name/supply/of_parse callbacks, obtains optional OCP IRQ, and calls `spmi_regulator_match()` to read hardware revision/type/subtype and choose the correct ops and voltage set points. OF parsing applies pin control, pull-down, soft-start, OCP retry properties, and startup register settings. Runtime voltage mapping favors staying in the current range to avoid spikes, then writes range/select registers; modes and load requests update mode registers; OCP interrupts clear and re-enable switches immediately or after a retry delay until retries are exhausted.

## State and Persistence
Most state lives in PMIC registers. In memory the driver caches static description, set-point pointers, calculated `n_voltages`, slew rate, DT config, OCP retry counters/timestamps, and a list of registered regulators. Voltage and mode getters read hardware live. OCP recovery uses delayed work and volatile counters. There is no persistent storage beyond PMIC register state.

## Dependencies and Integration Points
The driver depends on regmap, OF/platform match data, regulator regmap helpers, delayed work, IRQs, syscon/regmap for SAW, and Qualcomm SPMI PMIC register layout. Integration points include DT regulator child nodes, named OCP IRQs, optional `qcom,saw-leader`/`qcom,saw-slave` properties, regulator constraints, and standard regulator sysfs/debug consumers.

## Risks and Test Signals
Risk areas include voltage range conversion mistakes, ignored `spmi_vreg_read()` return values in several read helpers, static/global `saw_regmap` and mutable `spmi_saw_ops`, continuing probe when a listed regulator is unsupported, OCP delayed-work lifetime, and PMIC table/register-base drift. Test signals include probe on each compatible, hardware type/subtype mismatch logs, selector round trips at range boundaries, current-range voltage changes, slew-time calculations, DT pin-control parsing, OCP IRQ retry exhaustion, SAW leader/slave behavior, and regmap fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/qcom_spmi-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/qcom_usb_vbus-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/qcom_usb_vbus-regulator.c

## Purpose
This small Qualcomm PMIC driver exposes the USB VBUS OTG output as a regulator. It supports software enable/disable and selectable current limits for PM8150B-style VBUS regulator blocks.

## Important APIs, Types, and Functions
The driver defines the OTG command, current-limit, and configuration registers relative to a DT-provided base address. `curr_table` exposes 500 mA through 3 A current limits. `qcom_usb_vbus_reg_ops` uses generic regmap regulator helpers for enable, disable, status, and current-limit operations. `qcom_usb_vbus_regulator_probe()` reads resources, patches `qcom_usb_vbus_rdesc`, registers the regulator, and disables hardware-controlled VBUS enable logic.

## Control Flow
Probe reads the `reg` property as the register base, obtains the parent regmap, retrieves regulator init data, fills `enable_reg`, `enable_mask`, `csel_reg`, and `csel_mask` in the static descriptor, registers the regulator, then clears `OTG_EN_SRC_CFG` so software controls VBUS enable. Runtime control is delegated to regulator core regmap helpers.

## State and Persistence
There is no private per-device state. The static descriptor is updated at probe time with register addresses, and PMIC registers store enable/current-limit state. The final `regmap_update_bits()` changes hardware behavior until reset or later reconfiguration.

## Dependencies and Integration Points
The file depends on a parent PMIC regmap, a DT node compatible with `qcom,pm8150b-vbus-reg`, a valid `reg` base, and regulator constraints from OF. It integrates with USB/OTG consumers through a standard `usb_vbus` regulator name and current-limit operations.

## Risks and Test Signals
Risk areas include the mutable static descriptor if multiple instances ever probe, ignoring the return value when disabling hardware VBUS enable logic, current selector/table mismatch, and missing parent regmap. Test signals include probe failure for missing `reg`/regmap, regulator enable bit transitions, current-limit selector programming, and verifying `OTG_EN_SRC_CFG` is cleared after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/qcom_usb_vbus-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/raa215300.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/raa215300.c

## Purpose
This Renesas RAA215300 PMIC driver performs top-level I2C PMIC setup and optionally instantiates the companion RTC device when a 32.768 kHz input clock is present. Despite living under regulator drivers, it is primarily PMIC initialization, interrupt masking, and RTC/clock wiring.

## Important APIs, Types, and Functions
`raa215300_regmap_config` defines an 8-bit register/8-bit value regmap over I2C. `raa215300_clk_present()` probes optional `xin` and `clkin` clock inputs. `raa215300_i2c_probe()` initializes regmap, reads hardware revision, clears block enables except an already enabled RTC, clears latched fault registers, masks all PMIC interrupts, registers a fixed-rate clock when present, enables the RTC block, and creates an I2C RTC client. `raa215300_rtc_unregister_device()` is the devm cleanup action.

## Control Flow
Probe initializes regmap and reads `RAA215300_HW_REV`. It then reads `REG_BLOCK_EN`, preserves only `RTC_EN`, writes it back, clears five latched fault status registers by read/write, and masks all interrupt groups. It prefers an optional `xin` clock over `clkin`; if either exists, it registers a fixed 32768 Hz clock, picks RTC type `isl1208` for hardware revision >= 0x12 or `raa215300_a0` otherwise, optionally reads the `rtc` address from `reg-names`/`reg`, passes through the parent IRQ, enables the RTC block, creates the RTC I2C device, and registers cleanup.

## State and Persistence
The driver keeps no long-lived private structure. PMIC register writes clear latched faults, mask interrupts, and enable/disable blocks. The created RTC client and fixed-rate clock are devm-managed. There is no disk persistence.

## Dependencies and Integration Points
It depends on I2C, regmap, optional common clock framework consumers/producers, OF properties, and the downstream RTC driver selected by I2C type. The DT compatible is `renesas,raa215300`; optional `xin`/`clkin` clocks control RTC instantiation.

## Risks and Test Signals
Risk areas include largely unchecked regmap read/write errors after the hardware revision read, destructive clearing/masking of PMIC status on probe, optional clock ambiguity, RTC address parsing from multi-entry `reg`, and child I2C client creation failure. Test signals include I2C regmap fault injection, revision-dependent RTC type, systems with no clock versus `xin`/`clkin`, interrupt mask register contents after probe, RTC cleanup on driver unbind, and preservation of pre-enabled RTC bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/raa215300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rc5t583-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rc5t583-regulator.c

## Purpose
This driver registers the DC and LDO regulators of the Ricoh RC5T583 PMIC. It uses the parent MFD regmap and platform data to expose 14 voltage regulators with linear voltage tables, enable control, voltage selection, ramp timing, and optional external/deepsleep power control.

## Important APIs, Types, and Functions
`struct rc5t583_regulator_info` wraps per-regulator deepsleep metadata, discard/deepsleep registers, enable ramp speed, and a `regulator_desc`. The `RC5T583_REG()` macro builds all descriptors with enable/vsel registers, voltage range, step size, masks, and ramp delay. `rc5t583_ops` uses generic regmap helpers plus `rc5t583_regulator_enable_time()`. `rc5t583_regulator_probe()` obtains parent MFD data/platform data, configures external power request slots, and registers each descriptor.

## Control Flow
Probe requires platform data from the parent RC5T583 device. It loops over `RC5T583_REGULATOR_MAX`, optionally calls `rc5t583_ext_power_req_config()` for deepsleep/external control based on platform data, logs warnings but continues on those configuration failures, then registers each regulator with init data, driver data, and parent regmap. Runtime operations are almost entirely delegated to regulator regmap helpers. Enable time is calculated from the selected voltage and the regulator-specific `enable_uv_per_us`.

## State and Persistence
The static `rc5t583_reg_info` array holds descriptors and per-regulator metadata. Hardware state lives in the PMIC registers accessed by the parent regmap. Platform data controls deepsleep slots and init constraints. There is no persistent storage outside register state.

## Dependencies and Integration Points
The file depends on the RC5T583 MFD core/header, parent regmap, legacy platform data, regulator core, and `subsys_initcall()` registration. It does not parse OF directly; board data must provide regulator init data and external power/deepsleep configuration.

## Risks and Test Signals
Risk areas include mandatory platform data, static descriptor maintenance, enable-time calculation when voltage selector reads fail, external power configuration warnings hiding board integration issues, and correct alignment of platform arrays with regulator ids. Test signals include registration of all 14 regulators, voltage selector boundaries, enable/ramp timing, missing platform-data failure, external/deepsleep configuration failures, and regmap enable/vsel writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rc5t583-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/regnl.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/regnl.h

## Purpose
This private regulator header declares the netlink event emission hook used by regulator code to report regulator events by regulator name and event mask.

## Important APIs, Types, and Functions
The only API is `int reg_generate_netlink_event(const char *reg_name, u64 event);`. Include guards use `__REGULATOR_EVENT_H`, and the header carries GPL-2.0-or-later licensing.

## Control Flow
There is no executable control flow in this header. Callers include it to access the implementation-provided event generator.

## State and Persistence
The header defines no state and has no persistence behavior. Any state or side effects belong to the implementation of `reg_generate_netlink_event()`.

## Dependencies and Integration Points
It depends on standard kernel integer types for `u64` via includer context. It is an internal integration point between regulator event producers and the regulator netlink event implementation.

## Risks and Test Signals
Risk areas are declaration drift from the implementation and insufficient type includes if included from a translation unit that has not already defined `u64`. Test signals are compile coverage of all includers and runtime verification that regulator events produce expected netlink notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/regnl.h -->
