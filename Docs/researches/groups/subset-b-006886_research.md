# Research: subset-b-006886

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync.c

## Purpose
Provides the userspace helper layer used by the sync selftests. It wraps Linux `sync_file` ioctls and the debugfs `sw_sync` test driver so the individual test files can create timelines, create fences, merge fences, wait on fence file descriptors, and inspect fence status counts without duplicating ioctl setup.

## Important APIs, Types, And Functions
Public helpers are `sync_wait()`, `sync_merge()`, `sync_fence_size()`, `sync_fence_count_with_status()`, `sw_sync_timeline_create()`, `sw_sync_timeline_inc()`, `sw_sync_timeline_is_valid()`, `sw_sync_timeline_destroy()`, `sw_sync_fence_create()`, `sw_sync_fence_is_valid()`, and `sw_sync_fence_destroy()`. The file defines local `SW_SYNC_IOC_CREATE_FENCE` and `SW_SYNC_IOC_INC` ioctl numbers plus `struct sw_sync_create_fence_data`, while consuming `struct sync_merge_data`, `struct sync_file_info`, and `struct sync_fence_info` from `<linux/sync_file.h>`.

## Control Flow
Creation paths open `/sys/kernel/debug/sync/sw_sync`, then create fences by issuing `SW_SYNC_IOC_CREATE_FENCE` against the timeline fd. `sync_merge()` submits `SYNC_IOC_MERGE` on the first fence fd and returns the kernel-provided merged fence fd. `sync_file_info()` performs the two-stage `SYNC_IOC_FILE_INFO` query: first to learn `num_fences`, then with a caller-allocated `sync_fence_info` array attached through the 64-bit pointer field. Status helpers iterate that returned array and free all temporary allocations before returning.

## State And Persistence
The only persistent state is in kernel-owned file descriptors: timeline fds, fence fds, and merged fence fds. Userspace state is temporary allocation for `SYNC_IOC_FILE_INFO`. The validity helpers use `fcntl(F_GETFD)` and destruction is just `close()` when the fd is valid.

## Dependencies And Integration Points
Depends on debugfs `sw_sync` support, `SYNC_IOC_*` ABI definitions, libc `poll`, `open`, `ioctl`, `fcntl`, and `close`, and the public prototypes in `sync.h` plus `sw_sync.h`. All sync allocation, merge, wait, and stress tests call through this file.

## Risks
The helper assumes the debugfs sw_sync node exists and is accessible, so tests skip or fail depending on mount/permission state. The pointer cast through `uint64_t` must match the kernel ABI. `sync_fence_size()` returns `0` both for an empty fence set and for info-query failure, while `sync_fence_count_with_status()` returns `-1` on failure, so callers need to distinguish those semantics. Tests that forget to close merged fds can exhaust file descriptors during stress runs.

## Test Signals
Good signals are successful timeline/fence allocation, `poll()` returning timeout before signaling and readiness after timeline increments, `SYNC_IOC_FILE_INFO` reporting expected active/signaled/error counts, and stable behavior under repeated merges in the stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync.h

## Purpose
Declares the shared sync helper interface consumed by the sync selftest source files. It keeps the tests independent from direct `sync_file` ioctl details while exposing fence wait, merge, size, and status-count operations.

## Important APIs, Types, And Functions
Defines status constants `FENCE_STATUS_ERROR`, `FENCE_STATUS_ACTIVE`, and `FENCE_STATUS_SIGNALED`, matching the kernel sync-file status conventions used by `struct sync_fence_info.status`. Declares `sync_wait()`, `sync_merge()`, `sync_fence_size()`, and `sync_fence_count_with_status()`.

## Control Flow
This header has no runtime control flow. Compile units include it and link against `sync.c`; tests pass fence fds returned by `sw_sync_fence_create()` or `sync_merge()` into the declared helpers.

## State And Persistence
No state is held here. The status constants are a stable contract between test assertions and kernel-reported fence state.

## Dependencies And Integration Points
Integrated with `sync.c`, `sw_sync.h`, and all sync test cases. It intentionally does not include Linux ioctl headers itself, keeping callers focused on the small helper API.

## Risks
If kernel sync status values change, the hard-coded constants would silently invalidate assertions. The header also exposes only integer fd APIs, so ownership and close responsibilities remain implicit in callers.

## Test Signals
Compilation of all sync selftests against this header and correct active/signaled/error counts in the linked tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_alloc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_alloc.c

## Purpose
Contains allocation-focused sync selftests that verify the `sw_sync` debugfs driver can allocate timelines and fences and rejects fence creation on an invalid timeline fd.

## Important APIs, Types, And Functions
Implements `test_alloc_timeline()`, `test_alloc_fence()`, and `test_alloc_fence_negative()`. These use `sw_sync_timeline_create()`, `sw_sync_timeline_is_valid()`, `sw_sync_fence_create()`, `sw_sync_fence_is_valid()`, and the destruction helpers, with assertions from `synctest.h`.

## Control Flow
Each test creates a timeline, validates it, then optionally creates and validates a fence. The negative case intentionally calls `sw_sync_fence_create(-1, ...)` and expects a negative return. Cleanup closes any valid fence and timeline before returning success.

## State And Persistence
State is limited to local file descriptors. The kernel owns the actual timeline and fence objects until their fds are closed.

## Dependencies And Integration Points
Depends on the shared helper layer in `sync.c`, the `sw_sync` test driver node, and the kselftest runner in `sync_test.c`, which invokes these functions in isolated child processes.

## Risks
The tests assume fd validity checks are enough to prove allocation success. `test_alloc_fence_negative()` checks `timeline > 0` rather than the shared validity helper, so an unusual valid fd `0` would be treated as failure. The negative fence fd is passed to destroy, which is safe because the helper validates first.

