# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-opal.c

## Purpose
Implements an IBM OPAL-backed I2C adapter for Power systems. Linux I2C and SMBus requests are converted into OPAL firmware asynchronous I2C requests instead of driving hardware registers directly.

## Important APIs, Types, And Functions
`i2c_opal_xfer()` implements raw I2C transfers for one-message or simple two-message operations. `i2c_opal_smbus_xfer()` maps supported SMBus operations to `struct opal_i2c_request`. `i2c_opal_send_request()` obtains an OPAL async token, submits the request, waits for completion, translates OPAL return codes, and releases the token. Probe registers an adapter using the `ibm,opal-id` property.

## Control Flow
Module init first checks `FW_FEATURE_OPAL`. Probe reads the firmware bus ID, allocates/configures an adapter, names it from `ibm,port-name` when available, and registers it. Transfers build big-endian OPAL request fields, pass physical buffer addresses through `__pa()`, and block until OPAL asynchronous completion.

## State And Persistence
Adapter state is minimal: the OPAL bus ID is stored in `adapter->algo_data`. OPAL firmware owns actual bus transaction state. The driver keeps no persistent local transaction state or durable data.

## Dependencies And Integration Points
Depends on Power firmware interfaces in `asm/opal.h`, OPAL async token APIs, OF platform devices compatible with `ibm,opal-i2c`, and the Linux I2C/SMBus core. Adapter quirks restrict two-message operations to write-first, same-address combined transfers with a first message length up to four bytes.

## Risks
Buffers are passed by physical address, so callers must provide memory suitable for OPAL access. Functionality is intentionally limited to simple raw and SMBus transactions. OPAL error translation is broad for unknown failures. Async-token acquisition can be interrupted. Firmware behavior is a major external dependency.

## Test Signals
Test on OPAL firmware with raw reads/writes, write-then-read register access, SMBus quick/byte/byte-data/word/I2C-block operations, OPAL NACK/timeout/arbitration error mapping, interrupted token acquisition, adapter naming from device tree, and module init refusal when OPAL is absent.
