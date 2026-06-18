# sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/Makefile

This Makefile registers kexec selftests on supported architectures. It enables load and file-load shell tests on x86 and ppc64le, and adds the kexec jump helper only for 64-bit x86.

Important variables are `ARCH`, `ARCH_PROCESSED`, `TEST_PROGS`, `TEST_FILES`, `IS_64_BIT`, and `TEST_GEN_PROGS`. The file includes `../../../scripts/Makefile.arch` for architecture bitness and `../lib.mk` for selftest rules.

Make-time conditionals select test coverage. For x86 or ppc64le it registers `test_kexec_load.sh`, `test_kexec_file_load.sh`, and `kexec_common_lib.sh`. For x86_64 it also builds `test_kexec_jump` and registers `test_kexec_jump.sh`.

Dependencies are common kselftest make rules, the architecture helper makefile, shell scripts, kexec tooling at runtime, and a C compiler for jump tests. Unsupported architectures get no tests from this directory. Pass signals are correct test installation and x86_64 helper compilation.
