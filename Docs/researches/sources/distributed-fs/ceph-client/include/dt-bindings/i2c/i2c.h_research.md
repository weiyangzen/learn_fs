# sources/distributed-fs/ceph-client/include/dt-bindings/i2c/i2c.h

## Purpose
defines I2C client address flags for Devicetree: 10-bit addresses and slave-mode addresses.

## Important APIs, Types, and Functions
The exported macros are `I2C_TEN_BIT_ADDRESS`, `I2C_OWN_SLAVE_ADDRESS`. They are high-bit flags intended to be ORed into the `reg` address cell, not standalone bus operations.

## Control Flow
No code executes here. DTS authors place the flags in an I2C child `reg`; OF/I2C registration strips and interprets them when creating the client device.

## State, Persistence, and Dependencies
There is no state. The persisted ABI is the chosen high-bit encoding in compiled DTBs. The header is included by DTS files and consumed by I2C OF client creation code that recognizes `I2C_TEN_BIT_ADDRESS` and `I2C_OWN_SLAVE_ADDRESS`.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Using the flags as literal addresses, changing high-bit values, or colliding with valid address ranges can misregister devices.

## Test Signals
Compile DTS examples with 7-bit, 10-bit, and own-slave addresses; verify created `i2c_client` flags and stripped addresses match expectations.
