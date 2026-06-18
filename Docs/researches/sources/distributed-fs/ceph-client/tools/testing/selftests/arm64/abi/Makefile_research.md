# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/Makefile

Purpose: builds arm64 ABI selftests.

Important APIs/types/functions: `TEST_GEN_PROGS := hwcap ptrace syscall-abi tpidr2`; includes `../../lib.mk`; declares `syscall-abi` dependency on C and assembly; builds `tpidr2` as static freestanding nolibc binary with stripped/optimized flags.

Control flow: kselftest `lib.mk` builds generated programs; explicit rules handle assembly-linked and nolibc cases.

State and persistence: build outputs only.

Dependencies/integration: depends on arm64 compiler, nolibc include tree, and kselftest build variables.

Risks and test signals: `tpidr2` intentionally avoids libc because TPIDR2 is libc-managed; build flags are sensitive to toolchain support.
