# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_debug.py

## Role

Implements debug-only daemon, pool, filesystem, and blockdev actions.

## Main Behavior

- `TopDebugActions.refresh_state()` calls `Manager.Methods.RefreshState`.
- `TopDebugActions.send_uevent()` maps a `/dev/...` path to sysfs and writes `change` to the device `uevent` file.
- `PoolDebugActions` print pool object paths and pool metadata JSON.
- `FilesystemDebugActions` print filesystem object paths and filesystem metadata JSON.
- `BlockdevDebugActions.get_object_path()` looks up blockdevs by UUID and prints the object path.

## Error Handling

Daemon failures become `StratisCliEngineError`; sysfs write failures become `StratisCliSynthUeventError`.

## Notable Risk Areas

Synthetic uevent generation writes directly to host sysfs. Metadata pretty-printing assumes daemon-returned metadata strings are valid JSON.
