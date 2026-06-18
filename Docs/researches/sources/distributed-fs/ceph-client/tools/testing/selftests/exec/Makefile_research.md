# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/Makefile

## Purpose
Build and runtime recipe for exec selftests covering execveat, non-regular exec errors, load alignment, recursion depth, null argv, check-exec, and generated helper assets.

## Important APIs, Types, And Functions
Defines `TEST_PROGS`, `TEST_GEN_PROGS`, `TEST_GEN_PROGS_EXTENDED`, `TEST_GEN_FILES`, alignment-derived PIE/static-PIE binaries, `LDLIBS += -lcap`, and build rules for scripts, symlinks, denatured executable, load-address variants, static `false`, and samples from `samples/check-exec`.

## Control Flow
kselftest builds C tests and helper programs, creates runtime files such as `script`, `subdir`, `execveat.symlink`, and `execveat.denatured`, and installs `Makefile` as a runtime dependency for execveat negative tests.

## State And Persistence
Generated files in `$(OUTPUT)` include executables, symlink, copied sample scripts, and directories. `EXTRA_CLEAN` removes moved/temporary artifacts.

## Dependencies And Integration Points
Requires kernel headers, libcap, bash, samples/check-exec sources, and linker support for `-z max-page-size` and static PIE variants.

## Risks
Generated runtime assets are tightly coupled to test expectations. Missing sample files or libcap breaks check-exec tests. Static ASLR/load alignment tests depend on toolchain/linker behavior.

## Test Signals
Successful build creates all named executables and helper files; runtime tests rely on exact file modes and names.
