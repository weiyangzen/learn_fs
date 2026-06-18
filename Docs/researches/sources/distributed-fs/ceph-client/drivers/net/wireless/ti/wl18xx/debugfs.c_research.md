# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/debugfs.c

## Purpose
Adds wl18xx-specific debugfs files for firmware statistics, configuration export, DFS/radar test hooks, and dynamic firmware trace control.

## Important APIs, types, and functions
- `WL18XX_DEBUGFS_FWSTATS_FILE*` macros instantiate readers for fields in `struct wl18xx_acx_statistics`.
- `conf_read()` exports a binary configuration image containing wl18xx header, common wlcore config, and wl18xx private config.
- `clear_fw_stats_write()` sends `ACX_CLEAR_STATISTICS`.
- `radar_detection_write()` parses a channel and sends firmware radar debug command.
- `dynamic_fw_traces_write/read()` updates `wl->dynamic_fw_traces` and, when the device is on, sends `ACX_DYNAMIC_TRACES_CFG`.
- Optional `radar_debug_mode_write/read()` toggles certification radar debug mode and propagates it to AP roles.
- `wl18xx_debugfs_add_files()` creates the module directory, `fw_stats` tree, and control files.

## Control flow
Reader/writer callbacks acquire `wl->mutex` around shared driver state. Runtime firmware commands are skipped when `wl->state != WLCORE_STATE_ON`; commands that require active hardware resume the device with `pm_runtime_resume_and_get()` and release with `pm_runtime_put_autosuspend()`. The add-files function registers many statistic leaves then adds control files.

## State and persistence behavior
Debugfs is runtime-only. `dynamic_fw_traces_write()` persists the requested trace mask in `wl->dynamic_fw_traces` for later init/reconfiguration. `radar_debug_mode_write()` updates `wl->radar_debug_mode`. `conf_read()` snapshots current config but does not modify it.

## Dependencies and integration points
Depends on common wlcore debugfs macros, PM runtime, wlcore state/mutex, wlcore PS/debug helpers, wl18xx ACX and command helpers, and optional `CONFIG_CFG80211_CERTIFICATION_ONUS`. Called from `wl18xx_ops.debugfs_init`.

## Risks and test signals
Risks include exposing stale stats if firmware statistic layout changes, PM runtime imbalance on command failures, accepting invalid debug inputs, and certification-only radar behavior leaking into normal builds. Test signals are debugfs file creation, successful stats reads, `clear_fw_stats` while on/off, `dynamic_fw_traces` persistence across off/on states, radar debug command with valid/invalid channel text, and config dump size/magic/version.
