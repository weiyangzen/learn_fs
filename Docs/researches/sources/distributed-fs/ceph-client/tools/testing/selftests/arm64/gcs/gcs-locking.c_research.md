<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-locking.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-locking.c

Purpose: kselftest harness tests for locking GCS mode bits and ensuring locked modes cannot be changed.

Important APIs and functions: uses `PR_LOCK_SHADOW_STACK_STATUS`, `PR_SET_SHADOW_STACK_STATUS`, `PR_GET_SHADOW_STACK_STATUS`, and inline `my_syscall2` to zero unused syscall arguments. Tests include `lock_all_modes`, fixture variants for enable/write/push combinations, `set`, `enable_lock_disable`, `lock_enable`, and `lock_enable_disable_others`.

Control flow: main skips if no HWCAP_GCS, fails/skips if GCS already enabled because tests rely on unconfigured mode, then runs the harness. Each fixture test runs in a forked harness child and exits after assertions.

State and persistence: process-local GCS status and locked bits. No persistent files.

Dependencies and integration: uses `kselftest_harness.h`, `gcs-util.h`, Linux prctl UAPI, and harness process isolation.

Risks: cannot run after a loader or environment has already enabled GCS. Negative syscall return comparisons depend on the raw syscall wrapper returning kernel negative errno values.

Test signals: harness assertions compare returned modes and `-EBUSY` behavior for locked bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-locking.c -->
