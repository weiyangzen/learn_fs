# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/Makefile

## Purpose
Top-level filesystem selftest build metadata for several generic filesystem tests.

## Important APIs, Types, And Functions
Adds `$(KHDR_INCLUDES)` to `CFLAGS`, defines `TEST_GEN_PROGS := devpts_pts file_stressor anon_inode_test kernfs_test fclog`, `TEST_GEN_PROGS_EXTENDED := dnotify_test`, and includes `../lib.mk`.

## Control Flow
kselftest builds standard generated programs and extended helper/test binaries.

## State And Persistence
Generated binaries only.

## Dependencies And Integration Points
Pulls in tests for devpts, anonymous inodes, kernfs, fclog, stress, and dnotify. Some source files are outside this subset but are built here.

## Risks
Adding a program here without matching source/runtime prerequisites can break the whole directory build. Extended dnotify test is built but not necessarily run as a default test program.

## Test Signals
Successful build produces the listed filesystem test binaries.
