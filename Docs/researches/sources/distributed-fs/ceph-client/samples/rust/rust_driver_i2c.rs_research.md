# sources/distributed-fs/ceph-client/samples/rust/rust_driver_i2c.rs

## Purpose

This Rust sample is a basic I2C client driver with OF, ACPI, and traditional I2C id-table matching.

## Important APIs, Types, and Functions

It uses `acpi_device_table!`, `i2c_device_table!`, `of_device_table!`, implements `i2c::Driver` for `SampleDriver`, and registers via `module_i2c_driver!`. The callbacks are `probe()`, `shutdown()`, and `unbind()`.

## Control Flow

Matching can occur through ACPI HID `LNUXBEEF`, I2C name `rust_driver_i2c`, or OF compatible `test,rust_driver_i2c`. Probe logs the device and optional id info, returns a zero-sized driver instance, and later shutdown/unbind log lifecycle events.

## State and Persistence Behavior

The driver instance carries no private state. Device lifecycle state is managed by the I2C core.

## Dependencies and Integration Points

It depends on built-in I2C core support (`I2C=y`) and integrates with the three firmware/device-id matching paths.

## Risks and Edge Cases

Because it is stateless, it does not validate adapter functionality or communicate with hardware. It is useful for binding/lifecycle tests, not device protocol tests.

## Test Signals

Instantiate a matching I2C client, load the module, and verify probe, shutdown, and unbind logs.
