# File Research: sources/block-storage/stratisd/src/dbus/pool/mod.rs

Purpose: Central pool D-Bus registration and unregistration module.

Key behavior:
- Declares pool revision modules r0 through r9 plus shared helpers.
- Reexports `PoolR0` through `PoolR9`.
- `register_pool` allocates a unique object path under `STRATIS_BASE_PATH` using the atomic counter.
- Registers every pool interface revision on that path.
- Adds the pool UUID/path mapping to `Manager`.
- Registers existing filesystems and block devices belonging to the pool.
- Returns the pool path and blockdev paths.

Unregistration:
- Looks up and removes the pool path/UUID mapping from `Manager`.
- Removes every pool revision interface from the object server.
- Returns the pool UUID.

Important detail:
- Registration failures for individual interface revisions are warnings, not fatal.
- Failure to find the pool after engine start is fatal.
