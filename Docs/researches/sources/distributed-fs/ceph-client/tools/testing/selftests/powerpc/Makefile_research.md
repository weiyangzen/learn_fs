# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/Makefile

## Purpose
Top-level dispatcher for PowerPC selftest subdirectories and common library objects.

## Important APIs, Types, and Functions
Defines `SUB_DIRS`, `TARGETS`, `CFLAGS`, `GIT_VERSION`, `all`, `run_tests`, `emit_tests`, `install`, `clean`, and pattern recursion into child Makefiles; includes `../lib.mk`.

## Control Flow
Build flow exports `OUTPUT`, builds `lib/`, then recurses over target subdirectories. Test-run flow delegates to each child directory, and install/clean recurse similarly.

## State and Persistence
Build state lives under `$(OUTPUT)` and child output directories. No runtime state is managed here.

## Dependencies and Integration Points
Integrates all PowerPC selftest families with kselftest. `GIT_VERSION` embeds source revision metadata in builds that use it.

## Risks and Test Signals
Risks are recursive make ordering and missing child directories. Test signal is that every listed target can build/run through the shared kselftest interface.
