<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_lib.sh

## Purpose
This shell library centralizes prerequisite checks, Kconfig detection, firmware temp-file setup, proc/sysfs fallback toggles, and cleanup for firmware loader selftests.

## Important APIs, Types, And Functions
Key functions are `print_reqs_exit()`, `test_modprobe()`, `check_mods()`, `check_setup()`, `verify_reqs()`, `setup_tmp_file()`, `setup_random_file()`, `setup_random_file_fake()`, `proc_set_force_sysfs_fallback()`, `proc_set_ignore_sysfs_fallback()`, `proc_restore_defaults()`, `test_finish()`, and `kconfig_has()`. Important variables include `DIR`, `PROC_CONFIG`, `FW_FORCE_SYSFS_FALLBACK`, `FW_IGNORE_SYSFS_FALLBACK`, `OLD_TIMEOUT`, `OLD_FWPATH`, `HAS_FW_*`, `FW`, `FW_INTO_BUF`, and `NAME`.

## Control Flow
Tests call `check_mods()` to require root and load `test_firmware` and optionally `configs`, `check_setup()` to detect kernel capabilities and save old tunables, `verify_reqs()` to skip unsupported test modes, and `setup_tmp_file()` before manipulating firmware paths. `test_finish()` restores global firmware loader settings and removes temp files.

## State And Persistence
The library mutates global shell variables, `/sys/class/firmware/timeout`, `/sys/module/firmware_class/parameters/path`, `/proc/sys/kernel/firmware_config/*`, and temporary firmware directories. Cleanup is essential because those knobs are global kernel state.

## Dependencies And Integration Points
It integrates with `test_firmware`, `/proc/config.gz`, optional `configs` module, firmware loader proc/sysfs knobs, external compression tools detected by `which`, and kselftest skip code `4`.

## Risks
Unquoted variable tests such as `[ -z $PROC_SYS_DIR ]` can be sensitive to unusual values. Old heuristic Kconfig detection can overestimate fallback support when `/proc/config.gz` is absent. Cleanup must run through traps to avoid leaving global firmware settings modified.

## Test Signals
Good signals are root prerequisite enforcement, accurate skip when `test_firmware` or upload support is missing, restoration of timeout/path/fallback toggles after every script, and correct creation of temp firmware names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_lib.sh -->
