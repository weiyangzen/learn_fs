# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/Makefile

Purpose: builds the powerpc signal selftests covering plain signal delivery, TM signal delivery, sigreturn edge cases, and the TM-aware signal fuzzer.

Important APIs/types/functions: declares `TEST_GEN_PROGS` for `signal`, `signal_tm`, `sigfuz`, `sigreturn_vdso`, `sig_sc_double_restart`, `sigreturn_kernel`, and `sigreturn_unaligned`; adds `TEST_FILES := settings`.

Control flow: includes common kselftest `lib.mk` and powerpc `flags.mk`, compiles all programs with `../harness.c`, `../utils.c`, and `signal.S`, and adds targeted CFLAGS: `-mhtm` for `signal_tm`, `-pthread -m64` for `sigfuz`, and `-maltivec` generally.

State and persistence behavior: no runtime state; it produces binaries under `$(OUTPUT)`.

Dependencies and integration points: relies on the common selftest harness and powerpc assembly helper file for raw signal syscalls.

Risks and test signals: toolchains lacking HTM/Altivec flags or 64-bit support will fail at build time rather than runtime.
