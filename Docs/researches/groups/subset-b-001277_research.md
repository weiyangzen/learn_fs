# subset-b-001277 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-max77843.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-max77843.c

## Purpose
MAX77843 MUIC extcon provider for micro-USB accessory, charger, dock, MHL, JIG, and USB host/device detection. It is a platform child of the MAX77843/MAX77693-style MFD and creates a secondary MUIC I2C client/regmap plus a regmap IRQ chip. Its public kernel-facing output is an `extcon_dev` advertising USB, USB host, SDP/CDP/DCP/fast/slow chargers, MHL, dock, and JIG.

## Important APIs, Types, and Functions
`struct max77843_muic_info` owns the device, parent MFD pointer, extcon device, mutex, IRQ work, delayed initial detect work, last status register snapshot, previous ADC/charger/ground classifications, and pending IRQ flags. The register model is `max77843_muic_regmap_config`, `max77843_muic_irq[]`, and `max77843_muic_irq_chip`. `max77843_muic_set_path()` switches CONTROL1 COM routing and CONTROL2 low-power/charge-pump bits. `max77843_charger_set_otg_vbus()` drives charger OTG/boost mode for USB host. `max77843_muic_get_cable_type()` classifies ADC, charger, and ground-special cables while preserving previous type for detach. Handler functions split policy into ADC ground, JIG, dock, generic ADC, and charger cases. Probe initializes the MUIC regmap, registers extcon, disables auto detection, configures debounce, requests virtual IRQs, and schedules delayed cold-plug detection.

## Control Flow
Probe allocates `max77843_muic_info`, initializes a dummy MUIC I2C client at `I2C_ADDR_MUIC`, creates a regmap, adds a three-register IRQ chip, disables USB/factory auto mode, registers extcon, sets ADC debounce to 25 ms, and reads the current status for possible UART JIG path setup. It then maps every MUIC IRQ to a virtual IRQ and registers `max77843_muic_irq_handler()`. IRQ handlers only set `irq_adc` or `irq_chg` and schedule `irq_work`. `max77843_muic_irq_work()` locks, bulk-reads STATUS1-3, dispatches ADC and charger handlers, clears the pending flags, and unlocks. The delayed cold-plug worker runs after 15 seconds, reads the same status registers, and invokes ADC and charger handlers for already-attached cables.

## State and Persistence
Runtime state is in hardware registers and volatile in-memory fields. `prev_cable_type`, `prev_chg_type`, and `prev_gnd_type` are used to report correct detach events after an open/no-charger reading. `status[]` is a cached bulk-read of STATUS registers during work execution. The driver persists no configuration outside hardware register writes; suspend/resume handling is absent here.

## Dependencies and Integration Points
Depends on Linux extcon provider APIs, I2C/regmap/regmap-irq, workqueues, platform driver core, MAX77843/MAX77693 MFD definitions, and the charger regmap. It integrates with consumers through extcon state and with the parent MFD through `dev_get_drvdata(pdev->dev.parent)`, `max77843->irq`, `max77843->regmap_chg`, and `max77843->irq_data_muic`.

## Risks
The probe path ignores the return from disabling auto detection and from debounce setup, which can hide partial hardware initialization. Error paths manually unregister the dummy I2C client and IRQ chip, so ordering matters. IRQ work reports unused ADC accessory classes as errors/EAGAIN, which can be noisy on boards with unsupported accessories. Host OTG VBUS is controlled through charger mode bits, so misclassification can affect power delivery. There is no explicit cancellation of the delayed cold-plug work in remove.

## Test Signals
Useful signals are MUIC device ID logs, `CONTROL1/CONTROL2` debug logs, extcon uevents for USB/USB_HOST/charger/MHL/dock/JIG, successful virtual IRQ mapping, and attach/detach behavior for ADC ground, SmartDock, JIG USB/UART, SDP/CDP/DCP, special chargers, and MHL with/without VBUS. Fault injection should cover failed regmap reads/writes, missing virtual IRQs, and detach paths that rely on previous type fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-max77843.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-max8997.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-max8997.c

## Purpose
MAX8997 MUIC extcon provider for Samsung-era micro-USB accessory and charger detection. It maps MAX8997 MUIC and PMIC charge insert/remove interrupts into extcon states for USB device, USB host, SDP/CDP/DCP/fast/slow chargers, MHL, dock, and JIG.

