# File Research: sources/block-storage/kvdo/vdo/errors.c

## Purpose
Maps UDS internal status codes and selected system errors to readable names/messages and Linux errno values. Also allows other error blocks to be registered.

## Main Behavior
- Defines built-in UDS error metadata for `UDS_ERROR_CODE_BASE` range.
- `uds_string_error()` returns a descriptive message for UDS, registered block, success, or system errno.
- `uds_string_error_name()` returns the symbolic name where available.
- `uds_map_to_system_error()` converts internal positive UDS status codes to negative Linux errno values.
- `register_error_block()` adds a non-overlapping named error-code block with metadata.

## Mappings
- Success and negative errno values pass through appropriately.
- Small positive values are treated as errno and negated.
- `UDS_NO_INDEX` and `UDS_CORRUPT_DATA` map to `-ENOENT`.
- `UDS_INDEX_NOT_SAVED_CLEANLY` and `UDS_UNSUPPORTED_VERSION` map to `-EEXIST`.
- `UDS_DISABLED` and unexpected internal errors map to `-EIO`.

## Invariants
Registered error blocks cannot overlap and block names cannot duplicate. Capacity is fixed at six blocks.
