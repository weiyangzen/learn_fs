# sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/common_tests

Purpose: shared shell library for pstore scripts, defining logging, result accounting, paths, UUID test identity, and backend detection.

Important APIs and functions: `errexit`, `absdir`, `show_result`, `check_files_exist`, and `operate_files`. It creates `LOG_DIR`, `LOG_FILE`, `REBOOT_FLAG`, `UUID`, and `TEST_STRING_PATTERN`; `prlog()` tees output to log.

Control flow: when sourced, it creates a timestamped log directory, logs test header and UUID, reads `/sys/module/pstore/parameters/backend`, logs kernel cmdline, and exits failure if backend detection failed.

State and persistence: creates logs under `logs/<timestamp>_<uuid>/`, writes `uuid` in consumer scripts, and uses `reboot_flag` to bridge crash and post-reboot phases.

Dependencies and integration: assumes pstore module parameters are visible and shell utilities like `date`, `tee`, `ls`, and `cat`.

Risks and test signals: because code executes on source, scripts sourcing it inherit immediate failure if pstore backend is absent. Logging paths are relative to the script directory.
