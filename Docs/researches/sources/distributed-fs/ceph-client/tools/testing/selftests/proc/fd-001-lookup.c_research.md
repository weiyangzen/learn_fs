# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/fd-001-lookup.c

Purpose: validates `/proc/self/fd/<fd>` lookup accepts only canonical numeric fd names and rejects junk, negative, and overflow-like names.

Important APIs/types/functions: `test_lookup_pass()`, `test_lookup_fail()`, `test_lookup()`, and helpers from `proc.h` such as `xreaddir()`, `xstrtoull()`, and `streq()`.

Control flow: the program unshares the file table, closes all open fds by reading `/proc/self/fd`, opens `/` so it becomes fd 0, tests lookup acceptance/rejection around that fd, then duplicates fd 0 to a high target fd and repeats tests.

State and persistence behavior: mutates the process fd table heavily after `unshare(CLONE_FILES)`. No external files are modified.

Dependencies and integration points: requires procfs fd symlinks, `O_PATH`, `CLONE_FILES` unshare, and proc test helper header.

Risks and test signals: uses `assert()` for all checks. Running under environments with unusual inherited fds is handled by wiping the fd table, but permissions/procfs restrictions can still fail early.
