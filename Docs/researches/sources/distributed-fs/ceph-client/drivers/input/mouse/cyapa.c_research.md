# sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa.c

## Purpose

`cyapa.c` is the bus/core driver for Cypress APA I2C/SMBus trackpads. It handles adapter detection, regulator power, device state discovery across Gen3/Gen5/Gen6 protocols, input device creation, IRQ dispatch, runtime/system power management, sysfs controls, and firmware update orchestration while delegating generation-specific protocol operations to `cyapa_gen3_ops`, `cyapa_gen5_ops`, and `cyapa_gen6_ops`.

## Important APIs, Types, and Functions

Externally visible helpers include `cyapa_is_pip_bl_mode()`, `cyapa_is_pip_app_mode()`, `cyapa_poll_state()`, `cyapa_sleep_time_to_pwr_cmd()`, and `cyapa_pwr_cmd_to_sleep_time()`. Internal state flow centers on `cyapa_get_state()`, `cyapa_check_is_operational()`, `cyapa_detect()`, `cyapa_initialize()`, and `cyapa_reinitialize()`. Input lifecycle is handled by `cyapa_create_input_dev()`, `cyapa_open()`, and `cyapa_close()`. IRQ and command coordination uses `cyapa_irq()`, `cyapa_enable_irq_for_cmd()`, and `cyapa_disable_irq_for_cmd()`. Sysfs and firmware paths include `cyapa_firmware()`, `cyapa_update_fw_store()`, `cyapa_calibrate_store()`, `cyapa_show_baseline()`, and mode/version/product attributes.

## Control Flow

Probe verifies I2C or SMBus functionality, does a basic SMBus presence read, allocates `struct cyapa`, enables the `vcc` regulator with devm cleanup, initializes all generation command-state helpers, detects the trackpad, prepares wake/runtime sysfs controls, requests a threaded falling-edge IRQ, disables the IRQ until input open, and creates an input device immediately only if firmware is operational.

State detection reads three status bytes from register zero, retries with SMBus block command when needed, and asks Gen3, PIP, and old Gen5 parsers to classify the state. Operational check selects the generation ops table and runs `ops->operational_check()`. Opening the input device locks `state_sync_lock`, sets full-active power or reinitializes, enables IRQ, enables runtime PM, and schedules autosuspend. The threaded IRQ first lets command-response handling consume interrupts; if it is a data interrupt and the device is operational, it calls the generation `irq_handler()`, bumps runtime PM, and attempts reinitialize on errors.

Firmware update sysfs unregisters the input device, locks state, requests firmware, validates it through the active ops table, resumes/powers the device, enables IRQ for command completion, enters/activates/initiates bootloader, writes firmware, then reinitializes and recreates input state if possible.

## State and Persistence Behavior

`struct cyapa` persists as devm-managed client data. It stores current state/gen, bootloader status bytes, operational flag, regulator/client/input pointers, power-mode policy for suspend and runtime suspend, cached product/firmware/platform/capability data, geometry, Gen5/Gen6 electrode data, `state_sync_lock`, ops pointer, and union command states. Sysfs writes persist only in memory as suspend/runtime scanrate settings. Firmware update persists to the device flash through generation-specific ops.

## Dependencies and Integration Points

The file depends on I2C/SMBus APIs, Linux input MT, IRQ threading, regulators, firmware loader, sysfs attribute groups, runtime PM, ACPI/OF matching, and generation-specific cyapa protocol files. `cyapa.h` defines shared constants, state, ops, and command prototypes. Userspace integration appears through input events and sysfs attributes `firmware_version`, `product_id`, `update_fw`, `baseline`, `calibrate`, `mode`, and power scanrate controls.

## Risks and Edge Cases

`cyapa_suspend()` and `cyapa_resume()` dereference `cyapa->input`; probe can leave `input` NULL when firmware is non-operational, so suspend/resume on a bootloader-only device needs scrutiny. State detection has several protocol fallbacks and retries; incorrect adapter capability or even/odd address handling can misclassify devices. Firmware update unregisters the input device before taking the state lock, so input users, PM, and sysfs sequencing are sensitive. IRQ handling must distinguish command responses from touch reports; losing this distinction can drop command completions or report stale data. Runtime scanrate update calls `pm_runtime_get_sync()` before taking the state lock and may return early on lock interruption without a matching put. Regulator disable is devm-managed, so all probe failure paths after enabling rely on action cleanup.

## Test Signals

Tests should cover I2C-only, SMBus-only, and combined adapters; Gen3/Gen5/Gen6 state parse paths; bootloader busy/idle/active and app modes; operational input registration; open/close IRQ and PM transitions; threaded IRQ command-response versus data events; firmware update success and each bootloader step failure; sysfs scanrate parsing including `buttononly`, `off`, and numeric values; baseline/calibrate when non-operational; suspend/resume with and without wakeup; runtime suspend/resume; and probe where the device is detected but not operational.