## Important APIs, Types, and Functions
`struct max8997_muic_info` stores the MUIC I2C client, extcon device, previous ADC/charger type, two-byte status cache, current IRQ, work item, mutex, platform data, delayed cold-plug work, and default USB/UART switch paths. `max8997_muic_set_debounce_time()` programs ADC debounce. `max8997_muic_set_path()` programs CONTROL1 switch routing and CONTROL2 low-power/charge-pump bits. `max8997_muic_get_cable_type()` classifies ADC or charger groups and preserves previous values for detaches. `max8997_muic_handle_usb()`, `_handle_dock()`, and `_handle_jig_uart()` apply switch paths and extcon notifications. `max8997_muic_probe()` binds to the parent MFD, requests IRQ-domain mappings, registers extcon, applies platform initialization data, and schedules delayed initial detection.

## Control Flow
Probe obtains `struct max8997_dev` and optional platform MUIC data, registers threaded IRQs for ADC, VBVolt, charger-detect, OVP, and PMIC charger insert/remove lines, then registers extcon. If platform data exists, the driver writes board-provided initial register values and uses board-provided USB/UART paths and detect delay; otherwise defaults are used. It reads current STATUS1/2 to route UART JIG early, sets ADC debounce, and queues delayed detection. At runtime the threaded IRQ stores the virtual IRQ in `info->irq` and schedules work. `max8997_muic_irq_work()` maps that virtual IRQ back to a logical MUIC/PMIC interrupt, reads STATUS1/2, dispatches ADC or charger handling, and logs unsupported interrupts.

## State and Persistence
The only persistent effects are MUIC register programming and extcon state. Previous cable and charger types are per-device fields used to classify detach after open/no-charger statuses. `info->irq` is a transient one-slot pending IRQ field, so simultaneous IRQs before work runs can overwrite each other; the regmap/IRQ domain may still latch source state, but this worker only dispatches one stored IRQ type.

## Dependencies and Integration Points
Uses extcon provider, MAX8997 MFD register helpers (`max8997_update_reg`, `max8997_bulk_read`, `max8997_write_reg`), IRQ domain mapping, platform data, and workqueues. It integrates with board data through `struct max8997_muic_platform_data` for initial register writes, routing, and cold-plug delay.

## Risks
The single `info->irq` field is a race-prone compression of interrupt sources. The PMIC charger insert/remove IRQs share the charger handler, so charger classification depends on fresh STATUS2 reads. Unsupported ADC accessories return `-EAGAIN`, producing error logs during boot cold-plug detection. Probe has no remove callback to cancel delayed work, though devm work autocancel is used only for `irq_work`; the delayed work is initialized manually. Board-specific path values and init data can change core routing behavior.

## Test Signals
Check extcon uevents for USB host, USB device plus SDP, CDP, DCP, fast/slow chargers, MHL, dock, and JIG. Validate platform-data defaults versus custom USB/UART paths. Exercise ADC open detach after each attach type, PMIC charger insert/remove, cold-plug after the configured delay, and failures from STATUS reads or IRQ mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-max8997.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-palmas.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-palmas.c

## Purpose
Palmas/TWL6035 USB transceiver extcon provider for USB VBUS and ID detection. It reports `EXTCON_USB` for peripheral/VBUS and `EXTCON_USB_HOST` for grounded ID, using either Palmas internal interrupt/status registers or optional GPIO-backed ID/VBUS inputs.

## Important APIs, Types, and Functions
The driver operates on `struct palmas_usb` defined by the Palmas MFD headers. `palmas_usb_wakeup()` programs USB wakeup comparator enable. `palmas_vbus_irq_handler()` reads `PALMAS_INT3_LINE_STATE` and updates USB peripheral state. `palmas_id_irq_handler()` reads ID latch/source registers and updates host state. `palmas_gpio_id_detect()` is the software-debounced GPIO ID worker. `palmas_enable_irq()` enables hardware comparators and performs initial internal detection. Probe parses DT/platform options, optional `id` and `vbus` GPIOs, allocates extcon, requests internal or GPIO IRQs, and runs initial detection.

## Control Flow
Probe selects detection sources: DT booleans enable internal ID/VBUS detection, but present GPIOs override the matching internal path. GPIO ID can use hardware debounce or software delayed work. Internal ID and VBUS paths request virtual IRQs from the Palmas regmap IRQ data; GPIO paths call `gpiod_to_irq()` and request threaded IRQs. After registration, `palmas_enable_irq()` enables VBUS and ID comparators, optionally invokes the VBUS handler immediately, sleeps for host cold-plug stabilization, and invokes the ID handler. Probe also invokes GPIO initial detection. Suspend enables wake on active IRQs; resume disables wake and rechecks GPIO-backed state.

## State and Persistence
`palmas_usb->linkstat` tracks disconnected, VBUS, or ID state to suppress duplicate VBUS and ID events. Register latch clears are written for ID ground/float transitions. GPIO detection does not update `linkstat` in `palmas_gpio_id_detect()`, so hardware and GPIO paths have different state caches. No file-backed persistence exists.

