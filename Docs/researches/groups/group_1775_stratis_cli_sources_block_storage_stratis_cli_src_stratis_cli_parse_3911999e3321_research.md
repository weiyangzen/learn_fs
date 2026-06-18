# Group Research: group_1775_stratis_cli_sources_block_storage_stratis_cli_src_stratis_cli_parse_3911999e3321

Scope: `Docs/research_subset_a`, source tree `sources/block-storage/stratis-cli`.

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_pool.py -->
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
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_pool.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_shared.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_shared.py

## Purpose

Provides shared argparse helpers, reusable argument groups, size parsing, post-parse option handling, and move-notice formatting for Stratis CLI parser modules.

This file centralizes parser fragments used by multiple command groups, including pool creation/startup and encryption-related options.

## Constants

### Clevis/Tang keys

- `CLEVIS_KEY_TANG_TRUST_URL = "stratis:tang:trust_url"`
- `CLEVIS_PIN_TANG = "tang"`
- `CLEVIS_PIN_TPM2 = "tpm2"`
- `CLEVIS_KEY_THP = "thp"`
- `CLEVIS_KEY_URL = "url"`

These constants are used to construct `ClevisInfo` objects for Stratis daemon requests.

### Size parsing

- `_RANGE_RE = re.compile(r"^(?P<magnitude>[0-9]+)(?P<units>([KMGTP]i)?B)$")`

Accepted formats are a decimal integer followed by one of:

- `B`
- `KiB`
- `MiB`
- `GiB`
- `TiB`
- `PiB`

`_SIZE_SPECIFICATION` stores the user-facing error text for invalid size strings.

## Functions

### `_unit_map(unit_specifier)`

Maps a string unit specifier to the matching `justbytes` binary unit:

- `B` -> `B`
- `KiB` -> `KiB`
- `MiB` -> `MiB`
- `GiB` -> `GiB`
- `TiB` -> `TiB`
- `PiB` -> `PiB`

Unknown units trigger an assertion failure. Normal callers should be protected by `_RANGE_RE`, so this is an internal consistency assertion rather than user-facing validation.

### `parse_range(values)`

Parses CLI size strings into `justbytes.Range`.

Behavior:

- Validates `values` with `_RANGE_RE`.
- Raises `argparse.ArgumentTypeError` with `_SIZE_SPECIFICATION` if malformed.
- Converts the magnitude to `int`.
- Maps the unit through `_unit_map`.
- Returns `Range(int(magnitude), units)`.
- Asserts that the resulting magnitude denominator is `1`.

This function is used by pool integrity journal-size parsing.

### `ensure_nat(arg)`

Converts an argument to a non-negative integer.

Behavior:

- Attempts `int(arg)`.
- Raises `argparse.ArgumentTypeError` if conversion fails.
- Raises `argparse.ArgumentTypeError` if the result is less than zero.
- Returns the integer otherwise.

Despite the docstring saying “natural number,” this implementation accepts `0`.

## Argparse Actions

### `RejectAction`

An `argparse.Action` that always rejects use.

`__call__` raises `argparse.ArgumentError` saying the option cannot be assigned or set. It is used for hidden internal parser hooks such as `--post-parser`.

### `DefaultAction`

An `argparse.Action` that records whether a default value was overridden.

`__call__`:

- Sets `namespace.<dest>` to the parsed value.
- Sets `namespace.<dest>_default` to `False`.

Parser definitions pair this with a normal default value; if argparse never calls the action, helper classes can infer the default remained in effect.

## Classes

### `MoveNotice`

Formats deprecation/move notices for command epilogs.

Constructor fields:

- `name`
- `deprecated`
- `preferred`
- `version_completed`

`__str__` returns a notice saying the named subcommand is also available under a preferred command prefix and that the deprecated form will be removed in the specified Stratis version.

### `ClevisEncryptionOptions`

Post-parse helper for encryption options.

Constructor:

- Copies and deletes `namespace.clevis`.
- Copies and deletes `namespace.thumbprint`.
- Copies and deletes `namespace.tang_url`.
- Copies and deletes `namespace.trust_url`.

