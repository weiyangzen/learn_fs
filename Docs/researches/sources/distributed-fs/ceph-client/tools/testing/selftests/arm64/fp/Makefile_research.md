# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/Makefile

Purpose: builds arm64 floating-point, SVE, SME, ZA, ZT, vector-length, and stress selftests.

Important APIs/types/functions: declares many `TEST_GEN_PROGS`, `TEST_GEN_PROGS_EXTENDED`, and `TEST_PROGS_EXTENDED`; sets `top_srcdir`, `KHDR_INCLUDES`, and `EXTRA_CLEAN`; custom rules link several assembly/nolibc programs (`fp-pidbench`, `fpsimd-test`, `sve-test`, `ssve-test`, `za-fork`, `za-test`, `zt-test`) and C programs with shared objects such as `asm-utils.o` and `rdvl.o`; includes `../../lib.mk`.

Control flow: kselftest build rules compile the listed generated and extended programs; custom targets supply special link flags where libc must be avoided.

State and persistence: build outputs only.

Dependencies/integration: arm64 compiler, kernel headers, nolibc, local assembly utilities, and FP/SVE/SME source files not all in this subset.

Risks and test signals: toolchain support for SVE/SME instructions and static/nolibc builds is critical. Missing `asm-utils.o` or `rdvl.o` affects multiple targets.
