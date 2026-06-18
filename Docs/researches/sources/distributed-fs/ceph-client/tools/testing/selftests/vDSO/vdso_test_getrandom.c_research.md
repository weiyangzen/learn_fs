<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_getrandom.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_getrandom.c

## Purpose
Tests and benchmarks vDSO getrandom with opaque per-thread state, including time namespace behavior under ptrace.

## Important APIs, Types, and Functions
vgetrandom_init, vgetrandom_get_state/put_state, vgetrandom wrapper, bench_single, bench_multi, fill, kselftest.

## Control Flow
Resolves __vdso_getrandom, queries opaque state parameters, allocates aligned state blocks with mmap, performs repeated random fills, then forks under a new time namespace with ptrace to assert the vDSO path does not pass the test buffer to getrandom syscall; optional modes benchmark or fill indefinitely.

## State and Persistence
Maintains global state pool guarded by a mutex and thread-local state pointer; creates mappings, threads, namespaces, child process, and ptrace state.

## Dependencies and Integration Points
Depends on vDSO getrandom ABI, linux/random.h vgetrandom_opaque_params, pthreads, ptrace, CLONE_NEWTIME, getrandom syscall for benchmark comparisons.

## Risks and Edge Cases
Default constants are very large for benchmark modes; namespace/ptrace permissions can cause skips/failures; state allocator assumes page/cache-line alignment constraints from kernel params.

## Test Signals
Default kselftest passes two results: random fill and timens syscall-avoidance validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_getrandom.c -->
