# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/switch_endian/check.S

Purpose: register-preservation checker used in both native and reversed byte order by the endian-switch test.

Important APIs/types/functions: checks r3-r8, r13-r14, r16-r31, LR, and preserved CR fields against a pattern in r15, then either exits with a failing value or performs another `switch_endian` syscall.

Control flow: starts with a `nop` that is illegal in reverse-endian to guard wrong execution mode, compares each expected register value, branches to failure if any mismatch occurs, otherwise loads `__NR_switch_endian` and reaches the trailing syscall site.

State and persistence behavior: no persistent state; uses register contents set by `switch_endian_test.S`.

Dependencies and integration points: included directly and also transformed into `check-reversed.S` by the Makefile.

Risks and test signals: exact register contract must match kernel syscall clobber rules. Failure exits immediately through `__NR_exit` with a diagnostic register value in r3.
