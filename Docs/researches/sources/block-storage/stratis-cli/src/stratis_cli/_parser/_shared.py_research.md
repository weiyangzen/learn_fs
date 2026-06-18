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
