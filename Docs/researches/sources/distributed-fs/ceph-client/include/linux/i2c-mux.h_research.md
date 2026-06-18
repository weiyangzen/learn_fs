# sources/distributed-fs/ceph-client/include/linux/i2c-mux.h

## Purpose
Defines I2C mux core data structures and helpers for creating child I2C adapters behind a multiplexer, arbitrator, or gate.

## APIs, Control Flow, and State
Within `__KERNEL__`, `struct i2c_mux_core` stores parent adapter, owning device, mode flags, private data, select/deselect callbacks, adapter counts, and flexible array of child adapters. `i2c_mux_alloc()` allocates the core with private storage and callbacks. `I2C_MUX_LOCKED`, `I2C_MUX_ARBITRATOR`, and `I2C_MUX_GATE` configure locking/behavior. `i2c_mux_add_adapter()` creates child buses identified by channel ID, and `i2c_mux_del_adapters()` removes them. `i2c_root_adapter()` finds the root adapter for a device.

## Dependencies, Integration, Risks, and Tests
Depends on bitops and I2C adapter definitions. Integrates with I2C mux drivers, nested mux topologies, and bus locking. Risks include incorrect select/deselect symmetry, deadlocks with locked muxes, orphaned child adapters, wrong force bus numbers, and private data sizing mistakes. Test signals include nested mux transfer routing, channel select/deselect traces, adapter add/remove cleanup, and locking stress across root vs segment locks.
