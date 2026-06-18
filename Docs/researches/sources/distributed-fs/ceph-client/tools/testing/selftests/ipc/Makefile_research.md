# sources/distributed-fs/ceph-client/tools/testing/selftests/ipc/Makefile

This Makefile builds the IPC selftest binary `msgque`. It normalizes x86 architecture names and adds x86-specific preprocessor defines so kernel headers see the expected 32-bit or 64-bit configuration.

Important variables are `ARCH`, `CFLAGS`, `KHDR_INCLUDES`, and `TEST_GEN_PROGS := msgque`. It rewrites `i.86` and `x86_64` to `x86`, sets `CONFIG_X86_32`/`__i386__` or `CONFIG_X86_64`/`__x86_64__`, appends kernel header includes, and includes `../lib.mk`.

Control flow is make-time conditional evaluation only. State is generated build output for `msgque` plus inherited kselftest metadata. It depends on the common selftest make library, kernel headers, and a compiler. Integration is the standard kselftest generated-program path.

Risks are limited: non-x86 architectures receive no extra arch defines, and incorrect `ARCH` input could alter header assumptions. The test signal is successful `msgque` compilation and discovery by the kselftest runner.
