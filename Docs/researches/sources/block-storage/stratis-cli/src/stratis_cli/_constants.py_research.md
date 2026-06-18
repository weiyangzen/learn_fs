# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_constants.py

## Role

Defines shared enums and identifier wrappers used by parsers and actions.

## Identifier Types

- `IdType` distinguishes UUID and name.
- `Id` provides common D-Bus query key and D-Bus method argument conversion.
- `PoolId` and `FilesystemId` parse argparse namespaces and produce readable descriptions.
- `PoolId.stopped_pools_func()` builds a predicate for stopped-pool dictionary selection.

## Other Enums

- `YesOrNo` for yes/no parser toggles.
- `EncryptionMethod`: keyring or Clevis.
- `UnlockMethod`: any, Clevis, or keyring; legacy token slot mapping supports older pools.
- `Clevis`: `nbde`, `tang`, `tpm2`.
- `IntegrityTagSpec`: `0b`, `32b`, `512b`.
- `IntegrityOption`: no integrity or pre-allocate.

## Notable Risk Areas

These enums bridge CLI text, D-Bus argument shapes, and internal comparisons. Parser option choices and action code depend on their string values.
