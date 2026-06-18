# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/sve_helpers.c

## Purpose

This helper enumerates supported SVE or SME vector lengths for signal-context tests.

## Important APIs, Types, and Functions

It defines global `vls[SVE_VQ_MAX]` and `nvls`, and implements `sve_fill_vls(bool use_sme, int min_vls)`. It uses `PR_SVE_SET_VL` or `PR_SME_SET_VL` and masks with the matching VL length mask.

## Control Flow and Data Flow

The function walks vector quads from `SVE_VQ_MAX` down to one, asks the kernel to set the VL, records the returned implemented VL, skips missing lengths, and stops if SME returns a larger VL than requested. It returns pass, fail, or skip based on the number of discovered VLs.

## State and Persistence Behavior

The global `vls` array and `nvls` persist for the testcase process. The current process SVE/SME VL is changed during enumeration.

## Dependencies and Integration Points

It depends on `asm/sigcontext.h`, `prctl()`, kselftest return codes, and is used by SVE/SME signal testcases.

## Risks and Edge Cases

`nvls` is not reset inside the function, so callers should invoke it once per process. SME VLs need not be consecutive or include the minimum, so the loop has special termination logic.

## Test Signals

Dependent tests skip when too few VLs are available, fail on PRCTL errors, and otherwise iterate `vls[0..nvls)`.