## Dependencies and Integration Points
Depends on Palmas MFD register helpers and IRQ data, extcon provider APIs, GPIO descriptor APIs, OF/platform data, delayed work, and PM wakeup. It stores the USB child in `palmas->usb` for MFD-level integration.

## Risks
The VBUS GPIO acquisition error message says "id gpio", which can mislead debugging. Internal and GPIO source selection is implicit: a GPIO disables the matching internal detection flag. VBUS GPIO handling remuxes GPIO1 as VBUSDET before requesting the GPIO IRQ, so board pinmux assumptions matter. Some `palmas_read()`/`palmas_write()` calls ignore return codes in IRQ paths. GPIO ID detection does not set `linkstat`, which may matter if configurations change or if mixed paths are used.

## Test Signals
Validate ID grounded/float and VBUS high/low transitions for both internal and GPIO-backed configurations. Confirm cold-plug detection after probe, wakeup IRQ enable/disable during suspend/resume, GPIO debounce fallback when `gpiod_set_debounce()` fails, and correct extcon mutual behavior for USB and USB_HOST.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-palmas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-ptn5150.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-ptn5150.c

## Purpose
NXP PTN5150 USB Type-C CC logic driver that reports extcon USB/USB_HOST state and also drives Type-C orientation and USB role-switch integration. It handles attach/detach interrupts from an I2C CC controller and optionally drives a VBUS GPIO.

## Important APIs, Types, and Functions
`struct ptn5150_info` holds extcon, I2C/regmap, optional INT/VBUS GPIOs, IRQ work, mutex, `typec_switch`, and `usb_role_switch`. `ptn5150_check_state()` reads `PTN5150_REG_CC_STATUS`, derives orientation, attachment role, VBUS detection, extcon state, VBUS GPIO output, and USB role. `ptn5150_irq_work()` clears interrupt status, calls `ptn5150_check_state()` for attach, and resets extcon, VBUS, USB role, and orientation for detach. `ptn5150_init_dev_type()` reads device ID and clears stale interrupts. Probe wires GPIOs/IRQ, extcon properties, Type-C switch, role switch, cleanup action, and initial state.

## Control Flow
Probe requires a DT node, gets optional `vbus` output GPIO and either an I2C IRQ or `int` GPIO IRQ, registers a falling-edge threaded IRQ, allocates extcon, declares VBUS and polarity capabilities, clears stale interrupts, resolves the optional `connector` child to an orientation switch, resolves a USB role switch, installs a cleanup action, and then calls `ptn5150_check_state()` under the mutex for cold-plug state. The IRQ top-level handler schedules work. Work reads interrupt status; any attach bit triggers full CC-state classification, while non-attach interrupt status is treated as detach cleanup.

## State and Persistence
State is intentionally mostly hardware-derived. The driver does not cache the last role except through extcon/typec/role-switch frameworks. Work is serialized by `mutex`. The cleanup action cancels pending work and releases role/orientation switches. Hardware interrupt status registers clear on read.

## Dependencies and Integration Points
Uses regmap over I2C, GPIO descriptors, extcon provider properties, USB role switch, Type-C mux/switch APIs, OF fwnodes, and devm cleanup. The optional connector child can supply both orientation and role switch references.

## Risks
`gpiod_set_value_cansleep(info->vbus_gpiod, ...)` is called even when the VBUS GPIO is absent and set to NULL, which is only safe if the GPIO helper tolerates NULL for this API on the target kernel. Role/orientation switch acquisition is mandatory once attempted; missing role switch can fail probe. Detach handling treats any interrupt status without attach bit as detach, so unrecognized interrupt bits clear the connection. Error returns from `usb_role_switch_set_role()` and `typec_switch_set()` are logged but extcon state may already have changed.

## Test Signals
Exercise CC1 and CC2 orientation, DFP-attached device mode, UFP-attached host mode, detach cleanup, absent and present VBUS GPIO, I2C IRQ versus INT GPIO path, role switch failures, orientation switch failures, and resume scheduling a pending interrupt check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-ptn5150.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-qcom-spmi-misc.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-qcom-spmi-misc.c

## Purpose
Qualcomm PM8941 SPMI MISC extcon provider for USB ID and VBUS detection. It is based on GPIO-style extcon logic but reads IRQ line levels through irqchip state rather than GPIO descriptors.

## Important APIs, Types, and Functions
`struct qcom_usb_extcon_info` contains extcon, optional ID/VBUS IRQs, debounce delay, and delayed detection work. `qcom_usb_extcon_detect_cable()` calls `irq_get_irqchip_state(..., IRQCHIP_STATE_LINE_LEVEL, ...)` for `usb_id` and `usb_vbus` IRQs, sets SuperSpeed properties when active, and publishes USB_HOST/USB states. `qcom_usb_irq_handler()` queues the debounce work. Probe allocates extcon, enables SuperSpeed property capability, obtains named optional IRQs, requests handlers, validates at least one source, initializes wakeup, and performs initial detection.

