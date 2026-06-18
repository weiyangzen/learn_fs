# sources/distributed-fs/ceph-client/samples/rust/rust_i2c_client.rs

## Purpose

This Rust platform driver sample demonstrates manually registering a new I2C client from a parent platform device.

## Important APIs, Types, and Functions

It uses platform OF/ACPI match tables, `i2c::I2cAdapter::get`, `i2c::I2cBoardInfo`, `i2c::Registration`, `Devres`, `ARef<platform::Device>`, and `module_platform_driver!`. Constants define adapter index `0`, client address `0x30`, and board name `rust_driver_i2c`.

## Control Flow

When the parent platform device probes, the driver gets adapter 0 and creates an I2C client registration using the board info and parent device. The registration is stored in devres-backed state. `unbind()` logs lifecycle shutdown.

## State and Persistence Behavior

State is the parent device reference plus devres-managed I2C client registration. The registered child client persists until the platform driver instance is unbound.

## Dependencies and Integration Points

It depends on platform bus, OF/ACPI matching, built-in I2C, and an existing adapter 0. It pairs naturally with `rust_driver_i2c.rs`, whose id table can bind to the created client.

## Risks and Edge Cases

Hard-coding adapter 0 is fragile on real systems. If no adapter exists or address `0x30` conflicts, probe fails. The comments reference `rust_driver_platform` in a verification snippet, which appears copied and should not be treated as the module name.

## Test Signals

Load with a matching platform device and I2C adapter 0; verify the I2C client appears and can bind to the Rust I2C driver sample.
