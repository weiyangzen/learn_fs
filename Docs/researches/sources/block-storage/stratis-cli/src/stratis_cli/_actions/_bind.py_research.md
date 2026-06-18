# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_bind.py

## Role

Implements encryption binding actions for pools: bind, rebind, and unbind against Clevis or kernel keyring mechanisms.

## Main Behavior

- `_get_pool_id()` creates a `PoolId` from parser namespace data. Legacy pool subcommands pass a positional `pool_name`; newer encryption subcommands can pass UUID/name option pairs.
- `BindActions.bind_clevis()` locates the pool, builds a Clevis JSON configuration, and calls `Pool.Methods.BindClevis`.
- `BindActions.bind_keyring()` locates the pool and calls `Pool.Methods.BindKeyring`.
- `BindActions.unbind()` dispatches to `UnbindKeyring` or `UnbindClevis` based on `EncryptionMethod`.
- `RebindActions.rebind_clevis()` and `rebind_keyring()` call the corresponding pool rebind methods, optionally with token slot selection.

## D-Bus Interaction

All actions obtain the top object with `get_object(TOP_OBJECT)`, call `ObjectManager.Methods.GetManagedObjects`, then query pools by managed-object key before invoking pool methods.

## Error Handling

- Nonzero daemon return codes become `StratisCliEngineError`.
- False result flags from bind/rebind/unbind become `StratisCliNoChangeError`.
- Pool lookup failures are handled by generated query exceptions and later interpreted by `_error_reporting.py`.

## Notable Risk Areas

This module relies on parser namespaces having the right shape for both legacy and newer command paths. Token-slot semantics are passed directly to stratisd as optional `(bool, uint)`-style D-Bus data.
