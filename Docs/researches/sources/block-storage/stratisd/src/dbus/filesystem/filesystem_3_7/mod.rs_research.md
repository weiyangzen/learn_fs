# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_7/mod.rs

D-Bus interface `org.storage.stratis3.filesystem.r7`.

Changes relative to r6:
- Adds `Origin` property for snapshot origin UUID.
- Adds `MergeScheduled` property and writable setter.
- Retains writable `SizeLimit`.
- Retains base properties and `SetName`.

Filesystem relevance:
- Exposes snapshot lineage and deferred merge scheduling through D-Bus.
