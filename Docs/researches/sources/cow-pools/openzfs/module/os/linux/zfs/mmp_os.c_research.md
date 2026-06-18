# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/mmp_os.c

## Purpose

Linux-specific MMP parameter hook.

## Function

- `param_set_multihost_interval(val, kp)`: parses a `uint64_t` module parameter via `spl_param_set_u64()`. If pools have been initialized (`spa_mode_global != SPA_MODE_UNINIT`), it calls `mmp_signal_all_threads()` so MMP worker threads react promptly to interval changes.

## Notes

This file contains only the OS-specific parameter callback; core MMP logic is elsewhere.
