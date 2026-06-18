# sources/distributed-fs/ceph-client/tools/testing/selftests/splice/Makefile

## Purpose
Builds splice selftest helpers and registers shell tests for default and short splice reads.

## Important APIs, types, and functions
Declares `TEST_PROGS := default_file_splice_read.sh short_splice_read.sh` and `TEST_GEN_PROGS_EXTENDED := default_file_splice_read splice_read`.

## Control flow
`../lib.mk` builds helper binaries and runs shell scripts as kselftests.

## State and persistence
Only build outputs are produced.

## Dependencies and integration points
Integrated with kselftest common rules and the local C helpers/scripts.

## Risks
Runtime tests depend on procfs, sysfs, and a test module being available.

## Test signals
Successful build creates both helper binaries; shell scripts provide pass/fail exit codes.
