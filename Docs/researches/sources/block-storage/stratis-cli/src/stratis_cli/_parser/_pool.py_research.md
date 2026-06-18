# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_pool.py

## Purpose

Defines the `stratis pool ...` command-line parser surface for Stratis CLI. The file is mostly declarative parser metadata: subcommand names, help text, argument groups, mutually exclusive options, parser conversion functions, post-parse validators, and action dispatch targets.

It connects parser definitions to operational code in `PoolActions` and `BindActions`, while reusing shared parser fragments from `_parser/_shared.py` and encryption/debug subcommand groups from neighboring parser modules.

## Main Definitions

### `IntegrityOptions`

A post-parse helper that gathers integrity-related options from an `argparse.Namespace`:

- Copies and removes `namespace.integrity`.
- Copies and removes `namespace.journal_size`.
- Tracks whether `journal_size` was explicitly set via `namespace.journal_size_default`, defaulting to `True`.
- Copies and removes `namespace.tag_spec`.
- Tracks whether `tag_spec` was explicitly set via `namespace.tag_spec_default`, defaulting to `True`.

`verify(namespace, parser)` enforces conditional validity:

- `--integrity no` cannot be combined with an explicitly supplied `--journal-size`.
- `--integrity no` cannot be combined with an explicitly supplied `--tag-spec`.
- On success, stores the whole `IntegrityOptions` instance back as `namespace.integrity`.

This design preserves both parsed values and “was default used?” state, which matters because default journal/tag values are allowed with `--integrity no`, but explicit journal/tag options are rejected.

### `CreateOptions`

A post-parse helper for `pool create`.

It composes:

- `ClevisEncryptionOptions(namespace)` from `_shared.py`.
- `IntegrityOptions(namespace)` from this file.

`verify(namespace, parser)` delegates to both helpers. This lets `pool create` validate encryption and integrity option combinations after argparse has accepted the raw syntax.

## Parser Structure

### `POOL_SUBCMDS`

A list of subcommand descriptors consumed by the Stratis CLI parser builder. Each item is a tuple:

```python
("command-name", {parser metadata})
```

The metadata includes argument lists, grouped arguments, mutually exclusive argument groups, help text, aliases, epilog notices, nested subcommands, and the action function to dispatch.

## Subcommands

### `create`

Creates a pool.

Argument groups:

- `Encryption`
  - Uses `CLEVIS_AND_KERNEL` from `_shared.py`.
  - Adds `--key-desc`, `--clevis`, and `--tang-url`.

- `Tang Server Verification (only if --tang-url option is set)`
  - Mutually exclusive optional choices from `TRUST_URL_OR_THUMBPRINT`.
  - Adds `--trust-url` or `--thumbprint`.

- `Integrity`
  - Adds `--integrity`.
    - Type: `IntegrityOption`.
    - Choices: all `IntegrityOption` enum values.
    - Default: `IntegrityOption.PRE_ALLOCATE`.
  - Adds `--journal-size`.
    - Action: `DefaultAction`.
    - Default: `Range(128, MiB)`.
    - Type: `parse_range`.
  - Adds `--tag-spec`.
    - Action: `DefaultAction`.
    - Default: `IntegrityTagSpec.B512`.
    - Choices: all `IntegrityTagSpec` except `B0`.
    - Type: `IntegrityTagSpec`.

Arguments:

- Hidden `--post-parser`
  - `RejectAction`, defaulting to `CreateOptions`.
  - Prevents users from setting the internal hook directly.
- `pool_name`
- `blockdevs`, one or more devices.
- `--no-overprovision`

Dispatches to `PoolActions.create_pool`.

### `destroy`

Arguments:

- `pool_name`

Dispatches to `PoolActions.destroy_pool`.

### `start`

Starts a pool, with optional cache removal and optional unlock/key input.

Arguments:

- `--remove-cache`

Groups:

- Required `Pool Identifier`
  - Mutually exclusive required choice from `UUID_OR_NAME`: `--name` or `--uuid`.

- Optional `Unlock Method`
  - Mutually exclusive optional choice:
    - `--unlock-method`, type `UnlockMethod`.
    - `--token-slot`, type `ensure_nat`.

- Optional `Key Value Specification`
  - Mutually exclusive optional choice from `KEYFILE_PATH_OR_STDIN`:
    - `--keyfile-path`
    - `--capture-key`

Dispatches to `PoolActions.start_pool`.

### `stop`

Stops a pool storage stack without erasing metadata.

Groups:

- Required `Pool Identifier`
  - `--name` or `--uuid`.

Dispatches to `PoolActions.stop_pool`.

### `list`

Lists pools.

Arguments:

- `--stopped`

Groups:

- Optional `Pool Identifier`
  - `--name` or `--uuid`.

Dispatches to `PoolActions.list_pools`.

### `rename`

Arguments:

- `current`
- `new`

Dispatches to `PoolActions.rename_pool`.

