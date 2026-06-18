# sources/distributed-fs/ceph-client/drivers/power/reset/tdx-ec-poweroff.c

## Purpose
Toradex SMARC embedded-controller I2C poweroff/restart driver.

## Important APIs, Types, and Functions
regmap config/access tables, `tdx_ec_cmd()`, poweroff/restart callbacks, registration helper, and I2C probe.

## Control Flow
probe initializes 8-bit I2C regmap, bulk-reads chip ID and firmware version, logs them, and registers firmware-priority restart and poweroff handlers; callbacks write command register and wait one second.

## State and Persistence Behavior
regmap is devm-managed; EC command register is volatile and consumed by controller firmware.

## Dependencies and Integration Points
I2C, regmap cache/access tables, OF compatible `toradex,smarc-ec`, sys-off API.

## Risks and Edge Cases
chip ID is logged but not validated against known constants; if firmware ignores command, kernel only warns after delay; read/write access tables must match EC firmware.

## Test Signals
I2C probe, ID/version read failures, command write failures, poweroff/restart on SMARC iMX8MP/iMX95, and timeout warning.
