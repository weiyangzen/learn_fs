<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_chacha.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_chacha.c

## Purpose
Validates architecture vgetrandom ChaCha20 block implementation against a C reference.

## Important APIs, Types, and Functions
reference_chacha20_blocks, __arch_chacha20_blocks_nostack weak symbol, cpu_has_capabilities, kselftest main.

## Control Flow
Generates random keys, computes reference output for 128 blocks, calls the arch nostack implementation in every split position, compares output and counters, and tests counter wrap/block-limit behavior.

## State and Persistence
No persistent state; uses stack buffers and random keys.

## Dependencies and Integration Points
Depends on getrandom, tools/le_byteshift.h, arch assembly linked through vgetrandom-chacha.S, and required CPU vector capabilities on some architectures.

## Risks and Edge Cases
Very CPU-intensive nested loop; weak fallback skips if no implementation is linked.

## Test Signals
Pass is one kselftest result after all output/counter comparisons succeed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_chacha.c -->
