# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_data.py

## Role

Generates Python D-Bus client classes and managed-object query helpers from embedded introspection XML.

## Generated Objects

Creates `Report`, `Filesystem`, `MOFilesystem`, `filesystems`, `Pool`, `MOPool`, `pools`, `MODev`, `devs`, `Manager`, `ObjectManager`, and `Manager0`.

## Compatibility Behavior

Adds a minimal legacy `Manager.r0` spec when needed so daemon version checks can read the `Version` property independently of the current manager interface revision.

## Environment and Safety Hooks

Reads `STRATIS_DBUS_TIMEOUT`, defaulting to 60000 ms, through `_environment.get_timeout()`. It wraps mutating methods that accept device paths (`CreatePool`, `InitCache`, `AddCacheDevs`, `AddDataDevs`) with assertions that paths are absolute.

## Error Handling

Generation errors from `dbus_python_client_gen` or `dbus_client_gen` become `StratisCliGenerationError`.

## Notable Risk Areas

This module is import-order sensitive and asserts `stratis_cli.run` exists before loading. Any D-Bus XML/interface change affects generated classes used across almost all action modules.