### `encryption`

Nested command group for pool encryption operations.

- Help: manage pool encryption operations.
- Alias: `crypt`.
- Subcommands: `ENCRYPTION_SUBCMDS`.

### `init-cache`

Arguments:

- `pool_name`
- `blockdevs`, one or more devices.

Dispatches to `PoolActions.init_cache`.

### `add-data`

Arguments:

- `pool_name`
- `blockdevs`, one or more devices, displayed as `blockdev`.

Dispatches to `PoolActions.add_data_devices`.

### `add-cache`

Arguments:

- `pool_name`
- `blockdevs`, one or more devices, displayed as `blockdev`.

Dispatches to `PoolActions.add_cache_devices`.

### `extend-data`

Extends pool data capacity using enlarged component data devices.

Arguments:

- `pool_name`
- `--device-uuid`
  - Action: `extend`.
  - `nargs="*"`.
  - Type: `UUID`.
  - Default: empty list.
  - May be specified multiple times.
  - If omitted, all pool devices that appear to have increased in size are candidates.

Dispatches to `PoolActions.extend_data`.

### `bind`

Legacy/moved command wrapper.

- Subcommands: `BIND_SUBCMDS`.
- Epilog: `MoveNotice("bind", "pool", "pool encryption", "3.10.0")`.

### `rebind`

Legacy/moved command wrapper.

- Subcommands: `REBIND_SUBCMDS`.
- Epilog: `MoveNotice("rebind", "pool", "pool encryption", "3.10.0")`.

### `unbind`

Legacy/moved unbind command.

Arguments:

- `method`
  - Choices: all `EncryptionMethod`.
  - Type: `EncryptionMethod`.
- `pool_name`
- `--token-slot`
  - Type: `ensure_nat`.

Epilog indicates movement to `pool encryption` in Stratis `3.10.0`.

Dispatches to `BindActions.unbind`.

### `set-fs-limit`

Arguments:

- `pool_name`
- `amount`
  - Type: `ensure_nat`.

Dispatches to `PoolActions.set_fs_limit`.

### `overprovision`

Arguments:

- `pool_name`
- `decision`
  - Choices: all `YesOrNo`.
  - Type: `YesOrNo`.

Dispatches to `PoolActions.set_overprovisioning_mode`.

### `explain`

Explains pool alert codes.

Arguments:

- `code`
  - Choices from `PoolAlert.code_strs()`.

Dispatches to `PoolActions.explain_code`.

### `debug`

Nested debug command group.

- Subcommands: `POOL_DEBUG_SUBCMDS`.

## Dependencies

Imports from standard library:

- `copy`
- `argparse.SUPPRESS`
- `argparse.ArgumentParser`
- `argparse.Namespace`
- `uuid.UUID`

Imports from `justbytes`:

- `MiB`
- `Range`

Imports from local modules:

- `BindActions`, `PoolActions`
- `PoolAlert`
- Enums/constants:
  - `EncryptionMethod`
  - `IntegrityOption`
  - `IntegrityTagSpec`
  - `UnlockMethod`
  - `YesOrNo`
- Parser subcommand groups:
  - `POOL_DEBUG_SUBCMDS`
  - `BIND_SUBCMDS`
  - `ENCRYPTION_SUBCMDS`
  - `REBIND_SUBCMDS`
- Shared parser helpers:
  - `CLEVIS_AND_KERNEL`
  - `KEYFILE_PATH_OR_STDIN`
  - `TRUST_URL_OR_THUMBPRINT`
  - `UUID_OR_NAME`
  - `ClevisEncryptionOptions`
  - `DefaultAction`
  - `MoveNotice`
  - `RejectAction`
  - `ensure_nat`
  - `parse_range`

## Cross-File Relationships

- Depends directly on `_parser/_shared.py` for common argparse fragments and validation helpers.
- Uses `_stratisd_constants.ClevisInfo` indirectly through `ClevisEncryptionOptions`.
- Refers to Stratis action classes, but does not perform DBus or daemon calls itself.
- Reuses encryption subcommands while keeping deprecated `pool bind/rebind/unbind` entry points available through move notices.

## Important Behaviors

- `pool create --integrity no --journal-size ...` is rejected only when `--journal-size` was explicitly provided.
- `pool create --integrity no --tag-spec ...` is rejected only when `--tag-spec` was explicitly provided.
- Internal `--post-parser` is intentionally hidden and rejected if a user tries to set it.
- Several options use enum constructors as argparse `type` functions, causing CLI strings to be converted into project-specific enum values.
- `--device-uuid` for `extend-data` uses argparse `extend` with `nargs="*"`, so repeated occurrences append all supplied UUID values into one list.

## Research Notes

This file is the parser contract for pool commands. Behavioral changes here alter accepted CLI syntax, validation timing, default interpretation, help output, and action dispatch, even though the file itself contains little operational storage logic.
