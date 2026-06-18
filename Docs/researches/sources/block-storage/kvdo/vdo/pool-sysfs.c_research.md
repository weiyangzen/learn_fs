# File Research: sources/block-storage/kvdo/vdo/pool-sysfs.c

Read completely: 215 lines.

This file defines the main VDO pool sysfs kobject type and top-level pool attributes. It implements generic `show` and `store` dispatch through `struct pool_attribute`, resolves the enclosing `struct vdo` from `vdo_directory`, and exports `vdo_directory_type`.

Exposed top-level attributes are `compressing`, `discards_active`, `discards_limit`, `discards_maximum`, `instance`, `requests_active`, `requests_limit`, and `requests_maximum`. `discards_limit` is writable; its store path parses an unsigned integer, rejects overly long or invalid input, requires a value of at least 1, and delegates to `set_data_vio_pool_discard_limit()`.

The kobject release callback frees the enclosing `struct vdo` via `UDS_FREE(container_of(directory, struct vdo, vdo_directory))`. The attribute group is installed through `ATTRIBUTE_GROUPS(pool)` and assigned to `vdo_directory_type.default_groups`.

Dependencies: Linux sysfs/kobject APIs, VDO compression state, `data-vio-pool` limit/activity accessors, `dedupe.h`, `vdo.h`, and VDO memory allocation wrappers.

Security/reliability notes: writable parsing for `discards_limit` is narrow and rejects invalid values, but uses `sscanf()` and a fixed length heuristic rather than kernel numeric helpers. The release callback ties sysfs kobject lifetime directly to the `struct vdo` allocation.
