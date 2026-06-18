# File Research: sources/block-storage/stratisd/src/dbus/macros.rs

Defines `handle_action!` macro for D-Bus action logging and availability signaling.

Forms:
- `handle_action!(action)` logs successful actions via `log::info!`.
- `handle_action!(action, connection, manager, pool_uuid)` additionally checks errors for available-action changes and sends action-availability signal for the pool path.

Important details:
- Uses blocking futures executor to read manager and send signal from inside macro context.
- Logs a warning if the pool path cannot be found.
- Used around engine/pool actions to keep D-Bus clients informed when failure changes future valid actions.
