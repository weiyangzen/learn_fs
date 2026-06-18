## sources/distributed-fs/openafs/src/kopenafs/test-setpag.c

Purpose: `test-setpag.c` is a runtime smoke test for `libkopenafs` PAG creation.

Important control flow: if `k_hasafs` returns true, it prints current PAG status via `k_haspag`, calls `k_setpag`, prints status and `errno`, checks that `k_haspag` is now true, and optionally `execvp`s a command supplied on the command line. If AFS is unavailable, it prints that AFS is apparently not running.

State and persistence: changes the current process PAG and optionally executes another program inside that PAG.

Dependencies and integration points: includes public `kopenafs.h` and standard `errno`, `stdio`, `unistd`.

Risks: prints `errno` after `k_setpag` regardless of whether the call succeeded, so stale errno can be misleading. If `execvp` fails, the program does not explicitly report `perror`.

Test signals: expected success is status 0 and `k_haspag` true after `k_setpag`.
