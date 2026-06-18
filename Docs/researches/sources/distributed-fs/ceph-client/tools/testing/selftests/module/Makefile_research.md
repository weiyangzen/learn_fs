<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/module/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/module/Makefile

## Purpose
Kselftest makefile for module-loading selftests. It declares a shell-only test program and avoids building binaries.

## Important APIs, Types, and Functions
- `all:` is intentionally empty so an argument-less make does not run tests.
- `TEST_PROGS := find_symbol.sh` registers the runtime test.
- Includes `../lib.mk` for kselftest build/run plumbing.
- `clean:` is empty because there are no generated artifacts.

## Control Flow
Kselftest infrastructure reads `TEST_PROGS` and runs `find_symbol.sh`. No compilation or cleanup work is performed in this makefile.

## State and Persistence Behavior
No local state. It does not generate files.

## Dependencies and Integration Points
Integrates with `tools/testing/selftests/lib.mk` and the module `config` file in this directory.

## Risks and Edge Cases
The empty `all` target is a deliberate guard against unexpected test execution during plain make. Any future generated binaries would need corresponding clean rules.

## Test Signals
Signals are delegated to `find_symbol.sh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/module/Makefile -->
