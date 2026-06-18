# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_list_filesystem.py

## Role

Implements filesystem listing output for table and detailed views.

## Main Flow

`list_filesystems()` fetches managed objects, optionally filters by pool name or filesystem ID, builds a pool-object-path to pool-name mapping, and chooses detail or table display based on whether a specific filesystem was selected.

## Classes

- `ListFilesystem` is the abstract base for common formatting helpers.
- `Table` prints filesystem rows with pool, name, used/limit, created timestamp, device node, UUID, and status-related fields.
- `Detail` prints expanded per-filesystem properties.

## Formatting Behavior

Uses `SizeTriple` for total/used/free-style size data, `get_property()` for optional D-Bus properties, date parsing for timestamps, and `print_table()` for aligned tabular output.

## Dependencies

Depends on generated D-Bus object helpers, pool/filesystem managed-object queries, `justbytes.Range`, `dateutil`, and shared formatting utilities.

## Notable Risk Areas

Missing optional properties are handled deliberately through `DbusClientMissingPropertyError` and `TABLE_UNKNOWN_STRING`. Filtering depends on generated query helper semantics for unique matches.
