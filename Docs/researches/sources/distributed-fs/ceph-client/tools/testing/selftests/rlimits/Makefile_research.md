# sources/distributed-fs/ceph-client/tools/testing/selftests/rlimits/Makefile

Purpose: builds the `rlimits-per-userns` kselftest. It sets warning/debug CFLAGS, registers `TEST_GEN_PROGS := rlimits-per-userns`, and includes `../lib.mk`. State is the compiled output binary. Dependencies are user namespace support, libc, and root/capability context sufficient for UID/GID changes. Integration is with the adjacent config file. Risks are runtime privilege/environment requirements not expressed in the Makefile. Test signals are successful build and the binary’s pass/fail exit status.
