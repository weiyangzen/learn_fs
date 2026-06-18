# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_logical.py

## Role

Implements filesystem-level actions: create, list, destroy, snapshot, rename, size-limit changes, and snapshot revert scheduling.

## Main Actions

- `create_volumes()` creates one or more filesystems in a pool, checking for existing names and partial creation.
- `list_volumes()` delegates to `_list_filesystem.list_filesystems()`.
- `destroy_volumes()` removes one or more filesystems and checks actual removals.
- `snapshot_filesystem()` snapshots an origin filesystem.
- `rename_fs()` sets filesystem name.
- `set_size_limit()` sets a filesystem size limit, supporting `current`.
- `unset_size_limit()` clears an existing size limit.
- `schedule_revert()` sets `MergeScheduled`.
- `cancel_revert()` clears `MergeScheduled`.

## D-Bus Interaction

Uses `ObjectManager.GetManagedObjects`, pool/filesystem query helpers, `Pool.Methods.CreateFilesystems`, `DestroyFilesystems`, `SnapshotFilesystem`, `Filesystem.Methods.SetName`, and `Filesystem.Properties.*.Set`.

## Error Handling

Raises `StratisCliPartialChangeError`, `StratisCliEngineError`, `StratisCliIncoherenceError`, `StratisCliNoChangeError`, and `StratisCliNoPropertyChangeError` depending on daemon result and local pre/postconditions.

## Notable Risk Areas

Multi-filesystem operations carefully compare requested names against actual daemon-reported changes. That postcondition logic is important because D-Bus method success alone is not treated as enough.
