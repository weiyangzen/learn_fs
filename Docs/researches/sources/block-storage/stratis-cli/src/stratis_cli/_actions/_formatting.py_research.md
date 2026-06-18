# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_formatting.py

## Role

Shared formatting helpers for table output, D-Bus optional property display, and UUID rendering.

## Main Components

- `TABLE_UNKNOWN_STRING = "???"`.
- `TOTAL_USED_FREE = "Total / Used / Free"`.
- `get_property()` unwraps D-Bus optional-style structs and returns formatted values or defaults.
- `_get_column_len()` accounts for display width with `wcwidth`.
- `_print_row()` writes aligned table rows.
- `print_table()` computes column widths and prints headings plus rows.
- `get_uuid_formatter()` returns a hyphenated or unhyphenated UUID formatter.

## Dependencies

Uses `dbus.Struct`, `wcwidth.wcswidth`, `uuid.UUID`, and standard output/file abstractions.

## Notable Risk Areas

Correct table alignment depends on display width rather than byte or codepoint length. Any new formatted values should preserve this width-aware behavior.
