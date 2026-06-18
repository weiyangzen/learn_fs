<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/basic-gcs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/basic-gcs.c

Purpose: nolibc-style basic Guarded Control Stack selftest covering prctl status, permissions, shadow stack mapping, and fork/vfork inheritance.

Important APIs and functions: `gcs_set_status` wraps raw `prctl(PR_SET_SHADOW_STACK_STATUS)` and validates `PR_GET_SHADOW_STACK_STATUS` plus `CHKFEAT`; `read_status`, `base_enable`, `read_gcspr_el0`, `enable_writeable`, `enable_push_pop`, `enable_all`, `enable_invalid`, `map_guarded_stack`, `test_fork`, and `test_vfork` are test cases.

Control flow: skip if `HWCAP_GCS` absent, ensure GCS enabled, set kselftest plan, run test table, then attempt one final disable. Mapping test calls `map_shadow_stack` with marker/token flags and validates zero terminator, cap token, and zero-filled body.

State and persistence: process GCS status is mutated; mapped shadow stacks are `munmap`ed. Child processes inherit/check mode in fork and vfork tests.

Dependencies and integration: uses raw syscalls from nolibc, `gcs-util.h`, PR shadow stack UAPI constants, `map_shadow_stack`, and HWCAP_GCS. Built specially by the GCS Makefile.

Risks: hard-coded maximum page size of 65536 is used because nolibc lacks `sysconf`. Enabling/disabling GCS around C returns is delicate; unused syscall args are explicitly zeroed because kernel validates them.

Test signals: TAP results for each test table entry; diagnostics print mode, GCSPR, mapping bounds, cap token, and child exit details.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/basic-gcs.c -->
