# sources/distributed-fs/ceph-client/tools/arch/x86/lib/memset_64.S

## Purpose
Provides the x86-64 assembly implementation of `__memset`/`memset`, with an FSRS fast-string alternative and a manual store-loop fallback.

## APIs, Types, and Functions
Exports `__memset` and aliases `memset`. Local fallback label is `memset_orig`.

## Control Flow, State, and Persistence
The fast path can use `rep stosb` under `X86_FEATURE_FSRS`, preserving the original destination as the return value. The fallback expands the byte value to a 64-bit repeated pattern, aligns the destination when possible, stores 64-byte chunks, then handles remaining 8-byte and byte tails.

## Dependencies and Integration
Includes linkage, export, CFI type, cpufeature, and alternative headers. Placed in `.noinstr.text` for low-level contexts.

## Risks and Test Signals
Risks include alignment adjustment errors for very small sizes, alternative feature gating mistakes, register convention violations, and performance regressions for short fills. Test signals are exhaustive size/alignment tests, value-pattern checks, return-value checks, noinstr validation, and hardware tests with FSRS enabled/disabled.
