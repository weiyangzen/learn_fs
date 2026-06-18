# sources/distributed-fs/ceph-client/lib/crypto/simd.c

## Purpose

This file provides a per-CPU testing control used by crypto SIMD helpers. It was read as a complete 11-line file.

## Important APIs, Types, and Functions

It defines and exports `DEFINE_PER_CPU(bool, crypto_simd_disabled_for_test)` via `EXPORT_PER_CPU_SYMBOL_GPL`.

## Control Flow

There is no executable control flow beyond per-CPU variable definition and export initialization.

## State and Persistence Behavior

The per-CPU boolean persists for the lifetime of the kernel/module and can be used by tests or internal helpers to suppress SIMD paths on a CPU-local basis.

## Dependencies and Integration Points

It depends on `<crypto/internal/simd.h>` and integrates with architecture crypto dispatch code that consults testing SIMD-disable state.

## Risks and Edge Cases

The main risk is test-only state leaking into non-test execution paths if callers set it incorrectly. Per-CPU semantics mean tests must control the CPU context they are validating.

## Test Signals

Forced generic fallback tests and KUnit paths that disable SIMD for architecture differential coverage exercise this file.
