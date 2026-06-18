# sources/distributed-fs/ceph-client/tools/testing/selftests/membarrier/membarrier_test_impl.h

Purpose: shared membarrier syscall test implementation for single-threaded and multi-threaded runners.

Important APIs/types/functions: `sys_membarrier()` wraps `syscall(__NR_membarrier)`. Test helpers cover query, invalid command/flags, global barrier, private expedited registration/use, sync-core variants when supported, global expedited registration/use, and registration tracking with `MEMBARRIER_CMD_GET_REGISTRATIONS`.

Control flow: `test_membarrier_query()` skips if syscall is disabled or lacks `MEMBARRIER_CMD_GLOBAL`. `test_membarrier_fail()` verifies invalid invocations and unregistered private expedited commands fail with `EINVAL`/`EPERM`. `test_membarrier_success()` performs global, registration, and expedited commands, conditionally including sync-core based on query bits. `test_membarrier_get_registrations()` maintains a process-local `registrations` bitmask and compares syscall output to expected cumulative registrations.

State and persistence: state is per-process membarrier registrations plus the local expected `registrations` variable. No persistent system state.

Dependencies and integration points: kernel membarrier support, syscall numbers, kselftest result APIs.

Risks: the helper named `test_membarrier_private_expedited_sync_core_success()` uses `MEMBARRIER_CMD_PRIVATE_EXPEDITED` as command while its test name says sync core; that may reflect an intentional compatibility check or a coverage bug. Registration expectations are order-dependent.

Test signals: pass lines for each command; skip on disabled/unsupported membarrier; fatal failure on unexpected errno/result.
