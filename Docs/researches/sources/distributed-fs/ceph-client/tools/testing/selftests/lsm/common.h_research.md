# sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/common.h

Purpose: compatibility header for LSM syscall tests.

Important APIs/types/functions: defines inline wrappers for `lsm_get_self_attr`, `lsm_set_self_attr`, and `lsm_list_modules` when libc/kernel headers do not provide symbols. Declares common helper functions.

Control flow: no runtime control flow except direct `syscall(__NR_...)` wrappers.

State and persistence: none.

Dependencies and integration points: relies on syscall numbers and `struct lsm_ctx` from installed kernel headers.

Risks: build will fail if headers lack syscall numbers or `linux/lsm.h` support. Inline wrappers return raw syscall results and set `errno`.

Test signals: gives all LSM tests a uniform syscall invocation layer.
