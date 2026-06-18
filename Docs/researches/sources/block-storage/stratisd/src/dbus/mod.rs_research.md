# File Research: sources/block-storage/stratisd/src/dbus/mod.rs

Purpose: Top-level D-Bus module for stratisd.

Key behavior:
- Declares D-Bus submodules: macros, blockdev, consts, filesystem, manager, pool, types, udev, and util.
- Reexports core D-Bus entry points and helpers: blockdev/filesystem registration, `Manager`, `UdevHandler`, and background signal helpers.
- `create_dbus_handler` creates the system-bus connection, requests the Stratis service name, registers manager/report interfaces, and constructs the udev handler.

Runtime wiring:
- Creates a shared atomic object-path counter.
- Creates a shared `Lockable<Arc<RwLock<Manager>>>` registry.
- Returns `(Connection, UdevHandler, Manager)` for daemon integration.

Dependencies:
- `zbus::connection::Builder`.
- Tokio `UnboundedReceiver` and `RwLock`.
- Engine event type `UdevEngineEvent`.
