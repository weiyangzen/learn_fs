# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_physical.py

## Role

Implements block-device listing for devices that make up Stratis pools.

## Main Behavior

`PhysicalActions.list_devices()` fetches managed objects, optionally filters by pool name, and prints device information in a table.

## Output Data

The listing includes device node, physical path, pool, tier, size-related values, initialization time, UUID, hardware/user info, and related status fields where available.

## Dependencies

Uses generated blockdev and pool managed-object helpers, `BlockDevTiers`, `justbytes.Range`, `get_property()`, `get_uuid_formatter()`, and `print_table()`.

## Notable Risk Areas

Some D-Bus properties may be missing or optional. The implementation uses `DbusClientMissingPropertyError` handling and `TABLE_UNKNOWN_STRING` to keep listings usable across daemon/property conditions.
