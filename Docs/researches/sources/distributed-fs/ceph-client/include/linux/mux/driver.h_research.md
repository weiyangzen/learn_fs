# sources/distributed-fs/ceph-client/include/linux/mux/driver.h

Purpose: declares the provider-side multiplexer core structures and registration APIs used by mux controller drivers.

Important APIs and types: `struct mux_control_ops` exposes the provider `set()` callback. `struct mux_control` holds a semaphore lock, parent chip, cached state, number of states, idle state, and last-change timestamp. `struct mux_chip` embeds a device, controller count, internal id, ops pointer, and a flexible counted array of mux controls. Helpers include `to_mux_chip()`, `mux_chip_priv()`, allocation/register/unregister/free, devm allocation/register, and `mux_control_get_index()`.

Control flow: a driver allocates a mux chip with a controller count and private tailroom, initializes per-controller `states` and `idle_state` plus chip ops, registers the chip, and the mux core calls `ops->set()` under mux locking when consumers select/deselect states. Unregister and free release device-model resources.

State and persistence: mux state is in-memory cached selection plus hardware state programmed by provider callbacks. `last_change` supports delay/settle calculations; idle state determines what the core programs when no consumer is active.

Dependencies and integration points: depends on device model, DT mux bindings for idle-state constants, `ktime`, and semaphores. It integrates platform mux hardware providers with the consumer API.

Risks and test signals: risks include drivers modifying `cached_state`, wrong flexible-array private-memory sizing, incorrect idle-state semantics, missing locking in provider callbacks, and stale cached state after hardware reset. Test multi-controller chips, private data access via `mux_chip_priv()`, register/unregister/devm cleanup, idle disconnect/as-is behavior, delay-sensitive consumers, and hardware reset recovery.
