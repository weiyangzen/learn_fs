# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-diolan-u2c.c

## Purpose
USB I2C adapter driver for Diolan U2C-12. It converts Linux I2C messages into the device firmware command protocol over USB bulk endpoints.

## Important APIs, Types, And Functions
`struct i2c_diolan_u2c` stores output/input command buffers, endpoint addresses, USB device/interface, adapter, and queued command counts. USB command helpers include `diolan_usb_transfer()`, `diolan_usb_cmd*()`, `diolan_i2c_start()`, `diolan_i2c_stop()`, byte ACK helpers, and speed/clock-sync configuration. I2C operations are `diolan_usb_xfer()` and `diolan_usb_func()`. USB binding uses `diolan_u2c_probe()` and `diolan_u2c_disconnect()`.

## Control Flow
Probe validates interface zero with at least two endpoints, allocates state, stores endpoints, initializes adapter data, runs `diolan_init()` to flush stale input, log firmware/serial, set speed, and configure clock stretching, then registers the adapter. Transfer queues a START, repeated starts for subsequent messages, sends address with ACK check, then writes bytes or reads bytes with ACK/NACK handling. It always attempts STOP on abort.

## State And Persistence
State is per USB interface. `frequency` is a module parameter and may be normalized during initialization. Command output buffering batches firmware commands until flush thresholds or explicit flush. No durable persistence exists.

## Dependencies And Integration Points
Depends on USB bulk messaging, Diolan firmware command IDs/responses, Linux I2C core, module parameter handling, and HWMON adapter class.

## Risks
Endpoint ordering is assumed from descriptors. Response handling maps address-phase NACK differently from later NACKs based on command index. SMBus block reads mutate `pmsg->len` after receiving a length byte. USB timeouts and stale device input can desynchronize command/response streams.

## Test Signals
Test USB probe/disconnect, firmware init, frequency parameter normalization, simple writes/reads, repeated-start combined messages, SMBus block reads, address NACK to `-ENXIO`, later NACK to `-EIO`, USB timeout, STOP-on-error, and input flush behavior.
