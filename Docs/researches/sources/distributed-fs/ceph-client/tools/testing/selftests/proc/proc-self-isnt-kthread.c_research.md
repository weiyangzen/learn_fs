# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-isnt-kthread.c

Purpose: checks that a normal userspace process reports `Kthread: 0` in `/proc/self/status`.

Important APIs and functions: uses `open`, `read`, NUL termination, and `strstr`.

Control flow: read `/proc/self/status` into a 4 KiB buffer and assert the exact `Kthread:\t0\n` line is present.

State and persistence: no persistent state.

Dependencies and integration: depends on procfs status format including the Kthread field.

Risks and test signals: format changes can break the exact substring search. Failure means userspace task classification or `/proc/self/status` field emission is wrong.
