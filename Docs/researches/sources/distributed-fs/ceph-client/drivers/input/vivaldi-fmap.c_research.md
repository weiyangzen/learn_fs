# sources/distributed-fs/ceph-client/drivers/input/vivaldi-fmap.c

## Purpose
`vivaldi-fmap.c` provides a small exported helper for ChromeOS Vivaldi keyboard drivers to render the function-row physical map as a sysfs attribute string.

## Important APIs, Types, And Functions
`vivaldi_function_row_physmap_show()` takes `struct vivaldi_data`, iterates `function_row_physmap`, and formats each physical key code as two-digit uppercase hex separated by spaces with a trailing newline. The function is exported with `EXPORT_SYMBOL_GPL`.

## Control Flow
Callers pass their Vivaldi data and a sysfs buffer from an attribute show callback. If `num_function_row_keys` is zero, the helper returns zero bytes. Otherwise it accumulates output using `sysfs_emit_at()`.

## State And Persistence
The helper is stateless and only reads caller-owned data. It stores no persistent configuration.

## Dependencies And Integration Points
It depends on `linux/input/vivaldi-fmap.h`, sysfs formatting helpers, and module export infrastructure.

## Risks
The helper trusts that `function_row_physmap` has at least `num_function_row_keys` entries. Large maps must still fit the sysfs page-sized buffer, though `sysfs_emit_at()` is the correct bounded formatting primitive.

## Test Signals
Test zero-key output, single and multiple key formatting, spacing/newline behavior, buffer boundary behavior with large key counts, and GPL symbol linkage from a caller module.
