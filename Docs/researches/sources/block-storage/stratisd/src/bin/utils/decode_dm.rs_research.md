# File Research: sources/block-storage/stratisd/src/bin/utils/decode_dm.rs

Maps Stratis filesystem device-mapper paths back to user-facing Stratis names.

Key behavior:
- Connects to the system D-Bus and calls ObjectManager `GetManagedObjects` on `org.storage.stratis3`.
- Extracts device-mapper names from absolute `/dev/mapper/<name>` paths.
- Parses names of form `stratis-1-<pool_uuid>-thin-fs-<filesystem_uuid>`.
- Looks up `Name` properties by matching `Uuid` properties on current package-minor revision interfaces:
  - `org.storage.stratis3.pool.r<minor>`
  - `org.storage.stratis3.filesystem.r<minor>`
- Exposes:
  - `pool_name(dm_path)`
  - `filesystem_name(dm_path)`
  - `symlink(dm_path)` returning `/dev/stratis/<pool>/<filesystem>`.

Filesystem relevance:
- Bridges low-level device-mapper names and Stratis logical filesystem naming.
