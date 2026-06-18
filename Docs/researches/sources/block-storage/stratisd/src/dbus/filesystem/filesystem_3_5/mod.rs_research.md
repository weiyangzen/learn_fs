# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_5/mod.rs

D-Bus interface `org.storage.stratis3.filesystem.r5`.

Behavior:
- Same as r4: base filesystem properties and `SetName`.
- Uses shared `filesystem_prop()` plus r0 helper functions.
- Maintains compatibility under revision r5.

No unique semantic additions.
