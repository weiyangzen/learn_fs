# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-versatile.c

## Purpose

`i2c-versatile.c` is a small bit-banged I2C adapter driver for ARM Versatile-compatible hardware. It manipulates SCL and SDA through simple MMIO set/clear/read registers and delegates protocol timing to `i2c-algo-bit`.

## Important APIs, Types, and Functions

`struct i2c_versatile` combines an adapter, bit-algorithm data, and MMIO base. `i2c_versatile_setsda()`, `setscl()`, `getsda()`, and `getscl()` implement the bit callbacks. `i2c_versatile_probe()` maps resources, releases both lines high, configures the adapter, and calls `i2c_bit_add_numbered_bus()`.

## Control Flow

The platform driver binds via `arm,versatile-i2c`. Probe allocates state, maps the MMIO resource, sets SCL/SDA high, copies static bit-algo parameters, sets the platform device ID as adapter number, and registers the numbered bit-banged bus. Removal deletes the adapter.

## State and Persistence Behavior

There is no software cache or saved hardware state. Line state is directly represented in controller bits. The static bit algorithm uses `udelay = 30` and `timeout = HZ`.

## Dependencies and Integration Points

The driver depends on platform devices, OF matching, MMIO, and `i2c-algo-bit`. It uses `subsys_initcall()` so the adapter is available early for board devices.

## Risks

All protocol correctness is delegated to bit-banging callbacks, so incorrect GPIO-like line semantics would break the bus. No PM hooks restore line state. Numbered bus registration tied to `dev->id` may fail if platform IDs collide or are unset unexpectedly.

## Test Signals

Check OF/platform binding, MMIO resource mapping, idle-high SCL/SDA after probe, adapter number assignment, simple reads/writes through `i2c-algo-bit`, clock stretching through `getscl()`, and adapter removal.
