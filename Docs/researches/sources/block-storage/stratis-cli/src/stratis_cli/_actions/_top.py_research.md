# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_top.py

## Role

Implements top-level report and key-management actions.

## Main Helpers

- `_fetch_keylist()` calls `Manager.Methods.ListKeys`.
- `_add_update_key()` obtains a passphrase FD and calls `Manager.Methods.SetKey`, closing file descriptors afterward.

## Main Actions

- `get_report()` prints a report from `Report.Methods.GetReport` or legacy `Manager.Methods.EngineStateReport`, with JSON formatting and optional key sorting.
- `set_key()` adds a new key, detecting pre-existing key descriptions.
- `reset_key()` updates an existing key.
- `unset_key()` removes a key.
- `list_keys_()` prints keys in a table.

## Dependencies

Uses generated D-Bus classes, report keys, passphrase FD helpers, JSON, and table formatting.

## Error Handling

Raises resource-not-found, name-conflict, no-change, engine, and incoherence errors depending on key existence and daemon result flags.

## Notable Risk Areas

Passphrase handling uses file descriptors so secrets can be passed to stratisd without embedding secret text in D-Bus messages. All descriptor paths must remain closed on success and failure.
