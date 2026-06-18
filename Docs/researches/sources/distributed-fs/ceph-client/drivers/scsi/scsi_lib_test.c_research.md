# sources/distributed-fs/ceph-client/drivers/scsi/scsi_lib_test.c

Purpose: provides KUnit coverage for the passthrough retry policy implemented by the static `scsi_check_passthrough()` helper in `scsi_lib.c`. It is included directly by `scsi_lib.c` when `CONFIG_SCSI_LIB_KUNIT_TEST` is enabled so the tests can reach that static helper.

Important APIs/types/functions: the suite `scsi_lib` contains `scsi_lib_test_check_passthough()`, which calls focused subtests for multiple sense definitions, wildcard sense/status/host/result matching, total retry limits, mixed per-failure and total limits, and retry reset behavior. Test commands are synthetic `struct scsi_cmnd` instances with local sense buffers populated by `scsi_build_sense()`.

Control flow: each subtest builds `struct scsi_failure` arrays, wraps them in `struct scsi_failures`, sets `sc.result` and sense data, then asserts whether `scsi_check_passthrough()` returns `-EAGAIN` or zero. Retry-limit tests call the helper repeatedly to verify per-entry `retries` and aggregate `total_retries` accounting, then use `scsi_failures_reset_retries()` to reset state.

State and persistence: only in-test stack objects are mutated. The tests intentionally exercise mutation of `failure->retries` and `failures->total_retries`; no kernel device state or persistent data is used.

Dependencies and integration: depends on KUnit, SCSI protocol constants, `struct scsi_failure`, `scsi_build_sense()`, and direct inclusion from `scsi_lib.c`. The test validates behavior used by `scsi_execute_cmd()` callers that pass `scsi_exec_args.failures`.

Risks: because it is included into `scsi_lib.c`, symbol visibility and compile options matter. The test name contains the misspelling `passthough`, which is harmless but easy to miss in test filtering. It does not cover concurrent callers or real request execution.

Test signals: enable `CONFIG_SCSI_LIB_KUNIT_TEST` and run the `scsi_lib` KUnit suite. Extend cases when new wildcard constants, retry counters, or passthrough failure semantics are added.
