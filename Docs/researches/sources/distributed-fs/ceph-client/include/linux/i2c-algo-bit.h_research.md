# sources/distributed-fs/ceph-client/include/linux/i2c-algo-bit.h

## Purpose
Defines the bit-banging I2C adapter algorithm contract for controllers implemented through GPIO-like SDA/SCL callbacks.

## APIs, Control Flow, and State
`struct i2c_algo_bit_data` stores private callback data, setters/getters for SDA/SCL, optional transfer prologue/epilogue, half-cycle delay, timeout, and a `can_do_atomic` flag for non-sleeping callbacks. Adapters attach the algorithm through `i2c_bit_add_bus()` or `i2c_bit_add_numbered_bus()`, and can reference the exported `i2c_bit_algo`. State resides in adapter `algo_data` and timing parameters; transfers are implemented by the bit algorithm using these callbacks.

## Dependencies, Integration, Risks, and Tests
Depends on core I2C adapter types. Integrates with GPIO/pinctrl-backed I2C adapters and any hardware that needs software clocking. Risks include callbacks that sleep despite `can_do_atomic`, invalid `udelay` for SMBus/I2C timing, missing SCL reads for clock stretching, and bus hangs without proper timeout/recovery. Test signals include I2C transfer vectors, SMBus timing checks, arbitration/clock-stretch tests, and atomic transfer path coverage.
