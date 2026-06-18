# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_7/methods.rs

Purpose: Implements r7 metadata retrieval methods.

Methods:
- `metadata_method(engine, pool_uuid, current)`.
- `filesystem_metadata_method(engine, pool_uuid, fs_name, current)`.

Key behavior:
- Looks up pool by UUID with read access.
- Runs metadata access in `spawn_blocking`.
- `current == true` returns current metadata.
- `current == false` returns last metadata.
- Filesystem metadata accepts optional filesystem name.

Return semantics:
- Returns metadata JSON/string with OK status on success.
- Missing pool, engine metadata errors, and join errors are converted to D-Bus error tuples.
