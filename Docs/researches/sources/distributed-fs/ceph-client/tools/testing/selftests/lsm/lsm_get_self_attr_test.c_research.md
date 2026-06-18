# sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/lsm_get_self_attr_test.c

Purpose: validates `lsm_get_self_attr()` ABI behavior for current and other process security attributes.

Important APIs/types/functions: uses `struct lsm_ctx`, `LSM_ATTR_*`, `LSM_FLAG_SINGLE`, `lsm_get_self_attr()`, `lsm_list_modules()`, helper `next_ctx()`, and procfs comparison via `read_proc_attr()`.

Control flow: negative tests cover NULL size, NULL ctx, undersized buffer, invalid flag combinations, and unsupported attribute bit combinations. The basic test enumerates active LSM IDs, predicts which attributes should be returned for SELinux/Smack/AppArmor, calls `lsm_get_self_attr()` for current/exec/fscreate/keycreate/prev/sockcreate, walks variable-length `lsm_ctx` records using `next_ctx()`, and compares first returned context with matching `/proc/self/attr/*` content where available.

State and persistence: read-only process LSM attribute inspection.

Dependencies and integration points: `linux/lsm.h`, LSM syscalls, `/proc/self/attr`, `/sys/kernel/security/lsm`, and active LSM modules.

Risks: expected counts are hard-coded for known label-capable LSMs, so new LSM behavior may require updates. Tests assume ordering sufficiently matches procfs first context.

Test signals: expected errno includes `EINVAL`, `E2BIG`, and `EOPNOTSUPP`; basic pass requires count and string comparisons to match.
