# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/platform/x86/intel/ifs/test_ifs.sh

## Purpose
Hardware-dependent Intel IFS selftest. It validates driver sysfs creation, firmware image loading, corrupt-image rejection, scan execution across sibling CPUs, repeated same-CPU interval behavior, and optional Array BIST mode.

## Important APIs, Types, And Functions
Uses `/sys/devices/virtual/misc/intel_ifs_0` and `_1`, `/sys/devices/system/cpu`, `/lib/firmware/intel/ifs_0`, `current_batch`, `run_test`, `status`, `details`, `modprobe intel_ifs`, CPU online controls, and kselftest exit codes. Key functions include `append_log()`, `online_offline_cpu_list()`, `ifs_cleanup()`, `do_cmd()`, `test_exit()`, `online_all_cpus()`, `get_cpu_fms()`, `check_cpu_ifs_support_interval_time()`, `check_ifs_loaded()`, image load tests, `ifs_test_cpu()`, `ifs_test_cpus()`, `test_ifs_same_cpu_loop()`, `test_ifs_scan_available_imgs()`, and `test_ifs()`.

## Control Flow
The script prepares CPU/model state, onlines CPUs, selects a random CPU and default scan image, loads the module, checks sysfs, tests original and corrupt scan images, runs all available scan images on sibling representatives, loops same-CPU scans with model-dependent delay, and runs Array BIST if the mode directory exists. Cleanup restores images, CPU offline state, and module state, then summarizes PASS/SKIP/FAIL lines.

## State And Persistence
It can modify CPU online state, load/unload `intel_ifs`, write firmware image files during corrupt-image testing, and write a temporary `/tmp/ifs_logs.$$`. Backup/restore flags track whether a firmware image must be restored.

## Dependencies And Integration Points
Requires supported Intel Family 6 platform, IFS driver, firmware images, root, writable firmware directory for negative image tests, and sysfs CPU controls.

## Risks
This test is invasive: it onlines CPUs, modifies firmware image files, and waits platform-specific scan intervals. `eval` in `do_cmd()` requires trusted command construction. Failure during image corruption must execute cleanup to avoid leaving a bad image.

## Test Signals
Signals include sysfs directory existence, successful `current_batch` writes, rejected corrupt images, per-CPU `status=pass`, details output, Array BIST availability/skip, and final summarized pass/skip/fail counts.