`verify(namespace, parser)` enforces conditional rules:

- If `--clevis nbde` or `--clevis tang` is specified, `--tang-url` is required.
- If `--tang-url` is specified, either `--thumbprint` or `--trust-url` is required.
- If `--tang-url` is specified without `--clevis nbde/tang`, parsing fails.
- If `--trust-url` or `--thumbprint` is specified without `--tang-url`, parsing fails.

On success, it writes `namespace.clevis` as:

- `None` if no Clevis method was selected.
- `ClevisInfo("tang", config)` for `Clevis.NBDE` or `Clevis.TANG`.
  - Config includes `{"url": self.tang_url}`.
  - Config also includes either:
    - `{"stratis:tang:trust_url": True}` when `--trust-url` is set.
    - `{"thp": self.thumbprint}` otherwise.
- `ClevisInfo("tpm2", {})` for other Clevis methods.

The dict merge operator is used to combine Tang URL and trust/thumbprint config.

## Reusable Argument Lists

### `UUID_OR_NAME`

Mutually exclusive identifier options:

- `--name`
- `--uuid`, type `UUID`

Used by pool commands that can identify a pool either by name or UUID.

### `KEYFILE_PATH_OR_STDIN`

Mutually exclusive key input options:

- `--keyfile-path`
- `--capture-key`
  - `store_true`
  - Reads key from stdin with no terminal echo or userspace buffer storage.

### `TRUST_URL_OR_THUMBPRINT`

Tang credential verification options:

- `--trust-url`
  - `store_true`
  - Omits verification of Tang server credentials.
- `--thumbprint`
  - Tang server thumbprint.

### `CLEVIS_AND_KERNEL`

Encryption creation options:

- `--key-desc`
  - Kernel keyring key description.
- `--clevis`
  - Type: `Clevis`
  - Choices: all `Clevis` enum values.
- `--tang-url`
  - URL of a Clevis Tang server, requiring `--clevis=[tang|nbde]`.

### `IN_PLACE`

Reusable option:

- `--in-place`
  - `store_true`
  - Indicates an operation should be performed in place without additional devices.

## Dependencies

Imports from standard library:

- `argparse`
- `copy`
- `re`
- `uuid.UUID`

Imports from `justbytes`:

- `B`
- `KiB`
- `MiB`
- `GiB`
- `TiB`
- `PiB`
- `Range`

Imports from local modules:

- `Clevis` from `_constants`
- `ClevisInfo` from `_stratisd_constants`

## Cross-File Relationships

- `_parser/_pool.py` uses `parse_range`, `DefaultAction`, `RejectAction`, `MoveNotice`, `ensure_nat`, `ClevisEncryptionOptions`, and the reusable argument lists.
- `ClevisEncryptionOptions` creates `_stratisd_constants.ClevisInfo` instances that action code can pass toward daemon-facing layers.
- The reusable lists are designed to be embedded in parser group declarations elsewhere.

## Important Behaviors

- Size parsing requires binary suffixes exactly matching the accepted set. Plain numbers without `B` fail.
- `ensure_nat` accepts zero.
- `DefaultAction` does not set a `<dest>_default` flag to `True`; consumers use missing attribute as “default used.”
- `ClevisEncryptionOptions` deletes raw parser attributes from the namespace and replaces them with a processed `namespace.clevis` value.
- `Clevis.NBDE` and `Clevis.TANG` are both normalized to a Tang Clevis pin.

## Research Notes

This file contains shared parser mechanics rather than command-specific storage logic. Its validation behavior affects multiple CLI commands because it encodes common assumptions about identifiers, key capture, Clevis/Tang configuration, natural-number parsing, and size grammar.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_shared.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_stratisd_constants.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_stratisd_constants.py

## Purpose

Defines small Python representations of constants and data structures used when interacting with `stratisd`, the Stratis daemon.

The module includes daemon return codes, block device tier identifiers, report keys, pool action availability levels, metadata versions, and a Clevis configuration container.

## Definitions

### `StratisdErrors`

An `IntEnum` for daemon result codes:

