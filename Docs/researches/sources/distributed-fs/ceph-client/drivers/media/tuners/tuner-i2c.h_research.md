# sources/distributed-fs/ceph-client/drivers/media/tuners/tuner-i2c.h

Purpose: shared I2C transfer, logging, and hybrid-instance helper header for tuner drivers.

APIs/types: `struct tuner_i2c_props` stores address, adapter, refcount, and name. Inline helpers wrap send, receive, and send/receive I2C transfers. Logging macros assume a local `priv->i2c_props`. Hybrid macros allocate/find/release shared state by adapter ID and address.

Control flow/state: transfer helpers normalize successful `i2c_transfer()` counts to requested byte lengths. Hybrid request scans a caller-owned list under external locking, increments counts for existing devices, or allocates and links new state.

Dependencies/integration: Linux I2C, slab allocation, list nodes embedded in caller private structs, and driver-level mutexes.

Risks/tests: macros are not type-safe and require exact private-struct layout plus locking. Test I2C error propagation, shared attach/release counts, duplicate address handling, and debug logging.
