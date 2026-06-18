# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/sve_helpers.h

## Purpose

This header declares SVE/SME vector-length helper state and provides an inline reader for the SVCR system register.

## Important APIs, Types, and Functions

It defines `VLS_USE_SVE`, `VLS_USE_SME`, extern `vls`/`nvls`, declares `sve_fill_vls()`, and implements `get_svcr()` with an `mrs S3_3_C4_C2_2`.

## Control Flow and Data Flow

Testcases include this header to enumerate VLs and check that helper code has exited streaming/ZA state after grabbing a context.

## State and Persistence Behavior

The header owns no storage and exposes process-global vector-length arrays from `sve_helpers.c`.

## Dependencies and Integration Points

It integrates with SME/SVE signal tests and arm64 system-register access.

## Risks and Edge Cases

`get_svcr()` uses a raw sysreg encoding, so architectural renames or assembler support changes require review.

## Test Signals

SVE/SME context tests validate this header by checking expected vector lengths and zero SVCR after context capture.
