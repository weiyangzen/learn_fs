# sources/distributed-fs/ceph-client/include/linux/via_i2c.h

## Purpose
This header declares VIA framebuffer I2C adapter state and helper APIs.

## Important APIs, types, and functions
Key type is `via_i2c_stuff` containing an `i2c_adapter`, bit-banged algo data, IO port, adapter type, and active flag. APIs include byte and multi-byte read/write helpers, adapter lookup, `viafb_i2c_init()`, and `viafb_i2c_exit()`.

## Control flow, state, and persistence
VIA framebuffer code initializes bit-banged I2C adapters, then callers perform indexed byte reads/writes to display devices such as DDC/EDID or panel controllers. State is runtime adapter registration and bit-bang GPIO/IO state.

## Dependencies and integration points
It depends on Linux I2C and i2c-algo-bit plus VIA core adapter enums. It integrates VIA display output code with EDID and peripheral control.

## Risks and test signals
Risks include bus selection mistakes, adapter lifetime issues, and bit-bang timing/port errors. Tests should cover init/exit, adapter lookup, read/write transactions, and invalid adapter IDs.
