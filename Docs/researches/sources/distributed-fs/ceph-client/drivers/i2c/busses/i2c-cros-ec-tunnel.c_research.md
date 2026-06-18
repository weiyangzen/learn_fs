# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cros-ec-tunnel.c

## Purpose
ChromeOS EC I2C tunnel adapter. It presents a local Linux `i2c_adapter` whose transfers are serialized into `EC_CMD_I2C_PASSTHRU` commands and executed by a parent ChromeOS embedded controller on a remote I2C bus.

## Important APIs, Types, And Functions
`struct ec_i2c_device` stores the device, adapter, parent `cros_ec_device`, remote bus number, and fixed request/response scratch buffers. Message sizing and marshaling are handled by `ec_i2c_count_message()`, `ec_i2c_construct_message()`, `ec_i2c_count_response()`, and `ec_i2c_parse_response()`. The adapter algorithm uses `ec_i2c_xfer()` and `ec_i2c_functionality()`. Probe/remove are `ec_i2c_probe()` and `ec_i2c_remove()`.

## Control Flow
Probe fetches the parent EC from the parent device, validates `cmd_xfer`, reads `google,remote-bus`, initializes adapter fields and ACPI companion data, then calls `i2c_add_adapter()`. A transfer computes request and response lengths, allocates a `struct cros_ec_command` plus payload, packs Linux `i2c_msg` entries into EC passthrough structures, sends via `cros_ec_cmd_xfer_status()`, parses EC status flags, and copies read data back into the original messages.

## State And Persistence
No hardware state is owned locally beyond adapter registration. Per-transfer state lives in the allocated EC command buffer. The configured `remote_bus` is read once at probe and retained in `struct ec_i2c_device`.

## Dependencies And Integration Points
Depends on ChromeOS EC protocol headers, `cros_ec_cmd_xfer_status()`, platform device binding, ACPI/OF matching, and the Linux I2C core. Match points are OF `google,cros-ec-i2c-tunnel`, ACPI `GOOG0012`, and platform alias `cros-ec-i2c-tunnel`.

## Risks
Ten-bit addresses are rejected. Request/response lengths are dynamically allocated but constructed from fixed EC protocol structure sizes; malformed EC responses can produce `-EPROTO`. Status mapping collapses EC timeout, NAK, and generic errors into standard Linux errors. Remote bus behavior and locking are delegated to EC firmware.

## Test Signals
Test probe deferral when parent EC is absent, missing `google,remote-bus`, normal write/read passthrough, readback copying for combined transactions, EC NAK to `-ENXIO`, EC timeout to `-ETIMEDOUT`, ten-bit rejection, and ACPI/OF adapter discovery.