## Control Flow
After probe, each ID or VBUS edge queues one delayed work item after 5 ms. The worker independently samples line level for each configured IRQ. ID low means host and sets `EXTCON_USB_HOST`; VBUS high means peripheral and sets `EXTCON_USB`. Initial detection calls the worker body directly. Suspend/resume enable and disable wake on the configured IRQs if the device may wake the system.

## State and Persistence
No cached cable state is maintained. Every report is derived from current irqchip line levels. The extcon framework stores last published state/properties. There is no hardware register programming beyond IRQ wake toggling.

## Dependencies and Integration Points
Depends on platform IRQ resources named `usb_id` and/or `usb_vbus`, irqchip line-level support, extcon provider APIs, devm delayed work autocancel, and PM wakeup. Device matching is `qcom,pm8941-misc`.

## Risks
If the IRQ controller does not support line-level state queries, detection silently returns early. The worker returns immediately on the first failed source, so one broken IRQ can suppress the other source update. SuperSpeed properties are only set true on active states and are not explicitly cleared. Suspend/resume return only the last wake operation result, potentially hiding an earlier failure.

## Test Signals
Validate named IRQ discovery, line-level polarity for ID low and VBUS high, initial detection, debounce behavior, wake IRQ enable/disable, behavior with only one source configured, and failure injection for `irq_get_irqchip_state()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-qcom-spmi-misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-rt8973a.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-rt8973a.c

## Purpose
Richtek RT8973A MUIC extcon provider for USB switch, OTG, charger, and JIG detection over I2C. It programs default MUIC control registers, registers a regmap IRQ chip, classifies ADC/DEV1 values, switches DM/DP routing, and publishes USB, USB host, DCP, SDP, and JIG states.

## Important APIs, Types, and Functions
`struct rt8973a_muic_info` owns I2C/regmap, regmap IRQ data, IRQ flags, register initialization table, auto-config flag, mutex, extcon, and delayed cold-plug work. `rt8973a_muic_set_path()` writes `RT8973A_REG_MANUAL_SW1` unless auto-config mode is enabled. `rt8973a_muic_get_cable_type()` reads ADC and DEV1 to disambiguate USB and TA when ADC is open. `rt8973a_muic_cable_handler()` handles attach, detach, OVP, and OTP events, maps cable types to extcon IDs and switch routes, and updates extcon. `rt8973a_init_dev_type()` logs version/vendor, writes initialization data, and detects auto-configuration mode.

## Control Flow
Probe requires OF, allocates state, initializes regmap, adds a two-register regmap IRQ chip, maps/request all logical IRQs, registers extcon, schedules delayed attach detection, and initializes hardware. IRQ handlers map virtual IRQs to logical RT8973A interrupts, set one of `irq_attach`, `irq_detach`, `irq_ovp`, or `irq_otp`, and schedule work. Work serializes under mutex and calls the cable handler for each pending event. Detach/OVP/OTP reuse the previous cable type, while attach reads ADC/DEV1 live.

## State and Persistence
Hardware setup persists in CONTROL1 and MANUAL_SW1. `auto_config` suppresses manual path writes when hardware auto switching is enabled. IRQ flags are per-device fields, but `prev_cable_type` inside `rt8973a_muic_cable_handler()` is a function-static variable shared by all driver instances. That is persistent for the module lifetime and not per device.

## Dependencies and Integration Points
Uses extcon provider, I2C, regmap, regmap IRQ, threaded IRQs, OF match, and PM wake IRQ toggling. Register constants come from `extcon-rt8973a.h`.

## Risks
The function-static `prev_cable_type` can cross-contaminate detach state if more than one RT8973A exists. Probe error paths after `regmap_add_irq_chip()` do not remove the IRQ chip unless remove later runs, so failures during virtual IRQ/extcon registration may leak IRQ-chip setup. Delayed work is not explicitly canceled in remove. Many accessory classes are logged and ignored, so consumer expectations must match the limited extcon set. OVP/OTP forcibly detach the previous extcon state but do not publish a separate fault signal.

## Test Signals
Test ADC OTG, TA, USB via DEV1, JIG USB/UART, open/no cable, attach/detach ordering, OVP/OTP forced detach, auto-config enabled and disabled, suspend/resume wake IRQs, failed ADC/DEV1 reads, and multiple-instance behavior if supported by the platform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-rt8973a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-rt8973a.h -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-rt8973a.h

## Purpose
Private register and bitfield contract for the RT8973A MUIC extcon driver. It defines the register address map, device ID masks, control bits, interrupt IDs/masks, ADC/DEV classification helpers, manual switch encodings, and reset bits used by `extcon-rt8973a.c`.

## Important APIs, Types, and Functions
`enum rt8973a_types` supplies I2C match data. `enum rt8973A_reg` defines registers from `DEVICE_ID` through `RESET` and `RT8973A_REG_END`. Control masks include interrupt mask, auto-config, I2C reset, switch-open, charger type, USB charger detection, and ADC enable. DEV1/DEV2 masks distinguish OTG, SDP, UART, car kit, CDP, DCP, and JIG states. Manual switch macros build DM/DP open, USB, and UART values. `enum rt8973a_irq` and `RT8973A_INT*` masks define regmap IRQ layout.

## Control Flow
The header has no executable flow. Its constants drive regmap max register validation, regmap IRQ chip indexing, hardware initialization masks, ADC/DEV1 classification, and manual switch writes in the C file.

## State and Persistence
No state is stored in the header. The macros describe persistent device register fields. Manual switch values and reset masks directly affect hardware routing when written by the driver.

## Dependencies and Integration Points
Requires Linux `BIT()` macro availability through the including C file's kernel headers. It is tightly coupled to the RT8973A datasheet and to the driver's `regmap_irq` array ordering.

## Risks
Several interrupt-mask macros use `RT9873A` spelling while the rest of the driver uses `RT8973A`; these are not referenced by the C file's regmap IRQ table but could confuse future maintenance. `RT8973A_INT2_UVLOT_MASK` includes an extra `T` compared with the enum name `UVLO`, and the C file uses that spelling. Bitfield definitions are raw shifts/masks with no type checking.

## Test Signals
Compile coverage is the main signal: all enum values and masks must match the C file. Hardware validation should confirm DEV1 USB/DCP masks, manual switch encodings, interrupt mask positions, and reset behavior against the RT8973A datasheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-rt8973a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-rtk-type-c.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-rtk-type-c.c

## Purpose
Realtek SoC USB Type-C extcon and Type-C port driver for RTD1295/1312C/1315E/1319/1319D/1395/1619/1619B families. It programs memory-mapped CC detection thresholds, alternates between host/device detection, publishes USB/USB_HOST extcon states with VBUS/polarity/SuperSpeed properties, and optionally registers a Type-C port for data/power role updates.

## Important APIs, Types, and Functions
`struct cc_param` and `struct type_c_cfg` hold per-SoC calibration and DFP mode choices. `struct type_c_data` owns MMIO base, extcon, IRQ, optional Kylin RD GPIO, calculated CC code/vref/debounce values, state machine fields, spinlock, delayed work, debugfs directory, and Type-C port. `setup_type_c_parameter()` applies defaults or NVMEM efuse calibration, then encodes CC code/vref registers. `extcon_rtk_type_c_init()` writes parameters, sets initial device-detection mode, schedules detection, and registers the Type-C port from a `connector` child. `detect_type_c_state()`, `host_device_switch()`, and `type_c_detect_irq()` implement the attach/detach state machine. `switch_type_c_dr_mode()` publishes extcon and Type-C role state.

## Control Flow
Probe maps MMIO, parses IRQ, requests a shared IRQ, initializes the spinlock, optionally gets Kylin `realtek,rd-ctrl-gpios`, copies matched SoC config, applies NVMEM calibration, initializes delayed work, initializes the controller, stores driver data, registers extcon, and creates debugfs files. The delayed work alternates between host and device detection when no connection change is found. IRQ handling calls `detect_type_c_state()`, clears interrupt status when a change is found, and schedules immediate delayed work. Attach calls cancel delayed scanning, publish host/device extcon and Type-C roles, and re-enable CC interrupts. Detach disables CC interrupts, clears extcon state, and resumes scanning.

## State and Persistence
Hardware state persists in CC control/vref/debounce registers. Software state under `spinlock_t lock` includes current mode (`IN_HOST_MODE` or `IN_DEVICE_MODE`), attach state, selected CC pin, last interrupt/status registers, and pending connection-change flag. Calibration mutates a per-device copy of the matched config with efuse deltas or replacements. Debugfs exposes current parameters and status when enabled.

## Dependencies and Integration Points
Uses MMIO, OF match data, OF IRQ mapping, extcon provider, Type-C class, NVMEM cells (`usb-cal` or `usb-type-c-cal`), SoC family matching, GPIO descriptors, delayed work, spinlocks, debugfs under `usb_debug_root`, and PM prepare/resume hooks. Match data supplies per-SoC CC parameter tables.

## Risks
`devm_request_irq()` is paired with manual `free_irq()` in remove, which can double-free because devm will also release it. Probe calls `extcon_rtk_type_c_init()` before `extcon_rtk_type_c_edev_register()`, but the delayed work scheduled by init can call `switch_type_c_dr_mode()` and use `type_c->edev` before extcon registration. Some sleeps/delays occur around spinlock release/reacquire and `mdelay()` is used from interrupt context to debounce, increasing latency. `type_c_detect_irq()` uses a function-static `local_count`, shared across instances. The NVMEM v2 helper initializes `value_size = 0` and computes a zero-bit mask before later assignment; it is harmless before use but brittle. Several paths return without releasing `connector` fwnodes. The spelling `use_defalut_parameter` is consistent but error-prone for maintainers.

## Test Signals
Test each compatible table, efuse v1/v2 calibration and missing NVMEM fallback, host attach/detach on CC1/CC2, device attach/detach on CC1/CC2, role switching via Type-C `dr_set`, suspend prepare/resume reinitialization, debugfs parameter/status output, Kylin RD GPIO handling, and probe/remove under devres debugging to catch IRQ lifetime issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-rtk-type-c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-sm5502.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-sm5502.c

## Purpose
Silicon Mitus SM5502/SM5504/SM5703 MUIC extcon provider for USB switch, OTG, USB device, and DCP charger detection. It supports chip variants through per-type IRQ chips, initialization tables, and IRQ parsers, then reports USB, USB host, SDP, and DCP extcon states.

## Important APIs, Types, and Functions
`struct sm5502_muic_info` stores device, extcon, I2C/regmap, matched `sm5502_type`, regmap IRQ data, attach/detach flags, work, mutex, and delayed cold-plug work. `struct sm5502_type` selects IRQ descriptors, regmap IRQ chip, initialization data, OTG DEV_TYPE1 mask, and parse callback. `sm5502_muic_set_path()` writes manual DM/DP and VBUSIN switch fields. `sm5502_muic_get_cable_type()` reads ADC and DEV_TYPE1 to disambiguate OTG, USB, and TA. `sm5502_muic_cable_handler()` maps supported cable classes to switch settings and extcon states. Probe initializes regmap IRQ, requests virtual IRQs, registers extcon, schedules detection, and writes initialization registers.

## Control Flow
OF match data selects SM5502, SM5504, or SM5703 behavior. Probe sets up regmap and devm regmap IRQ chip, then maps each logical IRQ to a virtual IRQ and requests a threaded handler. The handler maps virtual IRQ to logical type, calls the variant parse function to set attach/detach flags, and schedules work. Work serializes under mutex and handles attach and detach by calling `sm5502_muic_cable_handler()`. The delayed worker runs after 17 seconds and handles initial attach state.

## State and Persistence
Variant initialization writes reset, control, and interrupt mask registers. Cable detach relies on a function-static `prev_cable_type` in `sm5502_muic_cable_handler()`, shared across all devices. Per-device state includes attach/detach booleans and the matched type table. No persistent storage exists outside hardware registers and extcon state.

## Dependencies and Integration Points
Uses extcon provider, I2C, regmap, devm regmap IRQ, threaded IRQs, OF match data, and PM wake IRQ toggling. Register constants and masks come from `extcon-sm5502.h`.

## Risks
The function-static previous cable type creates multi-instance risk. The initialization logic writes either `~val` or `val` depending on `invert`, and because writes are full-register writes, mask intent must be validated against hardware reset values. Unsupported ADC accessory classes are silently ignored after debug logs. Probe uses OF match data; pure I2C ID match data is present but the probe still requires an OF node and `device_get_match_data()`. Delayed work is not explicitly canceled in remove because there is no remove callback.

## Test Signals
Exercise SM5502 and SM5504 IRQ maps, USB SDP, DCP, ground/open OTG, detach after each supported attach, boot cold-plug, register initialization values, wake IRQ suspend/resume, and behavior when ADC/DEV_TYPE1 reads fail or when unsupported accessories are attached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-sm5502.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-sm5502.h -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-sm5502.h

## Purpose
Private register, bitfield, timing, device-type, switch, reset, and interrupt definitions for the SM5502-family MUIC extcon driver. It supports both SM5502-style and SM5504-style interrupt/control layouts.

## Important APIs, Types, and Functions
`enum sm5502_reg` maps the device register space through `SM5502_REG_END`. Control masks define interrupt masking, wait, manual switch, raw data, switch-open, and SM5504 charger/ADC enable bits. INTM and IRQ masks define two-register IRQ layouts for SM5502 and SM5504 variants. Timing constants encode key press, ADC detect, switch wait, and long-key windows. DEV_TYPE masks classify audio, USB SDP, UART, car kit, charger, DCP, OTG, JIG, PPD, TTY, and AV cable states. Manual switch macros encode VBUSIN and DM/DP routing. `enum sm5502_irq` and `enum sm5504_irq` define logical regmap IRQ indices.

## Control Flow
The header has no executable control flow. Its enum ordering must match the C file's `regmap_irq` arrays and variant IRQ descriptor arrays. Its switch and device-type macros are consumed by cable classification and hardware path programming.

## State and Persistence
No state is stored here. The constants describe persistent hardware register state when the C driver writes reset/control/mask/manual-switch registers.

## Dependencies and Integration Points
Requires kernel bit macros from the including C file. It is coupled to SM5502/SM5504 datasheet layouts and the variant data in `extcon-sm5502.c`.

## Risks
`SM5502_REG_DEV_TYPE1_AUDIO_TYPE1__MASK` appears to be named as audio type1 but uses the audio type2 shift, which is likely a naming typo and could mislead future users. Raw macros do not enforce field width or register variant. Full-register initialization in the C file makes these definitions sensitive to reset-value assumptions.

## Test Signals
Compile coverage, regmap IRQ event ordering, hardware validation of DEV_TYPE classification, manual VBUS/DM/DP switch routing, SM5502 versus SM5504 interrupt masks, and timing register programming if future code uses timing constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-sm5502.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-usb-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-usb-gpio.c

## Purpose
Generic USB extcon provider backed by optional ID and VBUS GPIOs. It reports peripheral state as `EXTCON_USB` and host state as `EXTCON_USB_HOST`, enforcing that host mode wins when ID is grounded.

## Important APIs, Types, and Functions
`struct usb_extcon_info` stores device, extcon, optional GPIO descriptors, IRQ numbers, debounce delay, and delayed detection work. `usb_extcon_detect_cable()` samples GPIOs, applies fallback semantics when only one signal exists, clears stale extcon states, and publishes host or device state. `usb_irq_handler()` queues debounce work. Probe obtains GPIOs, registers extcon, configures hardware debounce or software debounce fallback, requests GPIO IRQs, enables wakeup capability, and performs initial detection. Remove cancels delayed work and disables wakeup.

## Control Flow
Probe requires an OF node and at least one of `id` or `vbus` GPIO. If ID is absent, ID defaults high; if VBUS is absent, VBUS defaults to ID, allowing ID-only setups to distinguish no host versus host. IRQs are edge-triggered and queue the delayed worker. The worker first clears USB_HOST if ID high and clears USB if VBUS low, then sets USB_HOST when ID low, otherwise sets USB if VBUS high. Suspend enables IRQ wake when allowed or selects pinctrl sleep state; resume restores pinctrl, disables wake, and queues immediate detection.

## State and Persistence
No explicit cable cache exists; state is derived from current GPIO levels. `debounce_jiffies` is nonzero only when GPIO hardware debounce fails. Extcon stores published state. Pinctrl sleep/default states may persist across PM transitions.

## Dependencies and Integration Points
Uses GPIO descriptor APIs, extcon provider, platform/OF matching, IRQ APIs, delayed work, pinctrl PM helpers, and device wakeup. Compatible string is `linux,extcon-usb-gpio`; platform ID is `extcon-usb-gpio`.

## Risks
When both GPIOs exist, hardware debounce setup for VBUS only occurs if ID debounce succeeded because of `if (!ret && info->vbus_gpiod)`. If hardware debounce fails, software debounce is used, but only one shared delay is tracked. GPIO polarity is defined by descriptor flags in firmware; wrong polarity reverses role detection. Host and device state changes are split into multiple extcon sync calls, so observers may see transient clearing before setting.

## Test Signals
Test ID-only, VBUS-only, and both-GPIO configurations; ID low with VBUS high/low; ID high with VBUS high/low; hardware debounce success/failure; suspend/resume wake handling; pinctrl transitions; remove cancellation; and GPIO polarity from DT flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-usb-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-usbc-cros-ec.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-usbc-cros-ec.c

## Purpose
ChromeOS Embedded Controller USB-C extcon provider. It queries EC USB PD commands for a selected port and reports USB device, USB host, and DisplayPort extcon states with VBUS, polarity, SuperSpeed, and HPD properties.

## Important APIs, Types, and Functions
`struct cros_ec_extcon_info` stores device, extcon, port ID, EC device, notifier block, cached data role, power role, DP state, USB mux state, and power type. `cros_ec_pd_command()` allocates and transfers EC command buffers. Helper queries fetch power type, PD mux flags, current PD role/polarity, and number of ports. `extcon_cros_ec_detect_cable()` is the main state reconciliation function, mapping EC role/mux/power responses to extcon states and properties. `extcon_cros_ec_event()` handles EC host events. Probe validates port ID, registers extcon properties, registers the EC notifier, and performs initial detection.

## Control Flow
Probe reads `google,usb-port-id` or uses platform ID, queries EC port count, registers extcon, sets property capabilities, initializes cached state, registers a blocking notifier on `ec->event_notifier`, and forces initial detection. Runtime updates are notifier-driven: PD MCU or USB mux host events call detection. Detection first gets power type, then role/polarity; disconnected role returns `-ENOTCONN` and leaves data role none. If connected, it gets mux flags and derives DisplayPort, USB mux, and HPD. It suppresses UFP reporting for charger-only wall-wart types. If cached state changed or force is true, it updates all extcon states/properties and syncs USB, USB_HOST, and DP; HPD-only events can sync DP without role changes.

## State and Persistence
Cached fields in `cros_ec_extcon_info` prevent redundant extcon updates and allow HPD-only handling. All durable connection truth comes from EC command responses. No hardware registers are directly programmed by this driver.

## Dependencies and Integration Points
Uses ChromeOS EC protocol commands (`EC_CMD_USB_PD_*`), EC event notifier, extcon provider, OF, platform device core, and USB PD command structures. It integrates with consumers through extcon and with EC transport through `cros_ec_cmd_xfer_status()`.

## Risks
The wall-wart classifier has a FIXME noting some USB-C chargers are intentionally miscategorized to avoid breaking cables/peripherals. PD mux query failure falls back to USB enabled, which may over-report SuperSpeed. EC command allocation occurs on each detection. If initial detection fails after notifier registration, probe unregisters correctly; runtime detection errors just log and keep previous extcon state. Polarity properties are updated even for DP and both USB roles during state changes.

## Test Signals
Test disconnected, DFP, UFP, charger-only, DP alt mode, USB mux on/off, HPD IRQ-only, EC command failures, invalid port IDs, notifier unregister on remove, and resume forced detection. Extcon property checks should include VBUS, Type-C polarity, USB_SS, and DP HPD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-usbc-cros-ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-usbc-tusb320.c -->
# sources/distributed-fs/ceph-client/drivers/extcon/extcon-usbc-tusb320.c

## Purpose
TI TUSB320/TUSB320L USB Type-C CC controller driver with extcon output and optional Type-C class/USB role-switch integration. It verifies the chip signature, reports USB device/host state and polarity, optionally registers a Type-C port, and supports changing advertised port type/current mode.

## Important APIs, Types, and Functions
`struct tusb320_priv` owns regmap, extcon, variant ops, current attached state, optional Type-C port/capability, port type, power opmode, connector fwnode, and role switch. `tusb320_check_signature()` validates the register signature. Variant ops provide `set_mode()` and optional revision read; TUSB320L disables CC termination while changing mode. `tusb320_extcon_irq_handler()` maps REG9 attached state to extcon USB/USB_HOST and polarity. `tusb320_typec_irq_handler()` reads REG8/REG9, updates Type-C orientation, roles, mode/accessory, role switch, and power opmode. `tusb320_state_update_handler()` reads REG9, filters interrupt status unless forced, runs handlers, and clears interrupt status by writing REG9.

## Control Flow
Probe allocates state, creates I2C regmap, checks signature, selects variant ops from OF match data, optionally reads revision, registers extcon and optional Type-C port from a `connector` child, forces initial state update, resets the chip, forces another state update, determines IRQ trigger type, and requests a threaded IRQ. Runtime IRQs call `tusb320_state_update_handler(false)`. Type-C port operations call `tusb320_port_type_set()`, which maps source/sink/DRP/default requests to hardware mode writes. Remove unregisters Type-C resources.

## State and Persistence
`priv->state` caches current attached state and prevents mode changes while attached. Hardware mode, advertised current, reset, interrupt status, and CC state live in registers. Optional Type-C and role-switch frameworks cache their own last reported roles. Extcon state persists until changed by later IRQ/forced update.

## Dependencies and Integration Points
Uses I2C regmap, extcon provider properties, Type-C class, USB role switch, OF match data for `ti,tusb320` and `ti,tusb320l`, IRQ trigger metadata, and Type-C connector firmware properties such as `typec-power-opmode`.

## Risks
`tusb320_typec_remove()` unconditionally calls `usb_role_switch_put()`, `typec_unregister_port()`, and `fwnode_handle_put()` even when no connector was present; safety depends on those helpers tolerating NULL. If `devm_request_threaded_irq()` fails after Type-C probe, resources are manually removed, but devm extcon/regmap remain. Reset after initial state can change state, hence the second forced update is required. Accessory role handling makes best-effort guesses for debug accessories. Mode changes return `-EBUSY` when attached, which callers must handle.

## Test Signals
Validate signature mismatch, TUSB320 versus TUSB320L mode-setting paths, revision read, initial forced updates before and after reset, REG9 interrupt filtering, CC1/CC2 polarity, DFP/UFP/accessory states, Type-C connector absent/present, advertised current from firmware, role-switch updates, and IRQ trigger type inheritance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon-usbc-tusb320.c -->
