# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ccgx-ucsi.h

## Purpose
Public internal declaration for the Cypress CCGx UCSI I2C-client instantiation helper.

## APIs, Control Flow, and State
The header forward-declares `struct i2c_adapter`, `struct i2c_client`, and `struct software_node`, then declares `i2c_new_ccgx_ucsi()`. Include guards prevent duplicate declarations. It owns no state and contains no inline behavior.

## Dependencies and Integration
Used by code that wants to create the CCGx UCSI client without depending on full I2C or software-node header inclusion in its own interface. The implementation is in `i2c-ccgx-ucsi.c`.

## Risks and Test Signals
Risks are limited to prototype drift and missing includes in callers. Test with compile coverage of all helper users and module builds where `i2c-ccgx-ucsi.c` is enabled as built-in or module.
