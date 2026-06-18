# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_8/mod.rs

D-Bus interface `org.storage.stratis3.filesystem.r8`.

Behavior:
- Carries forward r7 surface:
  - `Origin`
  - writable `MergeScheduled`
  - writable `SizeLimit`
  - base filesystem properties
  - `SetName`
- Uses r0, r6, and r7 helper modules.
- Separate revisioned interface for compatibility.

No file-local semantic delta from r7.
