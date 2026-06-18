# sources/distributed-fs/ceph-client/tools/testing/selftests/syscall_user_dispatch/Makefile

## Purpose
Builds and installs the syscall user dispatch selftests.

## Important APIs, Types, And Functions
Defines `top_srcdir`, `INSTALL_HDR_PATH`, `LINUX_HDR_PATH`, adds `-Wall` and the installed UAPI include path to `CFLAGS`, sets `TEST_GEN_PROGS := sud_test sud_benchmark`, and includes `../lib.mk`.

## Control Flow
The kselftest build framework compiles both C programs as generated test binaries and handles install/run targets through `lib.mk`.

## State And Persistence
No runtime state. Build outputs are the two generated programs.

## Dependencies And Integration Points
Depends on kernel headers under `usr/include` and the common kselftest Makefile. It pairs with `config`, which requests `CONFIG_GENERIC_ENTRY=y`.

## Risks
If installed headers do not expose recent `PR_SET_SYSCALL_USER_DISPATCH` constants, the C files provide fallbacks, but syscall numbers and architecture behavior still depend on target headers and libc.

## Test Signals
Successful compilation of `sud_test` and `sud_benchmark` with `-Wall` and inclusion in the kselftest generated-program list.
