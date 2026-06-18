# sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa_gen6.c

## Purpose

`cyapa_gen6.c` adds Gen6-specific behavior on top of the shared Gen5 PIP command engine. It identifies Gen5 versus Gen6 PIP devices, reads Gen6-specific system information, implements Gen6 power/IRQ interval controls, wraps proximity changes with command-IRQ masking, exposes Gen6 baseline diagnostics, and registers `cyapa_gen6_ops`.

## Important APIs, Types, and Functions

Local wire structures are `pip_app_cmd_head`, `pip_app_resp_head`, `pip_fixed_info`, and the local interval-setting command. `cyapa_pip_state_parse` is the shared PIP generation detector. Gen6-specific helpers include `cyapa_get_pip_fixed_info`, `cyapa_gen6_read_sys_info`, `cyapa_gen6_bl_read_app_info`, `cyapa_gen6_config_dev_irq`, `cyapa_gen6_set_proximity`, `cyapa_gen6_change_power_state`, `cyapa_gen6_set_interval_setting`, `cyapa_gen6_get_interval_setting`, `cyapa_gen6_deep_sleep`, `cyapa_gen6_set_power_mode`, `cyapa_pip_retrieve_data_structure`, `cyapa_gen6_show_baseline`, and `cyapa_gen6_operational_check`.

## Control Flow

State parsing wakes from deep sleep, drains queued data, reads the HID descriptor, determines app versus bootloader mode, then reads fixed silicon/family identifiers either from bootloader info or app system info. Family `0x9B` with silicon-high `0x0B` maps to Gen6; family `0x91` with silicon-high `0x02` maps to Gen5. Operational check exits bootloader if possible, forces full-active power, enables proximity, reads system info, and validates the `CYTRA` product prefix. Power changes disable command IRQs around disruptive transitions, wake from deep sleep with a ping plus deep-sleep command, use Gen6 active/button-only/LP1/LP2 modes, and update cached low-power intervals as needed.

## State and Persistence Behavior

Gen6 stores geometry, firmware, platform, product ID, origin flags, button capability, Rx electrode count, aligned Rx count, cached PIP power/sleep state, and `gen6_interval_setting` in `struct cyapa`. Firmware persistence is delegated to the shared PIP bootloader helpers. Baseline diagnostics suspend scanning, retrieve RX attenuator/IDAC and attenuator trim structures, then resume scanning and clear the sysfs buffer on failure.

## Dependencies and Integration Points

This file depends heavily on non-static helpers from `cyapa_gen5.c`, including PIP command execution, response sorting, firmware validation/update, deep sleep, proximity, scan suspend/resume, calibration, and IRQ processing. It integrates with the same cyapa core `cyapa_dev_ops` table and Linux I2C/input infrastructure.

## Risks and Edge Cases

`cyapa_pip_state_parse` returns success even when fixed info does not match Gen5 or Gen6, leaving `state` as no-device for the caller to interpret. IRQ enable/disable errors are often ignored around proximity/power operations. Gen6 interval updates choose LP2 once LP1 is occupied, so later distinct sleep times overwrite LP2. The retrieve-data helper has a fixed response buffer sized for `GEN6_MAX_RX_NUM + 10`; larger firmware data structures return `-ENOBUFS` only if the response itself fit.

## Test Signals

Coverage should include Gen5/Gen6 detection in app and bootloader modes, fixed-info read failures, deep-sleep wake ping behavior, command IRQ mask/unmask sequencing, active/button-only/off/LP1/LP2 transitions, interval cache synchronization, proximity error propagation, bootloader app-info fallback, system-info offset parsing and validation, baseline retrieve-data success and `-ENOBUFS`, resume-after-baseline failure, and reuse of shared PIP firmware/calibration/IRQ handlers.
