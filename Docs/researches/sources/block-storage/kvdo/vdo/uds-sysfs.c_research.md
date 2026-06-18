# File Research: sources/block-storage/kvdo/vdo/uds-sysfs.c

This file builds a UDS-specific sysfs tree at `/sys/uds` with a `parameter` subdirectory. The current parameter exposed is `log_level`.

It defines minimal kobject types for empty directories and parameter files:
- `empty_object_type` has no attributes and no-op release.
- `parameter_object_type` uses custom show/store dispatch through `struct parameter_attribute`.

`buffer_to_string()` copies sysfs input, NUL-terminates it, and strips a trailing newline. The `log_level` parameter reads/writes the global UDS log level using string/priority conversion helpers.

`uds_init_sysfs()` initializes and adds `/sys/uds` and `/sys/uds/parameter`, tracking booleans so `uds_put_sysfs()` can release only successfully added kobjects on failure or module unload.
