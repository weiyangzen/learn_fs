# sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/lsm_set_self_attr_test.c

Purpose: negative ABI tests for `lsm_set_self_attr()`.

Important APIs/types/functions: uses `lsm_set_self_attr()`, `lsm_get_self_attr()` to prepare a context when label-capable LSMs are active, `LSM_ATTR_CURRENT`, `LSM_ATTR_PREV`, and kselftest harness assertions.

Control flow: tests reject NULL context, too-small size, nonzero flags, and overset attribute bits. Where active LSM label contexts exist, the test first fetches a valid current context to make the subsequent set failure target meaningful.

State and persistence: attempts to set self attributes but only tests failing invocations, so no intended process security state mutation.

Dependencies and integration points: LSM syscalls and active LSMs. Shares helper behavior with the get/list tests.

Risks: assertions only check failure, not exact errno, so regressions that still fail with the wrong reason may pass.

Test signals: all listed invalid `lsm_set_self_attr()` calls must return `-1`.
