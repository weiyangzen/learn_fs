# File Research: sources/block-storage/stratisd/src/dbus/filesystem/mod.rs

Filesystem D-Bus revision registry.

Key behavior:
- Declares filesystem revisions r0 through r9 plus shared helpers.
- Re-exports `FilesystemR0` through `FilesystemR9`.
- `register_filesystem()` creates a unique object path, records filesystem UUID in `Manager`, and registers every filesystem revision on that path.
- `unregister_filesystem()` removes manager mapping first, then unregisters every revision from zbus, returning the filesystem UUID.

Filesystem relevance:
- Ensures each Stratis filesystem is exposed through all supported D-Bus API revisions on a single object path.
