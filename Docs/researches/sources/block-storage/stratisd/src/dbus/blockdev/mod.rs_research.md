# File Research: sources/block-storage/stratisd/src/dbus/blockdev/mod.rs

Blockdev D-Bus revision registry.

Key behavior:
- Declares blockdev revisions r0 through r9 plus shared helpers.
- Re-exports `BlockdevR0` through `BlockdevR9`.
- `register_blockdev()` creates a unique object path under `/org/storage/stratis3/<counter>`, registers every blockdev revision on that path, logs individual registration failures, and records the path-to-UUID mapping in `Manager`.
- `unregister_blockdev()` removes every revision from zbus, resolves UUID from `Manager`, removes manager mapping, and returns the UUID.

Filesystem/block-storage relevance:
- Ensures one physical block device appears through all supported D-Bus API revisions on a single object path.
