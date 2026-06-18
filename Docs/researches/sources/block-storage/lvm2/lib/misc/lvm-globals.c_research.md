# File Research: sources/block-storage/lvm2/lib/misc/lvm-globals.c

This file stores and exposes process-wide LVM runtime settings.

Main state:
- Verbose/silent/test/debug settings.
- Filtering settings for MD, internal devices, fwraid, udev device list, external device info source.
- Command logging prefix/file strings and command name.
- Mirror sync, dmeventd monitoring, background polling, suspended-device handling.
- Static build, udev checking, retry deactivation, activation checks, PV minimum size, unknown device name, IO memory size.

Main APIs:
- `init_*()` setters for all global options.
- Getter functions such as `test_mode()`, `use_aio()`, `dmeventd_monitor_mode()`, `mirror_in_sync()`, `verbose_level()`, `debug_level()`, `pv_min_size()`, etc.
- `set_cmd_name()`, `get_cmd_name()`, `log_command_info()`, `log_command_file()`.
- `debug_class_is_logged()`.

Correctness notes:
- `init_test()` prints a warning the first time test mode is enabled.
- `init_dmeventd_monitor()` and `init_ignore_suspended_devices()` are frozen when dmeventd monitoring is disabled.
- `init_log_command()` always fills `_log_command_file` with command name and pid, while `_log_command_info` depends on configured flags.

Risks:
- All state is global process state, so callers must reset/reinitialize carefully across command contexts, callbacks, and forks.
