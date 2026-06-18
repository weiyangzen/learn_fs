# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/apx.c

## Purpose

`apx.c` is a minimal x86_64 xstate selftest entry point for APX state. It delegates all behavior to the generic xstate test framework.

## Important APIs, Types, and Functions

The file includes `xstate.h` and calls `test_xstate(XFEATURE_APX)` from `main()`.

## Control Flow

Execution immediately runs the generic xstate test suite for `XFEATURE_APX`. Feature probing, skip logic, context-switch validation, ptrace validation, and signal behavior are handled by `xstate.c`/`xstate.h`.

## State and Persistence Behavior

State is limited to process register/xstate manipulation performed by the xstate helper framework. There is no persistence.

## Dependencies and Integration Points

It depends on the x86 selftests build adding `xstate.c`, APX-aware kernel/CPU support, and generic xstate helper code.

## Risks and Edge Cases

The source itself has no local checks; all robustness depends on the shared xstate harness correctly handling unsupported APX environments.

## Test Signals

Pass/skip/fail signals are emitted by `test_xstate(XFEATURE_APX)`.
