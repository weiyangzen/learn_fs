
# sources/distributed-fs/ceph-client/drivers/power/supply/pm8916_bms_vm.c

## Purpose
This Qualcomm PM8916 VM-BMS driver exposes a simple battery power supply backed by the PMIC voltage-monitoring BMS block. It reports status, health, current battery voltage, and last open-circuit voltage while working around hardware state-machine limitations during suspend/resume.

## Important APIs, Types, and Functions
`struct pm8916_bms_vm_battery` stores the device, battery power supply, battery info, regmap/base register, last OCV/time, and current VBAT. Important functions are `pm8916_bms_vm_battery_probe()`, `pm8916_bms_vm_battery_get_property()`, `pm8916_bms_vm_fifo_update_done_irq()`, `pm8916_bms_vm_battery_suspend()`, and `pm8916_bms_vm_battery_resume()`.

## Control Flow
Probe gets the parent regmap and `reg` base, validates peripheral type, configures S1/S2 sample intervals and FIFO length, enables BMS, reads boot/resume OCV, registers the battery power supply, loads monitored-battery info, and requests the `fifo` IRQ. FIFO IRQ reads two voltage samples, uses the last sample as VBAT scaled by 300 uV units, then sends `power_supply_changed()`. Status is derived from `power_supply_am_i_supplied()`. Suspend unlocks secure access and forces S3 OCV/sleep mode; resume reads fresh OCV and returns hardware to normal mode.

## State and Persistence
`last_ocv` and `last_ocv_time` are cached in RAM and invalidated for property reads after 180 seconds. `vbat_now` is updated by FIFO IRQs. Battery design bounds come from `power_supply_get_battery_info()` and are used to derive health. No persistent storage is written.

## Dependencies and Integration Points
The file depends on Qualcomm SPMI/regmap peripheral layout, a `qcom,pm8916-bms-vm` DT node with `reg`, `monitored-battery`, a named `fifo` IRQ, power_supply supplier relationships, and platform suspend/resume callbacks.

## Risks and Test Signals
Risks include endian/width assumptions in `regmap_bulk_read()` into `u16`/`unsigned int`, stale OCV exposure, missing error handling after resume OCV read before using `tmp`, and health decisions when battery-info voltage fields are absent. Tests should validate peripheral type rejection, FIFO voltage scaling, OCV expiry, supplier-derived charging status, suspend/resume register writes, and IRQ-triggered uevents.
