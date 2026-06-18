# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/testcases.c

## Purpose

This file validates and manipulates arm64 signal-frame reserved records for the signal selftests. It is the central parser used by both good-context assertions and fake bad-context construction.

## Important APIs, Types, and Functions

Important validators are `validate_extra_context()`, `validate_sve_context()`, `validate_za_context()`, `validate_zt_context()`, and `validate_reserved()`. `get_starting_head()` finds or reclaims room in a sigframe reserved area for negative tests.

## Control Flow and Data Flow

`validate_reserved()` walks `_aarch64_ctx` records until a terminator, checks alignment, duplicates, record sizes, optional extra-context data, SVE/ZA/ZT VL validity, mandatory FPSIMD presence, and ZT-without-ZA invalidity. Unknown magic values are reported as possible test-suite staleness rather than hard ABI knowledge.

## State and Persistence Behavior

No persistent state is kept. Validation uses local flags to track seen context record types and returns an error string through the caller.

## Dependencies and Integration Points

It depends on `asm/sigcontext.h` record definitions and is called by `ASSERT_GOOD_CONTEXT()`, `ASSERT_BAD_CONTEXT()`, and live-context capture.

## Risks and Edge Cases

The parser must evolve with new signal context magic records. Bad size or missing terminator handling is security-sensitive because negative tests mirror kernel restore parsing.

## Test Signals

Good kernel-generated contexts validate successfully; handcrafted bad fake-sigreturn frames fail validation before being passed to the kernel.
