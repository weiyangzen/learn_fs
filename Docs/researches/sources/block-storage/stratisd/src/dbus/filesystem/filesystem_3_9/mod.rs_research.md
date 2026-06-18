# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_9/mod.rs

D-Bus interface `org.storage.stratis3.filesystem.r9`.

Behavior:
- Latest listed filesystem revision in this group.
- Same surface as r8/r7:
  - snapshot origin
  - merge scheduling
  - size limits
  - base properties and rename method
- Uses shared setter helpers to release pool locks before emitting D-Bus signals.

No unique semantic delta from r8 in this file.
