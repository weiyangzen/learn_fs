# Research: sources/distributed-fs/ceph-client/fs/nls/nls_ucs2_data.h

## Purpose

This header declares the shared data contract for UCS-2 uppercase conversion helpers. It exposes the compressed uppercase delta tables implemented in `nls_ucs2_utils.c` and consumed by inline functions in `nls_ucs2_utils.h`.

## Important APIs, Types, and Functions

`struct UniCaseRange` stores a start code point, end code point, and signed-char delta table. `extern signed char NlsUniUpperTable[512]` declares the base table for low Unicode values. `extern const struct UniCaseRange NlsUniUpperRange[]` declares the range table for sparse higher Unicode blocks.

## Control Flow

The header has no executable flow. Runtime lookup happens in `UniToupper()` by first indexing `NlsUniUpperTable` for values below its size and then scanning `NlsUniUpperRange`.

## State and Persistence Behavior

The header declares global uppercase data but owns no storage. Consumers rely on the data being linked from `nls_ucs2_utils.c`.

## Dependencies and Integration Points

It is included by `nls_ucs2_utils.h`. The type uses `wchar_t`, so consumers must include headers that define it before or through the utility header.

## Risks

The data contract assumes signed-char deltas are sufficient for every represented uppercase mapping. Any new range whose delta does not fit signed char would require a format change. Header and implementation must remain in sync.

## Test Signals

Build users that include the header, verify exported symbols resolve, and test uppercase conversion through `UniToupper()` for low-table and range-table values.
