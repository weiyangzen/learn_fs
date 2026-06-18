# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/test_signals.h

## Purpose

This header defines the descriptor ABI used by the arm64 signal selftest framework and feature flags used to gate testcases.

## Important APIs, Types, and Functions

It defines feature bits and masks for SSBS, SVE, SME, SME FA64, SME2, and GCS. `struct tdescr` contains identity, feature requirements, signal expectations, timeout, saved/live contexts, private data, and callback hooks for setup/init/cleanup/trigger/run/result checking. It declares external `tde`.

## Control Flow and Data Flow

Testcase source files initialize `tde`. The common wrapper and utilities read that descriptor to install handlers, check features, trigger signals, call the testcase's run callback, and decide pass/fail/skip.

## State and Persistence Behavior

The descriptor is mutable runtime state: the framework fills feature support, initialization status, live context pointers, pass/result flags, and token sanity fields.

## Dependencies and Integration Points

It depends on arm64 ptrace/hwcap headers, libc signal/ucontext types, and is included by all signal framework and testcase files.

## Risks and Edge Cases

`token` must remain the first field because `signals.S` writes it by offset. Callback contracts are implicit: `run` is mandatory, some signal expectations require `sig_trig` to have fired, and `sanity_disabled` weakens fake-sigreturn safety checks.

## Test Signals

Build failures catch descriptor signature drift. Runtime assertions in `test_setup()` catch missing mandatory fields.
