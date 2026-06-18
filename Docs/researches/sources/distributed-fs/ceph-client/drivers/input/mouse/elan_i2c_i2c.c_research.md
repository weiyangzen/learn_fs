# sources/distributed-fs/ceph-client/drivers/input/mouse/elan_i2c_i2c.c

## Purpose

`elan_i2c_i2c.c` is the native I2C transport backend for the Elan touchpad core. It implements register-command reads/writes, reset and descriptor reads, sleep/power/mode control, calibration and baseline queries, firmware/product/geometry queries, IAP firmware update operations, report feature selection, and full report reads for `elan_i2c_ops`.

## Important APIs, Types, and Functions

Low-level helpers are `elan_i2c_read_block`, `elan_i2c_read_cmd`, and `elan_i2c_write_cmd`. Initialization/control helpers include `elan_i2c_initialize`, `elan_i2c_sleep_control`, `elan_i2c_power_control`, `elan_i2c_set_mode`, `elan_i2c_calibrate`, and `elan_i2c_calibrate_result`. Query helpers include `elan_i2c_get_pattern`, `elan_i2c_get_version`, `elan_i2c_get_sm_version`, `elan_i2c_get_product_id`, `elan_i2c_get_checksum`, `elan_i2c_get_max`, `elan_i2c_get_resolution`, `elan_i2c_get_num_traces`, and `elan_i2c_get_pressure_adjustment`. IAP update helpers include `elan_i2c_iap_get_mode`, `elan_i2c_iap_reset`, `elan_i2c_prepare_fw_update`, `elan_i2c_write_fw_block`, and `elan_i2c_finish_fw_update`.

## Control Flow

Native I2C reads send a little-endian 16-bit register address followed by a read message. Initialization issues reset through the standard command register, consumes reset acknowledgement, then reads device and report descriptors. Firmware update checks/enters IAP mode, sets flash keys, optionally configures IAP page type for newer ICs, writes pages with register prefix plus checksum, polls IAP status bits, resets the device, waits on the IRQ completion, and drains the final interrupt signal. Normal report reads use `i2c_master_recv` for the report length selected from pattern.

## State and Persistence Behavior

The transport stores no private state; all persistent state is in core `elan_tp_data` and on the device. It changes hardware mode, power state, IAP page type, and flash contents through register writes. Pattern handling affects how firmware/IAP versions and report lengths are interpreted by the core.

## Dependencies and Integration Points

It depends on Linux I2C transfer APIs, unaligned endian helpers, completions supplied by the core, and constants/ops from `elan_i2c.h`. It is selected only when the adapter supports `I2C_FUNC_I2C`.

## Risks and Edge Cases

Several read helpers allocate 3-byte buffers for 2-byte reads, so callers must continue to interpret only the intended bytes. `elan_i2c_finish_fw_update` enables IRQ while the core-level update path is otherwise operating under disabled IRQ assumptions, so ordering with the completion is critical. Firmware signature bounds are checked in the core, not here. Pattern-specific version and IC-type parsing has separate old/new paths that can regress older firmware. Power control read-modify-write depends on the current register being readable while suspended.

## Test Signals

Tests should cover two-message I2C read errors, short transfers, reset descriptor sequence, old/new pattern parsing, IAP mode detection, IAP reset and password verification, 64/128/512-byte page programming, IAP status error bits, firmware reset completion timeout, report length selection for high-precision reports, pressure adjustment bit parsing, baseline/calibration commands, and integration with the core firmware update and IRQ completion paths.
