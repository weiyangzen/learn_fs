# File Research: sources/block-storage/thin-provisioning-tools/src/grid_layout.rs

This file implements a simple right-aligned text grid renderer.

`GridLayout` accumulates rows of string fields, computes per-column widths, and writes aligned lines to any `Write`.

Important behavior:
- `field()` appends a field to the current row.
- `new_row()` finalizes the current row and updates maximum column count.
- `calc_field_widths()` computes maximum string length per column.
- `render()` right-aligns each field and appends a space after every column.

Integration points:
- Useful for CLI/status table output elsewhere in the crate.

Risks and notes:
- Uses byte length through `String::len()`, so non-ASCII display widths are not handled.
- Current row is not rendered unless `new_row()` has been called.
