# sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/set-process-name.c

Purpose: tests `PR_SET_NAME` and `PR_GET_NAME` and confirms `/proc/self/task/<pid>/comm` reflects the prctl name.

Important APIs/types/functions: `set_name()`, `check_is_name_correct()`, `check_null_pointer()`, and `check_name()` are exercised by the `rename_process` kselftest.

Control flow: the test sets a normal name and empty name, verifies `PR_GET_NAME`, checks that a NULL output pointer fails, then compares `PR_GET_NAME` with the thread comm file in procfs.

State and persistence behavior: changes current task name, visible through procfs for the duration of the process.

Dependencies and integration points: uses kselftest harness, Linux prctl process-name ABI, and `/proc/self/task`.

Risks and test signals: `check_name()` uses `fscanf("%s")`, so embedded whitespace names would not round-trip, but test names avoid whitespace. File handle is not explicitly closed in that helper.
