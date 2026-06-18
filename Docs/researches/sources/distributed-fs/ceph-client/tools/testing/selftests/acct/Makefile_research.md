# sources/distributed-fs/ceph-client/tools/testing/selftests/acct/Makefile

Purpose: builds the process accounting syscall selftest.

Important APIs/types/functions: `TEST_GEN_PROGS := acct_syscall`, adds `-Wall`, and includes `../lib.mk`.

Control flow: kselftest `lib.mk` supplies build/run/install behavior for the generated program.

State and persistence: build output only.

Dependencies/integration: part of the top-level selftests `acct` target.

Risks and test signals: build failure or missing syscall headers/libraries are the only local signals.