## Test Signals
Pass signals are valid timeline fd allocation, valid fence fd allocation, and failure from fence creation with fd `-1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_fence.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_fence.c

## Purpose
Tests basic fence wait and merge semantics on a single sw_sync timeline. It validates timeout behavior before a fence reaches its target value, signaling after enough timeline increments, and merged-fence behavior where the merged fence tracks the maximum sync point on one timeline.

## Important APIs, Types, And Functions
Implements `test_fence_one_timeline_wait()` and `test_fence_one_timeline_merge()`. Key calls are `sw_sync_timeline_create()`, `sw_sync_fence_create()`, `sw_sync_timeline_inc()`, `sync_wait()`, `sync_merge()`, and `sync_fence_count_with_status()`.

## Control Flow
The wait test creates a fence at value `5`, verifies immediate zero-timeout waits return timeout while the timeline is below 5, increments by `1` and then `4`, and expects readiness once the target is reached. It then increments further to ensure already-signaled fences remain waitable. The merge test creates fences at values 1, 2, and 3, merges them, verifies active counts, then advances the timeline one step at a time and checks the merged fence remains active until the last component has signaled.

## State And Persistence
The persistent state is in kernel timeline progression and fence fds. Local variables retain the merged fd chain and are closed at the end.

## Dependencies And Integration Points
Uses the sync helper ABI and is run by `sync_test.c`. It is a baseline for the later multi-timeline and stress tests.

## Risks
The merge test has repeated assertions against `a` where messages mention `b`, `c`, and `d`; this limits diagnostic precision and may miss per-fence count regressions before the later `d` checks. Failed intermediate `sync_merge()` calls could leak earlier fds or feed invalid fds into the next merge.

## Test Signals
Expected signals are `sync_wait(..., 0)` returning `0` for unsignaled fences, returning positive for signaled fences, active count dropping only as timeline values reach component sync points, and merged fence status becoming fully signaled at the maximum component value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_merge.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_merge.c

## Purpose
Validates the special case of merging a fence with itself. The test ensures duplicate merge inputs do not create duplicate unsignaled points and that the merged fence signals once the original fence's timeline value is reached.

## Important APIs, Types, And Functions
Implements `test_fence_merge_same_fence()`, using sw_sync timeline and fence helpers, `sync_merge()`, and `sync_fence_count_with_status()`.

## Control Flow
The test creates one timeline and one fence at value `5`, merges the same fd with itself, verifies the merged fd is usable, checks it is not already signaled, increments the timeline by `5`, then expects exactly one signaled fence in the merged object before closing both fds and the timeline.

## State And Persistence
Only local fd state is held. Kernel state is the single timeline counter and the original/merged fence objects.

## Dependencies And Integration Points
Runs under `sync_test.c` after the single-timeline wait and merge tests. It depends on the kernel sync merge implementation deduplicating or coalescing same-fence inputs.

## Risks
The validity check after merge calls `sw_sync_fence_is_valid(fence)` instead of checking `merged`, so a failed merge could be less directly diagnosed before the count assertions. The test also assumes the merged duplicate has one signaled component, not two duplicate components.

## Test Signals
The key signal is `sync_fence_count_with_status(merged, FENCE_STATUS_SIGNALED) == 1` after the timeline increment, with no early signaled count before increment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_merge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_stress_consumer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_stress_consumer.c

## Purpose
Implements a multi-producer/single-consumer stress test for sw_sync. It exercises large numbers of fence creations, waits, timeline increments, merges, and cross-thread coordination under file descriptor pressure.

## Important APIs, Types, And Functions
Important functions are `test_consumer_stress_multi_producer_single_consumer()`, `mpsc_producer_thread()`, `mpcs_consumer_thread()`, and `busy_wait_on_fence()`. Shared state lives in `test_data_mpsc` with iteration count, thread count, counter, a consumer timeline, producer timeline array, and a pthread mutex.

## Control Flow
The top-level test creates one consumer timeline and five producer timelines, initializes global shared state, starts five producer threads, and runs the consumer loop in the main thread. Producers repeatedly create fences on the consumer timeline and wait until the consumer releases each iteration, then increment a protected shared counter and advance their producer timeline. The consumer creates one fence per producer timeline for the current iteration, merges them into a single fence, waits until all producers have advanced, verifies the counter equals `threads * iteration`, and advances the consumer timeline to release producers for the next round.

## State And Persistence
State persists in global `test_data_mpsc` across all threads. The counter is protected by a mutex for increments but read by the consumer without taking the mutex after synchronization through producer fences. Kernel state includes six timelines and many transient fences/merged fences.

## Dependencies And Integration Points
Depends on pthreads, sync helper functions, and enough process file descriptors for many transient fences. The test runner isolates it in a child process.

## Risks
This test is sensitive to fd limits and scheduling. `busy_wait_on_fence()` repeatedly queries fence info and can be CPU-heavy. Some thread functions return integer values through a `void *` pthread signature cast, which is conventional in this test tree but not type-clean. The branch choosing wait mode uses `(iterations + id) % 8`, so with the current constants it varies by producer id rather than by loop iteration.

## Test Signals
Signals are no fence error status, producer waits completing, merged producer fences signaling each iteration, shared counter exactly matching the expected producer count, and no fd exhaustion during `1 << 12` iterations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_stress_consumer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_stress_merge.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_stress_merge.c

## Purpose
Stress-tests sync-file merging across many timelines by randomly generating thousands of sync points, merging them into one fence, and checking the final merged fence contains one outstanding point per touched timeline.

## Important APIs, Types, And Functions
Implements `test_merge_stress_random_merge()`. It uses `rand()`, `srand(time(NULL))`, arrays of 32 timelines and latest sync points, `sw_sync_fence_create()`, `sync_merge()`, `sync_fence_size()`, `sync_wait()`, and `sw_sync_timeline_inc()`.

## Control Flow
The test creates 32 timelines and an initial fence, then performs 32k iterations. Each iteration selects a random timeline and random sync point, tracks the maximum sync point seen for that timeline, creates a temporary fence, merges it into the aggregate fence, and destroys the old fds. After the loop it counts touched timelines, checks the aggregate fence size equals that count, advances each touched timeline to its tracked maximum while verifying the aggregate is still unsignaled before each increment, and finally expects the aggregate fence to signal.

## State And Persistence
Local arrays hold timeline fds and the latest required sync point per timeline. Kernel fence state is repeatedly replaced by a new merged fd, and only the latest aggregate survives each iteration.

## Dependencies And Integration Points
Depends on sw_sync merge coalescing by timeline and sync point, and on the helper layer reporting accurate fence sizes. It is the broadest merge coverage in the sync suite.

## Risks
The random seed makes exact coverage non-reproducible. Very large random sync points are passed directly to `sw_sync_timeline_inc()`, so integer range and cumulative counter behavior matter. The test may leak or mis-handle fds if a merge fails mid-loop, because the code continues to replace `fence` after each merge assertion point.

## Test Signals
Key signals are aggregate fence size equaling the number of timelines touched, aggregate wait timing out before all required increments, and successful wait after all timelines have advanced to their max sync point.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_stress_merge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_stress_parallelism.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_stress_parallelism.c

## Purpose
Tests sw_sync as a two-thread sequencing primitive on one shared timeline. It verifies that alternating fence waits and timeline increments can serialize writes to a shared counter for many iterations.

## Important APIs, Types, And Functions
Implements `test_stress_two_threads_shared_timeline()` and `test_stress_two_threads_shared_timeline_thread()`. Shared state is `test_data_two_threads` with `iterations`, `timeline`, and `counter`.

## Control Flow
The main test creates one timeline, initializes the counter and iteration count (`1 << 16`), then starts two pthreads with ids 0 and 1. Each thread repeatedly creates a fence for `i * 2 + thread_id`, waits forever for that value to be reached, validates the shared counter equals the expected turn value, increments the counter, advances the timeline by one to release the other thread, and closes the fence. After both threads join, the main test checks the counter reached `iterations * 2`.

## State And Persistence
The shared counter is not protected by a mutex; the test relies entirely on timeline/fence ordering for visibility and serialization. Kernel state is the shared timeline and per-iteration fences.

## Dependencies And Integration Points
Depends on pthread scheduling, the sw_sync timeline increment semantics, and `sync_wait(..., -1)` blocking until a fence signals.

## Risks
Because the counter is ordinary shared memory without atomic or mutex access, the test assumes the synchronization through syscalls is enough for memory visibility on target architectures. Any missed timeline increment deadlocks both threads. The long iteration count makes it good at finding races but expensive when the kernel stalls.

## Test Signals
Expected signals are every wait completing, the counter always matching the expected turn, and final counter value exactly `131072`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_stress_parallelism.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_test.c

## Purpose
Provides the kselftest runner for the sync test suite. It checks environment support, runs each test function in an isolated child process, reports TAP-style kselftest results, and exits pass/fail/skip.

## Important APIs, Types, And Functions
Important functions are `run_test()`, `sync_api_supported()`, and `main()`. It uses `RUN_TEST()` from `synctest.h`, kselftest APIs such as `ksft_print_header()`, `ksft_set_plan()`, `ksft_test_result_pass()`, `ksft_test_result_fail()`, `ksft_get_fail_cnt()`, `ksft_exit_skip()`, `ksft_exit_fail_msg()`, and `ksft_exit_pass()`.

## Control Flow
`main()` prints the header, checks that `/sys/kernel/debug/sync/sw_sync` is present and accessible, sets a plan for ten tests, and invokes allocation, fence, wait, and stress tests. `run_test()` forks before executing each test; the parent waits and converts an exit status of zero into pass and nonzero or abnormal exit into failure. At the end it fails if any child test failed, otherwise exits pass.

## State And Persistence
The runner holds only process-local result state through kselftest counters. Forking isolates leaked fds, crashed tests, and mutated globals in each child.

## Dependencies And Integration Points
Depends on debugfs sw_sync, root or sufficient debugfs permissions, `../kselftest.h`, and all test prototypes from `synctest.h`. It is the executable listed by the sync selftest Makefile outside this assigned set.

## Risks
The plan is hard-coded as `3 + 7`; adding or removing tests requires updating it. A test terminated by signal is reported only as generic failure. `sync_api_supported()` skips on missing node or EACCES but fails other `stat()` errors.

## Test Signals
Useful signals are kselftest plan count matching executed tests, per-test pass/fail lines, skip when the sync framework is absent or inaccessible, and final aggregate pass only when no child test reports failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_wait.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_wait.c

## Purpose
Tests waiting on a merged fence built from three independent timelines. It ensures merged fence status tracks each component independently and only becomes fully signaled after all timelines have reached their target values.

## Important APIs, Types, And Functions
Implements `test_fence_multi_timeline_wait()`. It uses three sw_sync timelines, three fences, two `sync_merge()` calls, `sync_fence_count_with_status()`, `sync_wait()`, and timeline increments.

## Control Flow
The test creates timelines A, B, and C, creates a fence at value 5 on each, merges them into one fence, and checks that the merged fence has three active points. It verifies immediate wait times out, then increments each timeline by 5 in sequence and checks active/signaled counts transition from 2/1 to 1/2 to 0/3. A final wait with timeout 100 must succeed before all fds and timelines are destroyed.

## State And Persistence
Kernel state is distributed across three timeline counters and the merged fence fd. Local state records active/signaled counts for assertions.

## Dependencies And Integration Points
Builds on `sync.c` helpers and complements the single-timeline merge tests by validating independent timeline composition.

## Risks
The second `sync_merge()` overwrites `merged` without closing the first merged fd, so the test may leak one fd in the child process. Return values from timeline increments are not asserted in this file, meaning a failed increment would surface indirectly through count mismatches.

## Test Signals
Expected signals are three active components before increments, per-timeline count transitions after each increment, and a positive wait result once all three components are signaled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/synctest.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/synctest.h

## Purpose
Defines the shared test harness surface for the sync selftests: assertion and run macros plus prototypes for every test function compiled into the runner.

## Important APIs, Types, And Functions
`ASSERT(cond, msg)` prints a kselftest error message and returns `1` from the current test on failure. `RUN_TEST(x)` passes a function and its name to `run_test()`. The header declares allocation, fence, merge, wait, parallelism, consumer, and random-merge stress test functions.

## Control Flow
The macros shape control flow in all test implementations. Failed assertions return immediately from the test function, which becomes the child process exit status consumed by `sync_test.c`.

## State And Persistence
No state is held here. It centralizes the convention that test success is return `0` and failure is return `1`.

## Dependencies And Integration Points
Includes `../kselftest.h` for output and integrates all sync `.c` test files with the single runner. It relies on `run_test()` being visible in `sync_test.c` before macro expansion.

## Risks
`ASSERT` returns from the enclosing function, so using it in helper functions only signals failure if callers propagate the return value. It cannot run cleanup automatically, making fd cleanup after failed mid-test assertions dependent on process isolation.

## Test Signals
Compilation and clear kselftest `[ERROR]` messages from failed assertions are the primary signals. The full prototype list also protects against missing test objects at link time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/synctest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/syscall_user_dispatch/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/syscall_user_dispatch/Makefile

## Purpose
Builds and installs the syscall user dispatch selftests.

## Important APIs, Types, And Functions
Defines `top_srcdir`, `INSTALL_HDR_PATH`, `LINUX_HDR_PATH`, adds `-Wall` and the installed UAPI include path to `CFLAGS`, sets `TEST_GEN_PROGS := sud_test sud_benchmark`, and includes `../lib.mk`.

## Control Flow
The kselftest build framework compiles both C programs as generated test binaries and handles install/run targets through `lib.mk`.

## State And Persistence
No runtime state. Build outputs are the two generated programs.

## Dependencies And Integration Points
Depends on kernel headers under `usr/include` and the common kselftest Makefile. It pairs with `config`, which requests `CONFIG_GENERIC_ENTRY=y`.

## Risks
If installed headers do not expose recent `PR_SET_SYSCALL_USER_DISPATCH` constants, the C files provide fallbacks, but syscall numbers and architecture behavior still depend on target headers and libc.

## Test Signals
Successful compilation of `sud_test` and `sud_benchmark` with `-Wall` and inclusion in the kselftest generated-program list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/syscall_user_dispatch/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/syscall_user_dispatch/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/syscall_user_dispatch/config

## Purpose
Declares the kernel configuration dependency for syscall user dispatch selftests.

## Important APIs, Types, And Functions
Contains `CONFIG_GENERIC_ENTRY=y`, the infrastructure required by syscall user dispatch entry handling.

## Control Flow
No control flow. The kselftest configuration tooling reads this file to indicate required kernel support.

## State And Persistence
No state.

## Dependencies And Integration Points
Pairs with `sud_test.c` and `sud_benchmark.c`, which call `prctl(PR_SET_SYSCALL_USER_DISPATCH, ...)`.

## Risks
This config is necessary but not a complete guarantee that the runtime architecture supports all tested dispatcher modes or signal-return behavior.

## Test Signals
The requested config appears in the kernel build configuration; runtime tests then confirm actual support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/syscall_user_dispatch/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/syscall_user_dispatch/sud_benchmark.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/syscall_user_dispatch/sud_benchmark.c

## Purpose
Benchmarks syscall user dispatch overhead while also smoke-testing SIGSYS trapping and selector behavior. It compares repeated native `sysinfo()` syscall timing before and after enabling dispatch.

## Important APIs, Types, And Functions
Important globals are `selector`, `trapped_call_count`, `native_call_count`, `factor`, and architecture-specific dispatcher symbols. Functions include `one_sysinfo_step()`, `calibrate_set()`, `perf_syscall()`, `handle_sigsys()`, and `main()`. It uses `prctl(PR_SET_SYSCALL_USER_DISPATCH, ...)`, `sigaction(SIGSYS, ...)`, `syscall(MAGIC_SYSCALL_1)`, `clock_gettime()`, and `sysinfo()`.

## Control Flow
`main()` calibrates a loop to roughly five seconds, measures baseline syscall time, installs a SIGSYS handler, enables syscall user dispatch with an allowed dispatcher range, blocks dispatch through `selector`, and performs a deliberately invalid syscall to verify trapping. The handler unblocks dispatch, records whether the trapped syscall was the magic one, and on x86_64 emits inline assembly to test returning through a dispatcher-area syscall with the selector blocked. The program then unblocks dispatch, measures syscall time again, and reports overhead.

## State And Persistence
State is process-global and volatile during the benchmark: selector byte controls dispatch, counters record trapped/native unexpected syscalls, and `factor` controls iteration count. No state persists beyond process exit.

## Dependencies And Integration Points
Depends on syscall user dispatch prctl support, SIGSYS signal ABI fields, architecture-specific syscall argument/return behavior, and x86 dispatcher labels for `TEST_BLOCKED_RETURN`. It integrates with kselftest as a generated benchmark binary rather than the main pass/fail harness.

## Risks
The benchmark is architecture-sensitive and uses inline assembly on x86_64. `printf` is avoided in the signal handler except via `snprintf` plus `write`, but `snprintf` itself is not async-signal-safe. Timing is noisy and calibration scales `factor` in coarse steps. The fallback syscall number must remain invalid on the target architecture.

## Test Signals
Signals include a successful prctl enable, at least one trapped magic syscall, selector still blocked after the blocked-return test on supported architectures, zero unexpected native dispatches, and a printed overhead percentage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/syscall_user_dispatch/sud_benchmark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/syscall_user_dispatch/sud_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/syscall_user_dispatch/sud_test.c

## Purpose
Provides kselftest harness coverage for syscall user dispatch API behavior, signal delivery, emulated syscall return, dispatcher enable/disable, and inclusive/exclusive dispatch ranges.

## Important APIs, Types, And Functions
Uses `kselftest_harness.h` tests: `dispatch_trigger_sigsys`, `bad_prctl_param`, `dispatch_and_return`, `bad_selector`, `disable_dispatch`, `direct_dispatch_range`, and `dispatch_range`. Helpers include `prctl_valid()`, `prctl_invalid()`, `handle_sigsys()`, `setup_sigsys_handler()`, and `test_range()`. Globals `glob_sel`, `nr_syscalls_emulated`, `si_code`, `si_errno`, and `syscall_addr` capture handler state.

## Control Flow
Signal tests enable dispatch, block selector state, and expect SIGSYS termination or catchable handler paths. Parameter tests exercise invalid op codes, invalid off/size/selector combinations, overflow ranges, valid off mode, and inclusive mode validation. `dispatch_and_return()` verifies a magic syscall is a normal `-1` when dispatch is allowed, then becomes an emulated return value when dispatch is blocked and SIGSYS handling adjusts state. Range tests first learn the syscall instruction address from the handler and then verify exclusive and inclusive allowed ranges dispatch or bypass as expected.

## State And Persistence
State is process-global across individual test bodies but reset by tests before use. The selector byte is the kernel-observed switch. Handler-captured `syscall_addr` persists for later range tests.

## Dependencies And Integration Points
Depends on `PR_SET_SYSCALL_USER_DISPATCH` constants, `SYS_USER_DISPATCH` signal code, architecture-specific `ucontext_t` register adjustment for RISC-V, and kselftest harness signal-test support. The Makefile builds it as `sud_test`.

## Risks
Some behavior is architecture-specific: the comment notes syscall return emulation assumes `syscall(x) == x` except where adjusted for RISC-V. Test ordering matters because `dispatch_range()` relies on `syscall_addr` having been populated. Unsupported kernels are reported through failed `ASSERT_EQ(0, prctl(...))` blocks with explanatory logs rather than explicit skip in every path.

## Test Signals
Passing signals are SIGSYS raised when expected, invalid prctl parameters returning `EINVAL` or `EFAULT`, magic syscall emulation incrementing `nr_syscalls_emulated`, dispatch disable allowing `sysinfo`, direct allowed ranges bypassing dispatch, and JSON-free kselftest harness pass/fail output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/syscall_user_dispatch/sud_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sysctl/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sysctl/Makefile

## Purpose
Registers the sysctl selftest shell script with kselftest.

## Important APIs, Types, And Functions
Defines a no-op `all` target so plain `make` does not run tests, sets `TEST_PROGS := sysctl.sh`, includes `../lib.mk`, and defines an empty `clean` target. Comments document the expectation that `kernel.sysctl_writes_strict=1`.

## Control Flow
Build-time control is delegated to kselftest `lib.mk`; runtime is entirely in `sysctl.sh`.

## State And Persistence
No state is persisted by the Makefile.

## Dependencies And Integration Points
Pairs with `config`, which requests `CONFIG_TEST_SYSCTL=m`, and with the shell script that modprobes `test_sysctl` when needed.

## Risks
The no-op `all` target is deliberate; changing it could make sysctl tests run during build by accident. The tests require root and can mutate production sysctls during execution.

## Test Signals
`make kselftest` discovers `sysctl.sh` as a test program and does not build binaries for this directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sysctl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sysctl/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sysctl/config

## Purpose
Declares the kernel module dependency for sysctl selftests.

## Important APIs, Types, And Functions
Contains `CONFIG_TEST_SYSCTL=m`, requesting the `test_sysctl` module that creates `/proc/sys/debug/test_sysctl` targets.

## Control Flow
No runtime control flow. `sysctl.sh` uses this file for user-facing skip guidance in built-in-only boot parameter tests.

## State And Persistence
No state.

## Dependencies And Integration Points
Integrated with `sysctl.sh` and kernel selftest config tooling.

## Risks
Some tests require the test sysctl support to be built in rather than loaded as a module, so this module config is not sufficient for every test case.

## Test Signals
Availability of the `test_sysctl` module and creation of the expected debug sysctl tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sysctl/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sysctl/sysctl.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sysctl/sysctl.sh

## Purpose
Runs a comprehensive shell-based suite against the proc sysctl interface and the `test_sysctl` kernel test module. It validates numeric, string, bitmap, boot parameter, registration, mount-point, empty-directory, and u8 range-check behavior.

## Important APIs, Types, And Functions
Important globals include `ALL_TESTS`, `SYSCTL`, `PROD_SYSCTL`, `WRITES_STRICT`, `PAGE_SIZE`, `MAX_DIGITS`, `INT_MAX`, `UINT_MAX`, `TARGET`, `TEST_STR`, `ORIG`, and `rc`. Setup helpers are `test_reqs()`, `allow_user_defaults()`, `check_production_sysctl_writes_strict()`, and `load_req_mod()`. Validation helpers include `reset_vals()`, `set_orig()`, `verify()`, `verify_diff_proc_file()`, `check_failure()`, `run_numerictests()`, `run_wideint_tests()`, `run_limit_digit*()`, `run_stringtests()`, and `run_bitmaptest()`. Test entry points are `sysctl_test_0001()` through `sysctl_test_0012()`.

## Control Flow
The script requires root plus `perl`, `getconf`, and `diff`, sets defaults, forces or checks `kernel/sysctl_writes_strict`, loads `test_sysctl` if `/proc/sys/debug/test_sysctl` is missing, installs an EXIT trap to restore the original target and writes-strict value, then parses CLI arguments. Default mode runs all enabled tests from `ALL_TESTS`; `-t`, `-s`, `-c`, and `-w` select count or watch modes. Individual tests construct `TARGET`, reset it, save original values, then run reusable numeric/string/bitmap boundary tests or direct structural checks.

## State And Persistence
The script mutates live sysctl files under `/proc/sys/debug/test_sysctl` and may temporarily set `/proc/sys/kernel/sysctl_writes_strict` to `1`, restoring the old value in `test_finish()`. It uses temporary files from `mktemp` for expected data and proc dumps. Module loading can persist the `test_sysctl` module beyond the script's lifetime.

## Dependencies And Integration Points
Depends on root privileges, debug test sysctl module or built-in support, production procfs, shell utilities, dmesg for u8 range checks, and kselftest skip code 4. It integrates with `Makefile` as `TEST_PROGS`.

## Risks
The script touches a production sysctl setting and must restore it reliably; abrupt termination outside the EXIT trap could leave strict writes changed. Some variables are unquoted in tests, which is typical here but fragile. `run_bitmaptest()` uses random lengths and bit ranges, making exact failures less reproducible. Boot-parameter test 0007 is skipped unless the kernel was booted with the expected built-in parameter. dmesg-based checks can be polluted by previous runs.

## Test Signals
Signals include successful write/verify/reset cycles, strict rejection of out-of-range wide integer inputs, PAGE_SIZE space-prefix boundary behavior, string maxlen/null-termination checks, bitmap round-trip diff, expected skips for unavailable boot-param conditions, correct missing directories for unregister/mount error tests, and exactly one u8 over/under range warning in dmesg.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sysctl/sysctl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/Makefile

## Purpose
Registers tc-testing assets with kselftest.

## Important APIs, Types, And Functions
Adds `tdc.sh` to `TEST_PROGS` and installs files matching `action-ebpf`, `tdc*.py`, `Tdc*.py`, `plugins`, `plugin-lib`, `tc-tests`, and `scripts` through `TEST_FILES`, then includes `../lib.mk`.

## Control Flow
No custom build control beyond kselftest file staging. The actual runner is `tdc.sh`/Python code outside this assigned set.

## State And Persistence
No runtime state in this file.

## Dependencies And Integration Points
Depends on kselftest installation preserving Python plugins, JSON tests, helper scripts, and the eBPF action object. It pairs with `config` for kernel networking feature requirements.

## Risks
Missing a file pattern here can make installed tests fail even though they work in-tree. The Makefile assumes `action-ebpf` exists or is produced elsewhere.

## Test Signals
Installed kselftest directories contain the runner, Python modules, plugin libraries, JSON test cases, scripts, and eBPF helper object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/TdcPlugin.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/TdcPlugin.py

## Purpose
Defines the base plugin interface for the tc-testing Python runner. Subclasses override lifecycle hooks to prepare suites, cases, command execution, and command rewriting.

## Important APIs, Types, And Functions
Class `TdcPlugin` exposes `pre_suite()`, `post_suite()`, `pre_case()`, `post_case()`, `pre_execute()`, `post_execute()`, `adjust_command()`, `add_args()`, and `check_args()`. It stores `args`, `argparser`, `testcount`, `testlist`, `caseinfo`, and `test_skip` as shared plugin state.

## Control Flow
The runner calls hooks around suite start/end, each case, and each command stage. The base implementation mostly records state and emits verbose traces. `adjust_command()` returns the input command unchanged, allowing subclasses to wrap it.

## State And Persistence
State is in the plugin instance for the duration of one runner invocation. It persists parsed arguments and current case metadata.

## Dependencies And Integration Points
Imported by `nsPlugin.py`, `rootPlugin.py`, `scapyPlugin.py`, and `valgrindPlugin.py`. It assumes subclasses set `self.sub_class` before invoking the base constructor.

## Risks
If a subclass does not set `sub_class`, base logging can raise an attribute error during construction. The base `check_args()` must be called by subclasses that rely on `self.args`.

## Test Signals
Verbose runner output showing hook order and successful plugin command adjustments without changing commands in the base class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/TdcPlugin.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/TdcResults.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/TdcResults.py

## Purpose
Provides result data structures and formatting helpers for tc-testing. It models per-test results, aggregates suites, and emits TAP or xUnit-like XML.

## Important APIs, Types, And Functions
Defines `ResultState` enum values `noresult`, `skip`, `success`, and `fail`; class `TestResult` with result, error, failure, and executed-step fields; and `TestSuiteReport` with add/update/count/find methods plus `format_tap()` and `format_xunit()`.

## Control Flow
Test code creates `TestResult`, sets result and messages, adds executed steps, and inserts it into `TestSuiteReport`. Formatters iterate results to produce a TAP plan with `ok`/`not ok` lines or XML with testcase, failure, error, and skipped elements.

## State And Persistence
Suite state is an in-memory list `_testsuite`. No files are written directly by this module.

## Dependencies And Integration Points
Used by `valgrindPlugin.py` to record memory-check subresults and likely by the main runner. XML formatting depends on `xml.sax.saxutils.escape`.

## Risks
`TestResult.add_steps()` has a bug in the string path: it appends undefined variable `step` instead of `newstep`. TAP skip formatting treats `noresult` as skipped. XML attribute escaping is applied to id/name, but the XML format lacks a failures count and may not match strict xUnit consumers.

## Test Signals
Correct suite counts, TAP plans matching result count, fail entries including executed commands and fail messages, skip entries carrying error text, and no TypeError except on invalid result/steps types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/TdcResults.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/action.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/action.c

## Purpose
Defines two tiny eBPF programs used by tc BPF action tests.

## Important APIs, Types, And Functions
`action_ok()` is placed in ELF section `action-ok` and returns `TC_ACT_OK`. `action_ko()` is placed in `action-ko`, writes `0` to `skb->data`, and returns `TC_ACT_OK`. `_license` is placed in the `license` section as `"GPL"`.

## Control Flow
The compiled object is loaded by `tc action bpf object-file ... section action-ok/action-ko`. The valid action returns OK without modifying the packet; the invalid one performs a verifier-hostile write to skb metadata.

## State And Persistence
No userspace state. Loaded eBPF program state is kernel-managed by tc/BPF.

## Dependencies And Integration Points
Depends on `<linux/bpf.h>` and `<linux/pkt_cls.h>`, and integrates with `bpf.json` tests through `$EBPFDIR/action-ebpf`.

## Risks
The intentionally invalid program must remain rejected by the verifier; verifier behavior changes could alter expected tc exit codes. Build flags outside this file determine whether sections and license are preserved.

## Test Signals
`bpf.json` should accept `action-ok`, reject or not install `action-ko`, and show expected action metadata in `tc action get`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/action.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/config

## Purpose
Lists kernel networking configuration needed for tc-testing coverage.

## Important APIs, Types, And Functions
Requests dummy/veth devices, netfilter and conntrack pieces, nft/nat/flow table modules, a broad set of qdiscs, classifiers, ematches, tc actions (`gact`, `bpf`, `connmark`, `ctinfo`, `ife`, `ct`, `gate`, and more), and supporting test devices such as `NETDEVSIM` and mock PTP.

## Control Flow
No runtime control flow. The config is consumed by kselftest config tooling and by humans preparing a kernel for tc-testing.

## State And Persistence
No state.

## Dependencies And Integration Points
Directly supports the JSON action suites in `tc-tests/actions`, namespace setup in `nsPlugin.py`, and scapy packet tests requiring veth/dummy devices.

## Risks
This file is broad but individual tests may still require userspace dependencies such as `ip`, `tc`, `pyroute2`, `scapy`, BPF tooling, or root privileges. Missing module autoload can cause test failures even when options are set to `m`.

## Test Signals
A prepared kernel has the requested qdisc/classifier/action modules available and can create veth/dummy devices and conntrack state in a namespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/creating-testcases/example.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/creating-testcases/example.json

## Purpose
Documents simple tc-testing JSON case structure using three non-network examples. It is an authoring reference rather than a kernel feature test suite.

## Important APIs, Types, And Functions
Each object demonstrates fields `id`, `name`, `category`, `setup`, `cmdUnderTest`, `expExitCode`, `verifyCmd`, `matchPattern`, `matchCount`, and `teardown`.

## Control Flow
The examples show runner ordering: setup commands create a temporary directory or file, command under test runs, verify command output is matched against regex/count expectations, and teardown removes state. One case shows no meaningful verify beyond `/bin/true`, and one shows empty setup/teardown arrays.

## State And Persistence
Temporary state is under `mytest` and is removed in teardown. No kernel state is required.

## Dependencies And Integration Points
Serves as documentation for the tc-testing runner schema consumed by the real test JSON files.

## Risks
Because this file is illustrative, running it in a shared directory could conflict with an existing `mytest` path. It does not demonstrate plugins or JSON matching.

## Test Signals
When run, the examples pass if `touch`, `ls`, `grep`, `ip`, and teardown behave as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/creating-testcases/example.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/creating-testcases/scapy-example.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/creating-testcases/scapy-example.json

## Purpose
Demonstrates tc-testing cases that use `nsPlugin` and `scapyPlugin` to send packets and verify tc statistics through JSON output.

## Important APIs, Types, And Functions
The cases use `plugins.requires`, setup commands for ingress qdisc management, `cmdUnderTest` adding a flower filter with `action ok`, a `scapy` block with `iface`, `count`, and packet expression, `verifyCmd` using `tc -s -j`, and `matchJSON` path/value assertions.

## Control Flow
Each case creates or resets ingress qdisc on `$DEV1`, installs a flower filter matching a source IP, sends packets from `$DEV0` through scapy after command execution, then verifies packet stats at a nested JSON path. The second case intentionally uses a packet count that does not match the expected value, demonstrating failure behavior.

## State And Persistence
Temporary state is a network namespace with veth devices and an ingress qdisc/filter, removed in teardown and namespace cleanup.

## Dependencies And Integration Points
Integrates with `nsPlugin.py` for namespace/device setup and `scapyPlugin.py` for packet injection. Requires tc flower classifier and action support.

## Risks
The `packet` field is evaluated by Python `eval()` in the scapy plugin, so these examples rely on trusted test data. JSON paths are brittle to tc output schema changes.

## Test Signals
Successful packet counter increments in `tc -s -j filter ls` for the matching packet case, and a deliberate mismatch in the wrong-count example.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/creating-testcases/scapy-example.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/creating-testcases/template.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/creating-testcases/template.json

## Purpose
Provides blank templates for authoring tc-testing JSON cases, including simple command cases and cases with accepted setup/teardown exit-code lists.

## Important APIs, Types, And Functions
Shows required schema fields: `id`, `name`, `category`, `setup`, `cmdUnderTest`, `expExitCode`, `verifyCmd`, `matchPattern`, `matchCount`, and `teardown`. The second template demonstrates command entries represented as arrays with the command string followed by acceptable exit codes.

## Control Flow
No meaningful test flow is encoded because values are placeholders. It documents how the runner interprets setup and teardown lists before and after command/verify phases.

## State And Persistence
No real state.

## Dependencies And Integration Points
Used by test authors creating new files under `tc-tests`.

## Risks
Placeholders must not be run as real tests. The schema shown is regex-oriented and does not cover plugin, scapy, or `matchJSON` fields except by implication from other examples.

## Test Signals
As documentation, the signal is that new tests copied from this template load successfully after placeholders are filled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/creating-testcases/template.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugin-lib/nsPlugin.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugin-lib/nsPlugin.py

## Purpose
Implements the tc-testing namespace plugin. It creates a disposable network namespace and veth/dummy devices for tests requiring isolated networking, rewrites test commands to run inside that namespace, and cleans up namespaces after cases and suites.

## Important APIs, Types, And Functions
Class `SubPlugin(TdcPlugin)` implements `prepare_test()`, `pre_case()`, `post_case()`, `post_suite()`, `adjust_command()`, `_nl_ns_create()`, `_ipr2_ns_create_cmds()`, `_ipr2_ns_create()`, `_nl_ns_destroy()`, `_ipr2_ns_destroy_cmd()`, `_ipr2_ns_destroy()`, `_proc`, `_proc_check()`, `_exec_cmd()`, `_exec_cmd_batched()`, and `_replace_keywords()`. It optionally uses `pyroute2.netns` and `IPRoute`; otherwise it drives `ip -b -` through a persistent subprocess.

## Control Flow
Before a case, the plugin skips cases marked skipped or not requiring `nsPlugin`. For required cases it creates the namespace, veth peer, dummy device, and optional passed-through device, then waits until `/run/netns/$NS` is visible. During setup/execute/verify/teardown stages, `adjust_command()` prefixes commands with `$IP netns exec $NS`. After each case it removes the namespace, and after the suite it force-deletes any remaining namespaces with `ip -a netns del`.

## State And Persistence
State includes plugin args, substituted names from `tdc_config`, optional persistent `ip -b -` process cached in `_proc`, and kernel network namespace/device state. Namespace cleanup should remove veth and dummy devices automatically.

## Dependencies And Integration Points
Depends on root privileges, `iproute2`, optional `pyroute2`, veth/dummy kernel support, and tc-testing plugin lifecycle hooks. JSON tests request it through `plugins.requires`.

## Risks
The pyroute2 path and iproute2 fallback differ in implementation, so bugs may be backend-specific. `adjust_command()` uses naive `split()` for string commands, which can alter quoting. The cached batch `ip` subprocess can fail and poison later commands. Cleanup is broad (`ip -a netns del`) and must run in an isolated test environment.

## Test Signals
Signals include namespace visibility under `/run/netns`, `$DEV0/$DEV1/$DUMMY` links up, commands executing inside the namespace, no namespace leaks after suite cleanup, and tc action tests with `nsPlugin` passing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugin-lib/nsPlugin.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugin-lib/rootPlugin.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugin-lib/rootPlugin.py

## Purpose
Provides a tc-testing plugin that enforces root privileges before the suite runs.

## Important APIs, Types, And Functions
Class `SubPlugin(TdcPlugin)` sets `sub_class` to `root/SubPlugin` and overrides `pre_suite()`. It uses `os.geteuid()` and exits with status `1` when not root.

## Control Flow
At suite start, it calls the base `pre_suite()` then checks effective uid. Non-root execution prints an error to stderr and terminates the runner.

## State And Persistence
No persistent state beyond base plugin args and suite metadata.

## Dependencies And Integration Points
Used by the tc-testing runner when root-only operations such as namespace, tc, netfilter, or BPF tests are enabled.

## Risks
It exits immediately rather than returning a kselftest skip result, so non-root runs may appear as failures depending on the caller. It does not check specific capabilities as an alternative to uid 0.

## Test Signals
Root runs continue into cases; non-root runs stop with `This script must be run with root privileges`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugin-lib/rootPlugin.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugin-lib/scapyPlugin.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugin-lib/scapyPlugin.py

## Purpose
Adds packet injection support to tc-testing cases using scapy. It sends packets after the command under test so tc filters/actions can update counters before verification.

## Important APIs, Types, And Functions
Class `SubPlugin(TdcPlugin)` overrides `post_execute()`. It imports `scapy.all`, reads each case's `scapy` block, requires `iface`, `count`, and `packet`, substitutes interface names from `NAMES`, evaluates the packet expression, and calls `sendp()`.

## Control Flow
If a case has no `scapy` key, the hook returns. A single scapy object is normalized into a list, allowing multiple packet sends. For each block the plugin validates keys, builds the packet with `eval()`, substitutes `$DEV*` interface placeholders, and sends the packet `count` times.

## State And Persistence
No persistent state other than mutated `scapyinfo['iface']` after substitution. Packet effects persist in network namespace counters and conntrack tables until teardown.

## Dependencies And Integration Points
Depends on the `scapy` Python package, raw packet privileges, and usually `nsPlugin`-created veth devices. Used by scapy examples and ct DNAT conflict tests.

## Risks
`eval()` on JSON-provided packet strings is powerful and requires trusted test files. Missing scapy exits the process at import time. Key validation reports missing keys but does not explicitly skip sending for malformed entries, so later errors can still occur.

## Test Signals
Packets appear on the requested interface, tc stats or conntrack state changes after `post_execute()`, and scapy import failures are clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugin-lib/scapyPlugin.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugin-lib/valgrindPlugin.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugin-lib/valgrindPlugin.py

## Purpose
Adds optional Valgrind execution and memory-leak reporting for tc-testing command-under-test stages.

## Important APIs, Types, And Functions
Defines `vp_extract_num_from_string()` and class `SubPlugin(TdcPlugin)`. The class adds `-V/--valgrind`, wraps execute-stage commands with `VALGRIND_BIN` plus leak options and per-test `vgnd-$testid.log`, parses leak/error summaries in `post_execute()`, stores `TestResult` objects in `TestSuiteReport`, and deletes logs when verbosity is low.

## Control Flow
When `--valgrind` is disabled, hooks return commands unchanged. When enabled, execute commands are prefixed with Valgrind options. After execution, skipped cases get skipped memory results; otherwise the plugin opens the test log, extracts definite/indirect/possible leak and non-leak error counts, marks the memory subtest failed if any are nonzero, and records the result. `post_suite()` marks remaining unattempted memory subtests skipped.

## State And Persistence
State includes `tap`, `_tsr`, `testidlist`, compiled regexes, and `vgnd-*.log` files. Logs may persist at high verbosity.

## Dependencies And Integration Points
Depends on `TdcPlugin`, `TdcResults`, `tdc_config.ENVIR['VALGRIND_BIN']`, and the runner's stage model. It is useful for tc userspace command memory checks, not kernel memory.

## Risks
`pre_suite(self, testcount, testist)` references `testlist` despite the parameter being misspelled, which can fail unless a global exists. String command splitting is naive. The `possibly_lost` regex is missing whitespace before `bytes`, likely missing some reports. Concurrent runs can collide on `vgnd-$testid.log`.

## Test Signals
With `--valgrind`, execute commands run under Valgrind, `vgnd-*.log` files are produced, zero leak/error summaries become success memory results, and leak/error summaries become failed memory subtests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugin-lib/valgrindPlugin.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugins/__init__.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugins/__init__.py

## Purpose
Marks the `plugins` directory as a Python package for tc-testing plugin imports.

## Important APIs, Types, And Functions
The file is intentionally empty and exports no names.

## Control Flow
No runtime control flow beyond Python package initialization.

## State And Persistence
No state.

## Dependencies And Integration Points
Allows plugin modules under `plugins` to be imported by package path if present. The assigned plugin implementations live under `plugin-lib`, but the runner may also use this package directory.

## Risks
Because it is empty, all behavior depends on external plugin discovery logic. Removing it could break package-based imports on older Python tooling.

## Test Signals
Python can import the `plugins` package without error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugins/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/scripts/sfq_rejects_limit_1.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/scripts/sfq_rejects_limit_1.py

## Purpose
Validates packet accounting for an SFQ qdisc with a low packet limit by sending UDP traffic and checking reject/drop counters.

## Important APIs, Types, And Functions
Uses scapy `sendp`, `Ether`, `IP`, `UDP`, and `Raw`, plus `sys.argv` for the target interface. Sends 100 packets with a large payload and varying destination ports.

## Control Flow
The script constructs one Ethernet/IP/UDP packet template and loops from 0 to 99, changing `UDP.dport` to `i` and sending each packet on the supplied interface. The comments document expected qdisc output: 100 sent packets, 99 drops, and 99 overlimit/requeue events when `limit 1` applies.

## State And Persistence
No script state persists. Kernel qdisc statistics on the target interface persist until qdisc teardown.

## Dependencies And Integration Points
Depends on scapy and an interface prepared by tc-testing. Intended to be invoked from a JSON qdisc test outside this assigned action subset.

## Risks
Requires root/raw packet permissions and a correctly configured qdisc before execution. It does not validate argument count or catch send errors.

## Test Signals
After execution, tc qdisc statistics should show one packet queued/accepted and the expected reject/drop counters for the rest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/scripts/sfq_rejects_limit_1.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/scripts/taprio_wait_for_admin.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/scripts/taprio_wait_for_admin.sh

## Purpose
Polls a taprio qdisc until an admin schedule is visible, helping tests wait for asynchronous taprio state publication.

## Important APIs, Types, And Functions
Uses shell variables `TC`, `DEV`, `handle`, `query`, `taprio`, and `MAX_WAIT`. It runs `tc qdisc show dev "$DEV"` repeatedly and greps for the expected taprio handle plus `admin`.

## Control Flow
The script loops for up to 20 seconds. Each second it checks whether the qdisc output contains the requested handle with `taprio` and an admin schedule; if so it exits success. After the timeout it exits failure.

## State And Persistence
No persistent state. It observes qdisc state on the device provided by arguments.

## Dependencies And Integration Points
Depends on `tc`, a target interface, taprio qdisc support, and tests that pass the correct qdisc handle.

## Risks
String matching is simple and can break if `tc qdisc show` formatting changes. Polling at one-second granularity can add up to 20 seconds to failing tests.

## Test Signals
Exit status `0` when admin schedule appears; exit status `1` after timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/scripts/taprio_wait_for_admin.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/bpf.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/bpf.json

## Purpose
Defines 12 tc action tests for classic BPF and eBPF action handling.

## Important APIs, Types, And Functions
Cases cover valid/invalid cBPF bytecode, valid/invalid eBPF object sections from `$EBPFDIR/action-ebpf`, replace behavior, delete, list, flush, duplicate and invalid indexes, cookies, and invalid `goto chain` control. Verification uses `tc action get/list action bpf` plus regex `matchPattern` and `matchCount`.

## Control Flow
Each case uses setup to establish any expected preexisting action state, runs a `tc action add/replace/delete/list/flush` command, checks the expected exit code, verifies state with another `tc` command, and tears down action state. eBPF cases use sections `action-ok` and `action-ko` from `action.c`.

## State And Persistence
Kernel tc action table state persists during each case and is removed in teardown or flush tests. Cookies and indexes are part of tc action state.

## Dependencies And Integration Points
Depends on `NET_ACT_BPF`, classic BPF parsing, eBPF verifier/object loading, the compiled action object, and the tc-testing runner. Unlike most other action JSON files, this one does not require `nsPlugin`.

## Risks
Regexes are sensitive to iproute2 output formatting, including JIT tag text. Invalid eBPF behavior depends on verifier rules. Large index boundary behavior may vary if tc parser changes.

## Test Signals
Expected signals are installed valid BPF actions with correct bytecode/object metadata, rejected invalid bytecode/object or invalid index cases, correct reference counts, cookie display, and successful list/flush count changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/bpf.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/connmark.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/connmark.json

## Purpose
Defines 15 tc tests for the `connmark` action parser and action-table lifecycle.

## Important APIs, Types, And Functions
Cases cover default creation, controls `pass`, `drop`, `pipe`, `reclassify`, `continue`, and `jump`, zone argument handling, unsupported/invalid arguments, replace, cookie, invalid `goto chain`, delete valid index, and delete invalid index. All require `nsPlugin`.

## Control Flow
Each case sets up isolated namespace state, runs `tc actions add/replace/del action connmark ...`, verifies with `tc actions get/list`, and matches textual output for zone, control action, index, ref count, and cookie. Negative cases expect no matching installed action or nonzero exit codes.

## State And Persistence
State is per-network-namespace tc action state plus conntrack-related action metadata. Teardown removes actions and namespace state.

## Dependencies And Integration Points
Depends on `NET_ACT_CONNMARK`, conntrack mark support, namespace setup, and iproute2 `tc`.

## Risks
Zone max/invalid handling and default control rendering are parser-sensitive. Regex checks rely on stable `tc` text output. Some tests use the same index values across cases and rely on isolation/teardown.

## Test Signals
Pass signals include correct zone display, action controls, ref counts, cookie preservation, and rejection of invalid zone/unsupported argument/goto-chain cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/connmark.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/csum.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/csum.json

## Purpose
Defines 23 tc tests for the `csum` action, including checksum target parsing, combined protocols, batching, cookies, invalid controls, and `no_percpu`.

## Important APIs, Types, And Functions
Tests cover aliases `iph`, `ip4h`, `ipv4h`, protocols `icmp`, `igmp`, `tcp`, `udp`, `udplite`, `sctp`, invalid `foobar`, invalid `udp xor iph`, combinations with `and/or`, all seven checksum targets, cookies, batches of 32 add/delete actions, invalid `goto chain`, and `no_percpu`.

## Control Flow
Cases run inside `nsPlugin`, create actions with `tc actions add/replace/del`, verify `tc actions get/list` output against regexes, and use setup/teardown to isolate the action table. Batch cases synthesize many `action csum ... index $i` clauses in a shell loop.

## State And Persistence
Per-namespace tc action state persists for the case duration. Batch tests create up to 32 indexed actions and remove them in paired delete cases or teardown.

## Dependencies And Integration Points
Depends on `NET_ACT_CSUM`, namespace support, and tc parser support for protocol aliases and `no_percpu`.

## Risks
Protocol order in `tc` output is normalized and regexes assume that order. Batch shell quoting is brittle. Negative cases depend on parser rejecting malformed combinations without leaving partial state.

## Test Signals
Signals are correct normalized protocol lists, control action display, cookie display, exact batch ref-count totals, deletion clearing actions, and rejected invalid target/control cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/csum.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/ct.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/ct.json

## Purpose
Defines 22 tests for the tc connection-tracking action, covering parser features, NAT/mark/label options, attachment restrictions, and one packet-driven conntrack/NAT conflict scenario.

## Important APIs, Types, And Functions
Cases cover simple `ct`, cookies, `clear`, zones, `commit`, marks and masks, IPv4/IPv6 NAT addresses and ranges, `force`, labels and label masks, `no_percpu`, DNAT tuple conflict, and attaching `act_ct` to ETS qdisc, ingress, clsact egress, and shared blocks. Verification uses both regex output and `matchJSON` for filter/action binding.

## Control Flow
Most cases run `tc actions add action ct ...` and verify textual state. The DNAT case configures an ingress flower rule with `ct commit nat dst`, sends two TCP packets with scapy, and verifies `/proc/net/nf_conntrack` contains the expected original destination. Attachment cases set up qdisc/block context, run `tc filter add ... action ct`, and verify JSON output or expected failure.

## State And Persistence
State includes per-namespace tc action/filter/qdisc state and conntrack table entries. Teardown must clear qdiscs/actions and namespace state.

## Dependencies And Integration Points
Depends on `NET_ACT_CT`, conntrack, NAT, flower/matchall classifiers, ingress/clsact/shared block support, `nsPlugin`, and for one case `scapyPlugin`.

## Risks
Conntrack table contents can be affected by prior packets if namespace isolation fails. NAT and label output formatting is iproute2-sensitive. JSON match expectations depend on tc's nested schema. Attachment restrictions may change as kernel qdisc/action compatibility evolves.

## Test Signals
Pass signals are correct ct option rendering, successful NAT/mark/label parser behavior, expected failure attaching to ETS, successful binding on ingress/egress/shared block with ref/bind counts, and conntrack entry evidence after scapy traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/ct.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/ctinfo.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/ctinfo.json

## Purpose
Defines 12 tests for the `ctinfo` action parser and lifecycle.

## Important APIs, Types, And Functions
Cases cover default settings, DSCP masks/stats, `cpmark` with zone, drop control, replace changing zone/control, valid and invalid delete, list, flush, duplicate index, invalid index over 32 bits, and invalid `goto_chain` control.

## Control Flow
All cases require `nsPlugin`, run a `tc action add/replace/delete/list/flush action ctinfo` command, compare expected exit code, and verify textual `tc` output for zone, action control, index, ref count, dscp/cpmark fields, and counts.

## State And Persistence
Per-namespace tc action state persists within a case and is reset by teardown.

## Dependencies And Integration Points
Depends on `NET_ACT_CTINFO`, conntrack mark/DSCP support, namespace setup, and tc action output formatting.

## Risks
DSCP/cpmark mask rendering and invalid goto-chain fallback behavior are parser/output sensitive. Some expected failures still verify preexisting state, so setup correctness is important.

## Test Signals
Signals include correct ctinfo field rendering, replace updating state, delete/flush reducing counts, duplicate/invalid indexes rejected, and invalid goto-chain leaving or showing expected pass behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/ctinfo.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/gact.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/gact.json

## Purpose
Defines 27 tests for the generic action (`gact`) family, including controls, index boundaries, list/flush/delete/get, batch operations, random/deterministic control parsing, `no_percpu`, and referenced-action flush behavior.

## Important APIs, Types, And Functions
Cases cover `pass`, `pipe`, `reclassify`, `drop`, `continue`, invalid `pump`, duplicate/oversized/max indexes, list/flush, deletion by control/index, replace, get by large index, batches of 32 actions, random deterministic goto-chain controls, invalid goto-chain replace, `no_percpu`, and flush attempts while actions are bound to filters.

## Control Flow
All cases use `nsPlugin`. Commands create or mutate actions, sometimes with setup-created referenced filters, then verify `tc actions list/get` output with regex counts and ref/bind values. Batch cases use shell loops to generate many action clauses.

## State And Persistence
Per-namespace action and filter state persists across setup, command, verify, and teardown. Referenced-action tests intentionally leave a bound action during flush verification to ensure reference protection.

## Dependencies And Integration Points
Depends on `NET_ACT_GACT`, matchall/filter support for reference tests, namespace setup, and tc parser support for random/deterministic action syntax.

## Risks
Regexes assume exact textual wording for ref/bind counts and random control output. Flush behavior for referenced actions is semantically delicate and can change with kernel fixes. Batch quoting is error-prone.

## Test Signals
Pass signals are correct action control rendering, rejected invalid controls/indexes, successful batch add/delete counts, `no_percpu` display, and flush refusing or preserving actions with active filter references as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/gact.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/gate.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/gate.json

## Purpose
Defines 12 tests for the time-aware `gate` tc action.

## Important APIs, Types, And Functions
Cases cover priority plus `sched-entry`, `base-time`, `cycle-time`, `cycle-time-ext`, replace of base-time action, delete valid/invalid index, list, flush, duplicate max index, invalid oversized index, and cookies. All require `nsPlugin`.

## Control Flow
Each test runs `tc action add/replace/delete/list/flush action gate ...`, verifies expected exit code, and matches `tc action get/list` output for timing fields normalized to seconds, index, ref count, priority, and cookies.

## State And Persistence
Per-namespace gate action state persists during each case. Schedule parameters are kernel action metadata, not active hardware offload state in these tests.

## Dependencies And Integration Points
Depends on `NET_ACT_GATE`, tc parser support for nanosecond time units and schedule entries, and namespace setup.

## Risks
Time formatting normalization (`200000000000ns` to `200s`) is output-sensitive. Delete test `d821` verifies through `action bpf` instead of `action gate`, which appears suspicious and could mask gate-specific behavior if not intentional. Gate availability may depend on kernel module loading.

## Test Signals
Signals include correct normalized base/cycle time display, sched-entry acceptance, replace updates, list/flush counts, invalid index rejection, duplicate max index behavior, and cookie display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/gate.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/ife.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/ife.json

## Purpose
Defines 50 tests for the IFE tc action, covering encode/decode modes, metadata selection, controls, boundaries, cookies, delete/replace, invalid input handling, and JSON verification for metadata updates.

## Important APIs, Types, And Functions
Cases cover encode with `mark`, `prio`, and `tcindex`; controls `pass`, `pipe`, `continue`, `drop`, `reclassify`, and `jump`; 32-bit mark/prio boundaries; 16-bit tcindex boundaries; source/destination MAC parameters; custom EtherType; max and oversized action indexes; decode controls; invalid controls/arguments/type/MACs; invalid goto-chain replacement; delete valid/invalid index; and replacing decode actions into encode metadata using `matchJSON`.

## Control Flow
All cases use `nsPlugin`. Commands add, replace, delete, or get IFE actions. Most verification uses regexes over `tc actions get/list`; the final update cases use `tc -j actions get` with JSON matching to verify encoded metadata fields after replacement.

## State And Persistence
State is per-namespace IFE action metadata including mode, allowed/used metadata, MAC addresses, EtherType, control action, cookies, and indexes. Teardown clears created actions where specified.

## Dependencies And Integration Points
Depends on `NET_ACT_IFE` and metadata modules `NET_IFE_SKBMARK`, `NET_IFE_SKBPRIO`, and `NET_IFE_SKBTCINDEX`, plus tc JSON/text output and namespace setup.

## Risks
The suite is highly parser-output sensitive: metadata ordering, EtherType case, default decode allow-list, and JSON field names can change. There is a duplicated name for two tcindex/continue cases, though ids differ. Invalid input tests must ensure rejected actions do not leave stale prior state under reused indexes.

## Test Signals
Pass signals are accepted valid metadata/control combinations, rejected out-of-range or malformed metadata, correct boundary acceptance at max values, preserved cookies, correct delete behavior, and JSON evidence that replace operations update IFE encode metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/ife.json -->
