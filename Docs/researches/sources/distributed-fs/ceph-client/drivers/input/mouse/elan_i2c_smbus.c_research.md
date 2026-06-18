# sources/distributed-fs/ceph-client/drivers/input/mouse/elan_i2c_smbus.c

## Purpose

`elan_i2c_smbus.c` is the SMBus transport backend for the Elan touchpad core. It implements the same `elan_transport_ops` contract as the native I2C backend using SMBus byte/block commands, including hello-packet initialization, mode/calibration/baseline/version/geometry queries, IAP firmware update preparation and page writes, packet reads, and SMBus-specific report feature selection.

## Important APIs, Types, and Functions

Core entry points are the functions installed into `elan_smbus_ops`: `elan_smbus_initialize`, `elan_smbus_sleep_control`, `elan_smbus_power_control`, `elan_smbus_set_mode`, `elan_smbus_calibrate`, `elan_smbus_calibrate_result`, `elan_smbus_get_baseline_data`, version/product/checksum/geometry helpers, `elan_smbus_iap_get_mode`, `elan_smbus_iap_reset`, `elan_smbus_prepare_fw_update`, `elan_smbus_write_fw_block`, `elan_smbus_finish_fw_update`, `elan_smbus_get_report_features`, `elan_smbus_get_report`, and `elan_smbus_get_pattern`.

## Control Flow

Initialization reads a five-byte hello packet of all `0x55` values and sends the enable-touchpad byte. Mode and calibration are written as small command blocks to `ETP_SMBUS_IAP_CMD`. Query helpers read block data from command IDs and decode big-endian or packed fields into core state. Firmware update enters IAP from main mode by setting the flash key, writing and verifying the SMBus IAP password, waiting for mode switch, setting the flash key again, and resetting. Each firmware page is split into two SMBus block writes because SMBus blocks are limited to 32 bytes, then IAP status bits are checked. Report reads place block data at offset 2 so the resulting buffer matches the shared report ID offsets expected by the core.

## State and Persistence Behavior

The backend stores no transport-private state. It mutates device mode, sleep state, IAP mode, and flash contents. `power_control`, `finish_fw_update`, and `get_pattern` are no-ops or fixed-value implementations because the SMBus protocol path does not expose the corresponding native I2C behavior.

## Dependencies and Integration Points

It depends on SMBus byte/block/I2C-block functionality selected in `elan_probe`, constants from `elan_i2c.h`, and Linux I2C SMBus helpers. Its buffer layout is intentionally coupled to the core ISR offsets.

## Risks and Edge Cases

SMBus page writes split by `fw_page_size / 2`; this only works for page sizes that fit the two-block protocol and may not support newer larger page modes. `elan_smbus_get_checksum` appears to choose the firmware checksum command when `iap` is true and IAP checksum when false, the reverse of the naming pattern used by I2C, so update verification should be treated carefully. `sleep_control(false)` and `power_control` are no-ops, which shifts wake behavior to initialization/enabling. Report length can shrink for `ETP_TP_REPORT_ID2` after reading the report ID.

## Test Signals

Tests should cover hello-packet validation, enable command errors, all block query length checks, packed range/resolution/trace decoding, calibration result copy bounds, IAP password write/read verification, main-to-IAP transition, page split writes and IAP error bits, checksum-command behavior, report offset compatibility with the core, trackpoint short-report handling, fixed pattern zero behavior, and parity with native I2C ops required by `struct elan_transport_ops`.
