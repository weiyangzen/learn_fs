# sources/distributed-fs/ceph-client/tools/testing/selftests/lib.mk

## Purpose

`lib.mk` is the common build, run, install, clean, and header-generation include for kernel selftests. It lets individual selftest directories declare programs, scripts, generated files, modules, headers, flags, and install assets while sharing consistent kselftest behavior.

## Important APIs, Types, and Functions

The Makefile variables include `TEST_GEN_PROGS`, `TEST_GEN_PROGS_EXTENDED`, `TEST_GEN_FILES`, `TEST_PROGS`, `TEST_CUSTOM_PROGS`, `TEST_FILES`, `TEST_INCLUDES`, `TEST_GEN_MODS_DIR`, `OUTPUT`, `INSTALL_PATH`, `KHDR_INCLUDES`, `TOOLS_INCLUDES`, `USERCFLAGS`, and `USERLDFLAGS`. It defines `RUN_TESTS`, install macros, build pattern rules for C and assembly, `gen_mods_dir`, `clean_mods_dir`, `emit_tests`, and `headers`.

## Control Flow and State

It selects clang or gcc based on `LLVM`/`CROSS_COMPILE`, derives target triples, initializes `OUTPUT` for standalone builds, rewrites generated test targets into output paths, builds generated programs/files, optionally builds module directories, runs tests through `kselftest/runner.sh`, installs artifacts with `rsync`, and cleans generated outputs. Persistent state is limited to build products under `OUTPUT` and installed files under `INSTALL_PATH`.

## Dependencies and Integration Points

It depends on GNU make, compiler toolchains, kselftest harness headers, optional kernel headers, `runner.sh`, `rsync`, and module sub-Makefiles.

## Risks and Test Signals

Risks include wrong output-path rewriting, cross-compile target mismatch, missing kernel headers, incomplete install lists, and module directories silently skipped when `KDIR` is absent. Signals are successful `make`, correct `run_tests` behavior in in-tree and out-of-tree builds, populated install trees, and `emit_tests` listing runnable tests.
