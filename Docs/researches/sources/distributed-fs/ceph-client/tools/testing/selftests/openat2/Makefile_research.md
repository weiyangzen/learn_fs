# sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/Makefile

Purpose: builds the openat2 selftest executables and links them with shared helper code.

Important settings: `CFLAGS` enables `-Wall -O2 -g` plus AddressSanitizer and UBSan. `TEST_GEN_PROGS` lists `openat2_test`, `resolve_test`, and `rename_attack_test`. `LOCAL_HDRS` declares `helpers.h`. Each generated program depends on `helpers.c`.

Control flow/integration: inclusion of `../lib.mk` connects this directory to the kselftest build/install/run framework. For GCC builds it adds `-static-libasan` so ASan is loaded first; clang/LLVM builds omit that flag because clang handles sanitizer linkage differently.

State and dependencies: build outputs are generated programs only. Runtime dependencies come from the C tests: openat2 syscall support, procfs, root/mount namespace permissions for resolver tests, and sanitizer runtime availability.

Risks: sanitizer flags can change timing and memory layout, which matters most for the rename race stress test. Systems without compatible sanitizer libraries or static ASan may fail at build/link time.

Test signals: the Makefile itself has no runtime signal; pass/fail comes from the three kselftest binaries it builds.
