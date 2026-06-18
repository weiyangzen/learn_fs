# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/pac.c

## Purpose

`pac.c` is the main pointer-authentication selftest. It verifies that PAC instructions are active, corrupted return authentication faults, different keys produce distinguishable signatures, exec changes keys, and context switches preserve keys.

## Important APIs, Types, and Functions

Important helpers are `sign_specific()`, `sign_all()`, `n_same()`, `n_same_single_set()`, `exec_sign_all()`, and `pac_signal_handler()`. Test cases are `corrupt_pac`, `pac_instructions_not_nop`, `pac_instructions_not_nop_generic`, `single_thread_different_keys`, `exec_changed_keys`, `context_switch_keep_keys`, and `context_switch_keep_keys_generic`.

## Control Flow and Data Flow

Feature macros gate tests with `HWCAP_PACA` and `HWCAP_PACG`. `exec_sign_all()` creates stdin/stdout pipes, pins execution to one CPU to force a useful context switch, forks, execs `exec_target`, writes a value, waits for completion, then reads back signatures. Collision-sensitive tests repeat up to `PAC_COLLISION_ATTEMPTS`.

## State and Persistence Behavior

The test changes signal handlers for SIGSEGV/SIGILL during corrupt-PAC validation and pins process affinity during exec comparisons. PAC keys are kernel-managed process/thread state. No persistent files are written.

## Dependencies and Integration Points

It uses `kselftest_harness.h`, helper functions, `pac_corruptor.S`, `exec_target`, auxv HWCAPs, pipes, fork/exec, wait, and CPU affinity APIs. It must be run from a directory where `exec_target` is executable under that name.

## Risks and Edge Cases

PAC bit width can be small, so equality checks are probabilistic and repeated. `PAC_MASK` assumes top-byte-ignore behavior and a 48-bit VA default. Pipe setup has some cleanup gaps on early failure. Generic PAC is optional and skipped independently.

## Test Signals

Expected failures include missing SIGSEGV/SIGILL for corrupted return PAC, all-zero masked PAC output, keys colliding every attempt, unchanged signatures across exec, or changed signatures after a context switch.
