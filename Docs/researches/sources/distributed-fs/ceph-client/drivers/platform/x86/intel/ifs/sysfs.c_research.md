<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/sysfs.c

## Purpose
Defines the IFS miscdevice sysfs ABI for loading batches, running tests, and reading last-test status/details.

## Important APIs, Types, And Functions
Attributes are `details`, `status`, `run_test`, `current_batch`, and `image_version` for scan/SBAF devices; array devices expose only `details`, `status`, and `run_test`. `ifs_sem` serializes firmware reloads and test execution.

## Control Flow
Writing a CPU number to `run_test` parses and bounds-checks it, takes `ifs_sem`, calls `do_core_test()`, and returns either count or errno. Writing `current_batch` validates `0..0xff`, stores it, then calls `ifs_load_firmware()`. Show handlers format cached state from `ifs_data`.

## State And Persistence
Sysfs exposes the latest in-memory state. `current_batch` returns `none` until a firmware image is loaded; `image_version` similarly reports `none` until load succeeds.

## Dependencies And Integration Points
Depends on `ifs.h`, sysfs device attributes, semaphore serialization, and the miscdevice groups referenced from `core.c`.

## Risks And Test Signals
Risks are user ABI regressions, insufficient serialization, and returning stale status after failed tests. Test concurrent writes to `run_test`/`current_batch`, invalid CPU/batch values, successful firmware load, array device attribute differences, and readable status strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/sysfs.c -->
