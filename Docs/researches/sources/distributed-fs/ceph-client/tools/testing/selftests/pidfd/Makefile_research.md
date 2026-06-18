# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/Makefile

Purpose: builds the pidfd selftest suite and the helper executable used by exec-related tests.

Important settings: `CFLAGS` includes debug info, kernel/tool includes, pthread, and `-Wall`. `TEST_GEN_PROGS` lists core pidfd, poll, wait, getfd, setns, file-handle, bind-mount, info, xattr, setattr, and autoreap tests. `TEST_GEN_PROGS_EXTENDED` builds `pidfd_exec_helper`.

Control flow/integration: inclusion of `../lib.mk` provides standard kselftest handling. The extended helper is installed/built but not run directly as a test.

State/dependencies: no runtime state. Runtime depends on pidfd syscalls, clone3, namespace support, pidfs ioctls, and sometimes mount APIs.

Risks: several listed programs are outside this subset but are part of the same build target. New kernel features such as autoreap/autokill may skip on older kernels.

Test signals: build success for all listed programs; runtime signals come from each binary.
