<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/asu.c -->
# sources/distributed-fs/openafs/src/tests/asu.c

## Purpose
Small privilege-drop wrapper for running a program as a named user during tests.

## Important APIs, Types, And Functions
Defines `usage` and `main`. Uses `getpwnam`, `setgroups`, `setgid`, `setuid`, `setegid`, `seteuid`, and `execvp`.

## Control Flow
Requires `user program [args...]`. If running as root, resolves the user, switches primary group and uid/euid/gid/egid to that account, then `execvp`s the requested program. If not root, it simply execs the program.

## State And Persistence
No filesystem persistence. It changes process credentials before replacing the process image.

## Dependencies And Integration Points
Useful for tests requiring non-root user semantics against AFS ACLs and tokens.

## Risks And Test Signals
If any credential change fails, it exits through `err`. It does not call `initgroups`, so supplementary groups are reduced to one primary group. Success is the child program's exit status after credential switch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/asu.c -->
