# sources/compression/xz/build-aux/ci_build.bash

## Purpose
This Bash wrapper normalizes POSIX CI builds for autotools and CMake. It converts concise feature flags into configure/CMake options, separates build and test phases, and collects logs on failure.

## Important APIs and Control Flow
CLI options choose autogen flags, build system, checks, disabled features, CFLAGS, destination dir, compiler, artifacts subdir, phase, source dir, and a test wrapper. Helpers `add_extra_option()` and `add_to_filter_list()` build option strings. Build phase validates checksum names, computes separators for autotools versus CMake, generates configure when needed, configures/builds with selected encoders/decoders/filters/threading/shared/NLS/small/CLMUL/sandbox/doxygen settings, and handles an x32 config.guess workaround. Test phase runs `make check` or CMake `test`, copying logs to `build-aux/artifacts/<name>` on failure.

## State, Dependencies, and Integration
Default build state goes to `../xz_build`; source is `build-aux/../`. Dependencies include Bash, autotools or CMake, make, compiler toolchains, and optional wrappers like Valgrind. GitHub POSIX CI uses this script heavily.

## Risks and Test Signals
It is a key integration contract between CI YAML and build systems. Risks include string-built option quoting, stale CMake cache handling, and partial option parity between autotools and CMake. Its artifact-copying behavior improves failure diagnosis.
