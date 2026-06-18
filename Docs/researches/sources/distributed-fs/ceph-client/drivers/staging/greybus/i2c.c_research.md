# sources/distributed-fs/ceph-client/drivers/staging/greybus/i2c.c

## Purpose
Greybus I2C bridged-PHY child driver. It exposes a remote Greybus I2C controller as a Linux `i2c_adapter`.

## Important APIs, Types, And Functions
`struct gb_i2c_device` holds the connection, gbphy device, functionality bits, and adapter. `gb_i2c_device_setup()` queries remote functionality. `gb_i2c_operation_create()` converts Linux `i2c_msg` arrays into one Greybus transfer operation with descriptors followed by outbound data. `gb_i2c_decode_response()` copies inbound data back to read messages. Adapter callbacks are `gb_i2c_master_xfer()` and `gb_i2c_functionality()`.

## Control Flow
Probe creates/enables the CPort connection, queries functionality, initializes adapter metadata and algorithm, registers the adapter, and releases the gbphy runtime-PM reference. Transfers allocate a Greybus operation sized for all message descriptors, write data, and read response data; runtime PM is held while the operation is sent. Expected transfer errors `-EAGAIN` and `-ENODEV` are not logged as hard errors.

## State And Persistence
Only functionality bits and adapter registration persist while the device is bound. Transfers are transient and do not cache remote bus state.

## Dependencies And Integration Points
Uses `gbphy`, Greybus I2C protocol, Linux I2C core, and runtime PM. The adapter is parented to the `gbphy_device`.

## Risks
Request/response sizes are derived from Linux message lengths; overflow and operation-size limits are important to preserve. The flag/functionality mapping currently assumes Greybus and Linux bit values match. Adapter removal must happen before disabling/destroying the connection.

## Test Signals
Test functionality query, mixed read/write transfers, zero-message and large-message boundaries, `msg_count > U16_MAX`, expected and unexpected transfer errors, adapter registration failure, and PM failure during transfer.