- `OK = 0`
- `ERROR = 1`

`__str__` returns the enum member name, such as `OK` or `ERROR`.

### `BlockDevTiers`

An `IntEnum` for block device tiers:

- `DATA = 0`
- `CACHE = 1`

`__str__` returns the enum member name.

### `ReportKey`

An `Enum` of report identifiers:

- `ENGINE_STATE = "engine_state_report"`
- `MANAGED_OBJECTS = "managed_objects_report"`
- `STOPPED_POOLS = "stopped_pools"`

`__str__` returns the underlying string value.

The file notes that `managed_objects_report` is not a key recognized by `stratisd`, but is defined here because it is used together with daemon-recognized report constants.

### `PoolActionAvailability`

An `IntEnum` describing which categories of pool interaction are available:

- `fully_operational = 0`
- `no_ipc_requests = 1`
- `no_pool_changes = 2`

#### `pool_maintenance_alerts()`

Returns a list of `PoolMaintenanceAlert` values corresponding to the availability level:

- If availability is at least `no_ipc_requests`, includes `PoolMaintenanceAlert.NO_IPC_REQUESTS`.
- If availability is at least `no_pool_changes`, includes `PoolMaintenanceAlert.NO_POOL_CHANGES`.

Because this is an `IntEnum`, ordering is significant. `no_pool_changes` includes both alerts, since its value is greater than `no_ipc_requests`.

### `MetadataVersion`

An `Enum` for Stratis metadata versions:

- `V1 = 1`
- `V2 = 2`

`__str__` returns the numeric value as a string.

### `ClevisInfo`

A simple container for Clevis encryption metadata.

Constructor parameters:

- `pin: str`
- `config: Mapping[str, Any]`

Stored fields:

- `self.pin`
- `self.config`

This is used by parser/helper code to represent Clevis pin and JSON-like config data before action/daemon layers consume it.

## Dependencies

Imports from standard library:

- `Enum`
- `IntEnum`
- `typing.Any`
- `typing.List`
- `typing.Mapping`

Imports from local modules:

- `PoolMaintenanceAlert` from `_alerts`

## Cross-File Relationships

- `_parser/_shared.py` imports `ClevisInfo` and creates instances during Clevis option validation.
- Alert/reporting code can use `PoolActionAvailability.pool_maintenance_alerts()` to map daemon availability state into user-facing maintenance alerts.
- Parser/action code may rely on `MetadataVersion`, `BlockDevTiers`, `ReportKey`, and `StratisdErrors` as stable daemon-facing constants.

## Important Behaviors

- `PoolActionAvailability` values are ordered by severity/capability reduction; comparison operators are used directly.
- `ClevisInfo` has no validation, representation, equality, or conversion methods. It is only a lightweight field container.
- `ReportKey.__str__` differs from most other enums in this file by returning the value rather than the member name.

## Research Notes

This file is a shared constants boundary between CLI code and daemon semantics. Changes to enum numeric values or string values can affect DBus/report interpretation and compatibility with `stratisd`.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_stratisd_constants.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_version.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_version.py

## Purpose

Defines package version information for Stratis CLI.

## Definitions

### `__version_info__`

Tuple version:

```python
(3, 9, 0)
```

### `__version__`

String version generated from `__version_info__`:

```python
".".join(str(x) for x in __version_info__)
```

For the current file contents, this evaluates to:

```python
"3.9.0"
```

## Dependencies

No imports.

## Cross-File Relationships

Other modules can import `__version__` or `__version_info__` for CLI version display, packaging metadata, compatibility checks, or user-facing diagnostics.

The parser move notices in `_parser/_pool.py` mention deprecated pool-level encryption commands being removed in Stratis `3.10.0`, which is one minor release after the version declared here.

## Important Behaviors

- The string version is derived from the tuple, avoiding duplicate literal version strings.
- There is no dynamic package metadata lookup; the version is static source data.

## Research Notes

This is a small metadata module. The main maintenance risk is keeping this static version synchronized with packaging/release metadata elsewhere in the Stratis CLI source tree.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_version.py -->