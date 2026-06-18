# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/Makefile

Purpose: central build/run Makefile for the kernel mm selftest suite.

Important APIs/types/functions: includes local config generation, architecture detection, common CFLAGS/LDLIBS, a large `TEST_GEN_FILES` suite, wrapper `TEST_PROGS`, helper `TEST_FILES`, x86 32/64-bit target generation, target-specific libraries, and warning targets for missing liburing or page_frag prerequisites.

Control flow: disables built-in make rules and deletes failed outputs. It generates `local_config.mk`/`.h` through `check_config.sh`, selects architecture-specific tests, adds optional pkey and VA tests, wires common dependencies like `vm_util.c`/`thp_settings.c`, and emits user-facing warnings instead of hard failures for optional support gaps.

State and persistence: creates local config files and many generated binaries under `$(OUTPUT)`.

Dependencies and integration points: kernel build tree, generated headers, optional liburing/libcap/libnuma, architecture toolchains, `Module.symvers`, and kselftest `lib.mk`.

Risks: broad Makefile means local changes can affect many mm tests. Optional feature detection impacts coverage, especially liburing for COW tests and 32-bit builds on x86_64.

Test signals: build products and wrapper scripts define CI-visible mm coverage.
