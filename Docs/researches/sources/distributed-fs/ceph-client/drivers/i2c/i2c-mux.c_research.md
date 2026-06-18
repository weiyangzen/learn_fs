# sources/distributed-fs/ceph-client/drivers/i2c/i2c-mux.c

Purpose: shared I2C mux framework implementation. It lets mux drivers expose each downstream channel as a child adapter while wrapping transfers with channel select/deselect callbacks and correct parent/root bus locking.

Important APIs: exports `i2c_root_adapter()`, `i2c_mux_alloc()`, `i2c_mux_add_adapter()`, and `i2c_mux_del_adapters()`. Private `struct i2c_mux_priv` stores each child adapter, algorithm, mux core pointer, and channel ID.

Control flow: child transfer callbacks select the channel, call parent `__i2c_transfer()`/`i2c_transfer()` or SMBus equivalents depending on mux locking mode, then deselect if provided. `i2c_mux_alloc()` creates the mux core and stores flags for locked muxes, arbitrators, and gates. `i2c_mux_add_adapter()` builds a per-channel adapter, mirrors parent functionality, timeout, quirks, and firmware node, registers it, and creates sysfs links. Deletion removes links, unregisters adapters, drops OF refs, and frees private data.

State and persistence: mux cores hold parent, callbacks, flags, channel adapter list, and driver-private data. Child adapters persist until explicit deletion. Sysfs links expose mux-to-channel relationships.

Dependencies and integration: depends on the I2C core, OF child-node conventions (`i2c-mux`, `i2c-arb`, `i2c-gate`), ACPI companion preset, and adapter locking APIs.

Risks: lock selection is central to avoiding nested-transfer deadlocks. Channel OF node lookup must support old and new DT layouts. The code assigns atomic callbacks from dynamic algorithm fields, so regressions around `master_xfer`/`xfer` aliases need build coverage. Deselect errors are ignored by transfer wrappers.

Test signals: nested mux topologies, mux-locked and parent-locked transfers, SMBus and I2C functionality inheritance, OF/ACPI channel enumeration, sysfs link creation, and cleanup after partial adapter-add failure.
