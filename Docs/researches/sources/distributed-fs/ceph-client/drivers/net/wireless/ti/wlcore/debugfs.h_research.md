# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/debugfs.h

## Purpose
`debugfs.h` declares wlcore debugfs lifecycle functions and provides macro templates for creating formatted read-only files and firmware-stat files.

## Important APIs and macros
It declares `wl1271_format_buffer()`, `wl1271_debugfs_init()`, `wl1271_debugfs_exit()`, `wl1271_debugfs_reset()`, and `wl1271_debugfs_update_stats()`. `DEBUGFS_READONLY_FILE` generates a read function and file operations for scalar values. `DEBUGFS_ADD` and `DEBUGFS_ADD_PREFIX` create files. `DEBUGFS_FWSTATS_FILE` and `DEBUGFS_FWSTATS_FILE_ARRAY` generate stats readers that refresh firmware stats before formatting a scalar or array.

## Control flow and integration
`debugfs.c` uses these helpers to reduce repetitive file-operation boilerplate. Chip-specific modules can use the firmware-stat macros to expose fields in their own firmware statistics structures while sharing the common `wl->stats.fw_stats` refresh path.

## State and persistence behavior
The header does not own state. Generated readers access `file->private_data` as `struct wl1271 *` and read live driver/statistics memory. The fixed buffer size limits formatted output for generated array readers.

## Dependencies and risks
It depends on `wlcore.h`, debugfs APIs through consuming C files, and correct type names passed to the macros. Macro-generated code can obscure bounds behavior; array output truncates once `DEBUGFS_FORMAT_BUFFER_SIZE` is reached.

## Test signals
Build coverage from generated operations, debugfs files showing expected scalar/array values, stats refresh calls before firmware-stat reads, and no truncation surprises for arrays near the buffer cap are primary signals.
