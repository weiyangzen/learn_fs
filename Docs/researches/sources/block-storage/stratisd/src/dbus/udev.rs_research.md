# File Research: sources/block-storage/stratisd/src/dbus/udev.rs

This file defines `UdevHandler`, which bridges queued udev engine events into D-Bus registration and property signaling.

State held by `UdevHandler`:
- D-Bus connection.
- Engine reference.
- Manager lock.
- `UnboundedReceiver<UdevEngineEvent>`.
- Object path counter.

Main behavior:
- `process_udev_events()`:
  - waits for at least one event;
  - drains any immediately available additional events with `try_recv()`;
  - calls `Engine::handle_events(events)`;
  - registers any newly discovered pools returned by the engine;
  - sends blockdev new-physical-size signals for block devices whose size diff changed.
- `register_pool()`:
  - delegates to `dbus::pool::register_pool`.

Error handling:
- A closed event channel is converted to `StratisError::Msg`.
- Pool registration failures and missing blockdev object paths are logged as warnings rather than aborting the whole handler.

Role in architecture:
- This is the D-Bus side of udev reconciliation. The engine interprets events; this handler updates exported D-Bus objects and emits property-change notifications.
