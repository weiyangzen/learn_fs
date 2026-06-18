# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/testcases/testcases.h

## Purpose

This header defines common signal-frame test helpers, macros, context flags, and the fake sigframe structure used by arm64 signal testcases.

## Important APIs, Types, and Functions

It defines context flags (`FPSIMD_CTX`, `SVE_CTX`, `ZA_CTX`, `EXTRA_CTX`, `ZT_CTX`, `FPMR_CTX`, `GCS_CTX`), `KSFT_BAD_MAGIC`, reserved-area access macros, `ASSERT_BAD_CONTEXT()`, `ASSERT_GOOD_CONTEXT()`, `GET_RESV_NEXT_HEAD()`, `struct fake_sigframe`, `get_header()`, `get_terminator()`, `write_terminator_record()`, and `get_starting_head()`.

## Control Flow and Data Flow

Testcases use macros to locate `uc_mcontext.__reserved`, find or write context records, validate expected-good or expected-bad frames, and pass fake frames to `fake_sigreturn()`.

## State and Persistence Behavior

The header owns no state. Inline helpers operate on caller-provided `ucontext_t` or fake sigframe buffers.

## Dependencies and Integration Points

It depends on `asm/sigcontext.h`, libc signal/ucontext types, and the validator implementation in `testcases.c`.

## Risks and Edge Cases

`get_header()` trusts record sizes while walking, so callers use it on buffers already bounded by a reserved-size argument. `ASSERT_BAD_CONTEXT()` aborts if a supposedly bad context validates as good.

## Test Signals

All signal testcase builds and context assertions validate this header's contract.
