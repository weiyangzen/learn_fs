# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/dead_code.c

Purpose: verifies verifier handling of unreachable instructions and dead subprogram regions without rejecting otherwise safe programs.

Important APIs/types/functions: uses jumps, exits, relative subprogram calls, and `.retval` checks; unprivileged paths validate restrictions on calls to other BPF functions.

Control flow: tests place dead code at the start, middle, and end of main programs, at function tails, inside and before subprograms, and around calls. The final zero-extension case ensures dead-code elimination does not disturb 32-bit register semantics.

State and persistence behavior: state is verifier reachability and liveness information. Dead instructions should not contribute invalid state, stack depth, or bad return values when unreachable.

Dependencies and integration points: included in verifier harness with privileged/unprivileged split for subprogram-call tests.

Risks: overly strict reachability checks can reject valid optimized programs; overly loose checks can hide reachable unsafe paths.

Test signals: most cases accept with return values `7`, `1`, `2`, or `0`; unprivileged subprogram cases reject with `loading/calling other bpf or kernel functions are allowed for`.
