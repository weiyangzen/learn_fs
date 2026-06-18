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
