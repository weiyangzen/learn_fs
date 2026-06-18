# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-fork.c

Purpose: smoke-tests entering the kernel through a `fork` syscall while in an active hardware transaction.

Important APIs/types/functions: `test_fork()` emits inline assembly with `tbegin.`, syscall number 2, `sc`, and `tend.`.

Control flow: after HTM skips, the test starts a transaction and executes the fork syscall directly. Reaching the end without kernel crash or process failure is treated as pass.

State and persistence behavior: a fork may create a child depending on transaction/syscall behavior, but the test does not manage child state explicitly because it is probing crash behavior.

Dependencies and integration points: depends on real HTM and raw powerpc syscall ABI.

Risks and test signals: it is intentionally shallow and does not verify child cleanup or specific failure code. Its useful signal is absence of kernel crash and harness completion.
