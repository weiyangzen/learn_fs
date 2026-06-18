# File Research: sources/block-storage/kvdo/vdo/sysfs.c

This file defines kernel module parameters for VDO logging and dedupe timing. `log_level` uses custom show/store functions that translate between UDS log priorities and strings. The store path copies at most 10 bytes, strips a trailing newline, and updates the global log level.

Two uint-backed module parameters, `deduplication_timeout_interval` and `min_deduplication_timer_interval`, use `param_set_uint()` and then call dedupe setters so runtime module-param writes update dedupe behavior immediately. Parameters are registered with `module_param_cb()` and mode `0644`.
