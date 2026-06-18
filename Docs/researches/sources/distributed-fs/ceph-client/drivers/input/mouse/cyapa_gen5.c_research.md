# sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa_gen5.c

## Purpose

`cyapa_gen5.c` implements the Cypress PIP transport and Gen5 device operations for cyapa touchpads. It provides shared PIP command serialization used by Gen5 and Gen6, PIP state detection, bootloader firmware update, power management, calibration, baseline diagnostics, proximity control, IRQ command response handling, and touch/button/proximity report decoding.

## Important APIs, Types, and Functions

Important packet structures include `cyapa_pip_touch_record`, `cyapa_pip_report_data`, `cyapa_tsg_bin_image_*`, `pip_bl_cmd_head`, `pip_app_cmd_head`, and parameter/retrieve command payloads. Public helpers used by Gen6 include `cyapa_pip_cmd_state_initialize`, `cyapa_i2c_pip_read`, `cyapa_i2c_pip_write`, `cyapa_empty_pip_output_data`, `cyapa_i2c_pip_cmd_irq_sync`, PIP response sorters, `cyapa_pip_bl_enter`, `cyapa_pip_bl_exit`, `cyapa_pip_check_fw`, `cyapa_pip_do_fw_update`, `cyapa_pip_deep_sleep`, `cyapa_pip_set_proximity`, `cyapa_pip_suspend_scanning`, `cyapa_pip_resume_scanning`, `cyapa_pip_do_calibrate`, `cyapa_pip_irq_cmd_handler`, and `cyapa_pip_irq_handler`. `cyapa_gen5_ops` binds these to the common driver.

## Control Flow

Initialization sets completions, command mutexes, PM-stage locks, response sort callbacks, and cached power/sleep state. Every PIP command takes `cmd_lock`, records the expected command code, optionally drains stale output data, writes an output report, then waits by IRQ completion or polling until the sorter finds the matching response. State parsing classifies idle buffers, HID descriptors, report descriptors, command responses, or touch/button reports into Gen5 app/bootloader states and always drains unread content afterward. Firmware update validates TSG image header/family/platform metadata, app-integrity CRC, row alignment, and app CRC; it initiates bootload with metadata, writes each row except the final integrity row, and validates bootloader acknowledgements. Runtime IRQs first give pending commands a chance to consume responses, then normal reports are parsed into MT slots, buttons, proximity distance, or runtime wake events.

## State and Persistence Behavior

Persistent driver state lives in `cyapa->cmd_states.pip`, cached device power/sleep values, product information, electrode geometry, platform version, origin flags, and input device state. Firmware writes persist in device flash through PIP bootloader commands. Baseline/IDAC scanning temporarily suspends scanning and resumes it even on most error paths.

## Dependencies and Integration Points

The code depends on Linux I2C master send/recv, completions, mutexes, atomics, PM runtime, CRC-ITU-T, input MT, and shared PIP constants/macros from `cyapa.h`. Gen6 directly reuses many non-static helpers from this file.

## Risks and Edge Cases

Command response matching depends on the global `in_progress_cmd`; malformed or interleaved responses must be drained carefully. `cyapa_empty_pip_output_data` has fixed report/empty-count limits and can return `-EINVAL` after draining unrelated reports. Baseline and panel-scan routines perform many command transactions while scanning is suspended, so resume failure masks or combines with the original error. Several response paths validate headers but trust payload offsets after minimum-length checks. Firmware parsing assumes the final flash record is row `0x01ff`.

## Test Signals

Tests should cover command serialization, IRQ and polling response paths, fallback polling after IRQ timeout, stale touch reports during commands, state parsing for HID/report/command data, bootloader enter/exit, TSG firmware validation failures, row-write errors, power transitions including deep sleep and button-only, proximity unsupported timeout mapping, calibration suspend/resume ordering, baseline data retrieval, touch liftoff and origin inversion, wake events, and invalid report lengths/IDs.
