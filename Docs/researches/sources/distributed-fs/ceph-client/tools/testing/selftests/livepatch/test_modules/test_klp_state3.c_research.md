# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_state3.c

## Purpose

`test_klp_state3.c` creates another compatible cumulative state livepatch by directly including the implementation of `test_klp_state2.c`.

## Important APIs, Types, and Functions

The file has no independent functions beyond including `"test_klp_state2.c"`. Module identity comes from the build object name even though the code is shared.

## Control Flow and State

Its runtime control flow is identical to `test_klp_state2.c`: allocate or take over console loglevel state on patch, restore or pass back on unpatch, and use state version 2.

## Dependencies and Integration Points

It depends on the included source file and kbuild compiling it as a distinct module. It is used by `test-state.sh` to test multiple compatible cumulative patches.

## Risks and Test Signals

Risks are include-file coupling and accidental divergence if state2 changes incompatibly. Signals are the same logs as state2 but with module name `test_klp_state3`.
