# sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa_gen3.c

## Purpose

`cyapa_gen3.c` implements the Gen3 Cypress APA I2C/SMBus touchpad backend behind the common `cyapa_dev_ops` interface. It covers legacy register-map access, device-state detection, bootloader entry/exit, firmware validation and flashing, calibration/baseline sysfs handlers, power-mode transitions, IRQ filtering, and multitouch input reporting.

## Important APIs, Types, and Functions

Key device wire types are `struct cyapa_touch`, `struct cyapa_reg_data`, and `struct gen3_write_block_cmd`. Bus access is normalized through `cyapa_read_byte`, `cyapa_write_byte`, `cyapa_read_block`, `cyapa_i2c_reg_read_block`, and `cyapa_smbus_read_block`. Firmware update is split across `cyapa_gen3_check_fw`, `cyapa_gen3_bl_enter`, `cyapa_gen3_bl_activate`, `cyapa_gen3_write_fw_block`, `cyapa_gen3_do_fw_update`, `cyapa_gen3_bl_deactivate`, and `cyapa_gen3_bl_exit`. Runtime behavior is exposed through `cyapa_gen3_do_operational_check`, `cyapa_gen3_set_power_mode`, `cyapa_gen3_do_calibrate`, `cyapa_gen3_show_baseline`, `cyapa_gen3_irq_handler`, and the exported `cyapa_gen3_ops` table.

## Control Flow

State parsing inspects bootloader status bytes or operational status/data-valid bits to set `cyapa->gen` and `cyapa->state`. Operational check exits bootloader if needed, sets full-active power before querying product data, and rejects non-Gen3 or non-`CYTRA` devices. Firmware update verifies an exact 30,848-byte image and two checksums, writes all data blocks first, then header/checksum blocks, with each 64-byte flash block wrapped in a security-key command and polled until the bootloader is no longer busy. IRQ handling reads one complete `cyapa_reg_data`, validates status/data bits, then reports slots, pressure, and mechanical buttons.

## State and Persistence Behavior

Runtime state is stored in the shared `struct cyapa`: state, generation, firmware version, product ID, dimensions, button capability, max pressure, operational flag, and input device pointer. Firmware persists on the touchpad flash only through the bootloader update path. Power state is written into the device register and delayed according to the previous scan rate; during runtime PM, the handler opportunistically drains/report polls to avoid losing touch state while the command settles.

## Dependencies and Integration Points

This file depends on Linux I2C/SMBus helpers, input MT helpers, unaligned endian helpers, `cyapa.h` constants/helpers, and the common cyapa core that calls `cyapa_dev_ops`. It integrates with sysfs attributes supplied by the core, the firmware loader, and the Linux input subsystem.

## Risks and Edge Cases

SMBus block reads loop by 32-byte chunks and trust the encoded command class; wrong lengths become `-EIO`. Touch IDs are converted to slots by `id - 1` without a local range check. The firmware checksum error for image data logs "header checksum", which can mislead diagnostics. Bootloader timing uses long sleeps and fixed retry windows, so marginal hardware can produce `-EAGAIN` despite being recoverable. Proximity and some bootloader hooks are stubs returning unsupported/success by design.

## Test Signals

Useful coverage includes I2C and SMBus read/write paths, state parsing for OP/BL idle/active/busy/watchdog cases, firmware-size and checksum rejection, block-write timeout/error injection, bootloader enter/exit recovery, calibration timeout, baseline read, power-mode no-op and PM-poll paths, invalid packet rejection, slot/button reporting, and `cyapa_gen3_ops` signature/build coverage.
