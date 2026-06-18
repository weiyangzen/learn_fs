# `sources/distributed-fs/ceph-client/include/linux/usb/ljca.h`

## Purpose

`ljca.h` defines the client-facing API for Intel La Jolla Cove Adapter USB devices. LJCA exposes auxiliary child devices for GPIO, I2C, SPI, and event-driven functions, and this header describes client identity, auxiliary-device conversion, event callbacks, and command transfer helpers.

## Important APIs, Types, and Constants

- `LJCA_MAX_GPIO_NUM` fixes the GPIO bitmap capacity.
- `auxiliary_dev_to_ljca_client()` converts an auxiliary device to its enclosing `ljca_client`.
- `ljca_event_cb_t` is an interrupt-context callback receiving command ID and transient event payload.
- `struct ljca_client` stores client type/id, adapter link, `auxiliary_device`, adapter backpointer, callback context, callback pointer, and spinlock.
- `struct ljca_gpio_info`, `struct ljca_i2c_info`, and `struct ljca_spi_info` describe child-device capabilities.
- `ljca_register_event_cb()`, `ljca_unregister_event_cb()`, `ljca_transfer()`, and `ljca_transfer_noack()` are the exported client operations.

## Control Flow and Lifetimes

The parent LJCA USB driver discovers adapter functions and registers auxiliary devices. Child drivers obtain `ljca_client`, register optional event callbacks, issue synchronous command/response transfers with `ljca_transfer()`, or fire no-ack commands with `ljca_transfer_noack()`. Event payloads are valid only for the callback invocation, so clients must copy data they retain.

## State and Persistence Behavior

Client objects persist while the auxiliary device is registered. Callback state is protected by `event_cb_lock`. Transfer state and firmware responses are transient. No disk persistence exists.

## Dependencies and Integration Points

It depends on Linux auxiliary bus, lists, spinlocks, bitmaps, and fixed-width types. It integrates the LJCA USB adapter core with GPIO, I2C, SPI, and other auxiliary child drivers.

## Risks and Edge Cases

Callbacks run in interrupt context and cannot sleep. Event payload lifetime is short. Register/unregister must be synchronized with in-flight events to avoid callback-after-free. `ljca_transfer()` requires callers to size input buffers correctly because return value is the actual response length.

## Test Signals

Probe LJCA devices, bind GPIO/I2C/SPI auxiliary drivers, run synchronous and no-ack transfers, generate firmware events, unregister callbacks during event storms, test disconnect during transfer, and use lockdep for callback spinlock paths.
