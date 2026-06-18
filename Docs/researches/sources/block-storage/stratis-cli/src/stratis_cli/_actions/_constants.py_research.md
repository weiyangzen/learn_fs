# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_constants.py

## Role

Defines D-Bus service, object, interface, sector-size, and stratisd version compatibility constants for the action layer.

## Constants

- `SERVICE = "org.storage.stratis3"`.
- `TOP_OBJECT = "/org/storage/stratis3"`.
- `SECTOR_SIZE = 512`.
- `MINIMUM_STRATISD_VERSION = "3.9.0"`.
- `MAXIMUM_STRATISD_VERSION = "4.0.0"`.
- `REVISION` is derived from the minimum version minor component, producing `r9`.
- Interface names cover blockdev, filesystem, manager, pool, report, and legacy `Manager.r0`.

## Dependencies

Uses `packaging.version.Version` to derive `REVISION`.

## Notable Behavior

The CLI is pinned to a D-Bus interface revision implied by the minimum supported stratisd version. Most generated D-Bus classes and error messages depend on these names.
