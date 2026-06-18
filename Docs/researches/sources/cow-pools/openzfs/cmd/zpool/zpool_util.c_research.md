# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool_util.c

This is a small shared utility implementation for the `zpool` command.

Functions:
- `safe_malloc(size_t)`: calloc-backed allocator that exits with an internal out-of-memory message on failure.
- `safe_realloc(void *, size_t)`: realloc wrapper that exits on allocation failure.
- `zpool_no_memory()`: asserts `errno == ENOMEM`, prints a localized out-of-memory message, and exits.
- `num_logs(nvlist_t *)`: counts child vdevs whose `ZPOOL_CONFIG_IS_LOG` flag is set.
- `array64_max(uint64_t array[], unsigned int len)`: returns the maximum value in a `uint64_t` array, defaulting to 0 for an empty scan.

Behavioral notes:
- Allocation helpers terminate the process rather than propagating allocation errors, matching CLI utility style.
- `num_logs()` returns 0 when the supplied nvlist has no `ZPOOL_CONFIG_CHILDREN` array.
- `num_logs()` only counts immediate children of the supplied nvlist, not nested descendants.

Dependencies:
- `zpool_util.h` for declarations and ZFS/nvlist types.
- `gettext()` for localized error messages.
