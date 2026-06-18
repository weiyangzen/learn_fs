# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/mte_def.h

## Purpose

This header provides local MTE constants and tag-manipulation macros so the selftests can build against older or sanitized headers that may not expose the newest arm64 MTE ABI definitions.

## Important APIs, Types, and Functions

It defines fallback values for `SEGV_MTEAERR`, `SEGV_MTESERR`, `PROT_MTE`, `HWCAP2_MTE`, and MTE PRCTL TCF bits. It also defines tag positions, tag masks, granule size/count, address-tag positions, PSTATE.TCO bit constants, alignment helpers, and inclusion/exclusion mask macros such as `MT_FETCH_TAG()`, `MT_SET_TAG()`, `MT_CLEAR_TAGS()`, and `MTE_ALLOW_NON_ZERO_TAG`.

## Control Flow and Data Flow

There is no control flow. The macros transform pointer-sized integers, align byte counts to 16-byte MTE granules, and construct tag inclusion masks passed to PRCTL.

## State and Persistence Behavior

The header carries no runtime state. Its constants persist as part of the test source and must remain ABI-compatible with Linux arm64 MTE definitions.

## Dependencies and Integration Points

It is included by both C utilities and `mte_helper.S`. It bridges kernel ABI values, MTE architectural layout, and selftest logic.

## Risks and Edge Cases

Incorrect fallback constants would make tests fail or silently test the wrong ABI on systems with older headers. Macro arguments are not fully parenthesized in every shift expression, so callers should pass simple integer expressions. `MT_ALIGN_UP(0)` returns 0, which the assembly range loops handle.

## Test Signals

Successful compilation against varying header versions and correct runtime behavior of all MTE tests validate the constants. Failures usually appear as wrong tag extraction, wrong PRCTL masks, or unexpected signal si_codes.
