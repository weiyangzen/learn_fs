# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_stratisd_version.py

## Role

Checks that the running `stratisd` version is compatible with this CLI.

## Main Behavior

`check_stratisd_version()` reads `Manager0.Properties.Version`, builds a packaging specifier range, and verifies that the daemon version is at least `MINIMUM_STRATISD_VERSION` and less than `MAXIMUM_STRATISD_VERSION`.

## Error Handling

Raises `StratisCliStratisdVersionError` when the daemon version is outside the supported range.

## Dependencies

Uses `packaging.specifiers.SpecifierSet`, `packaging.version.Version`, D-Bus object access, and constants from `_actions/_constants.py`.

## Notable Risk Areas

This is the gate that prevents commands from running against unsupported D-Bus revisions. Version parsing assumes daemon version strings are valid packaging versions.
