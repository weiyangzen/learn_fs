# Research: sources/distributed-fs/ceph-client/fs/nls/nls_ucs2_utils.c

## Purpose

This file provides exported UCS-2 uppercase conversion data derived from CIFS/server Unicode helpers. It is data-heavy support code for filesystems that need Windows-style or UCS-2 case-insensitive filename handling.

## Important APIs, Types, and Functions

`NlsUniUpperTable[512]` is an exported signed-char delta table for low Unicode values, including ASCII and Latin ranges. Range arrays `UniCaseRangeU03a0`, `UniCaseRangeU0430`, `UniCaseRangeU0490`, `UniCaseRangeU1e00`, and `UniCaseRangeUff40` cover Greek, Cyrillic, extended Cyrillic, extended Latin/Greek, and fullwidth Latin ranges. `NlsUniUpperRange[]` stitches those arrays into a sentinel-terminated table of `struct UniCaseRange`. Both `NlsUniUpperTable` and `NlsUniUpperRange` are exported with `EXPORT_SYMBOL_GPL`.

## Control Flow

There are no callable functions in this file beyond module metadata. Lookup control flow is implemented by inline consumers in the header: add the signed delta from the base table or from the first matching range table.

## State and Persistence Behavior

The exported tables are global static storage for the module/built-in kernel image. They are not mutated at runtime. Since the arrays define case-insensitive comparison behavior, changes can affect persistent filename lookup semantics for filesystems that depend on them.

## Dependencies and Integration Points

The file includes filesystem, module, slab, unaligned, and local UCS-2 utility headers. It integrates with any GPL kernel code that uses `UniToupper()`/`UniStrupr()` or directly references the exported tables.

## Risks

Signed-char deltas must be exact and within range. Range boundaries and sentinel order are critical because consumers scan ranges linearly. Case mapping is uppercase-only and compressed; it is not a full Unicode case-folding engine.

## Test Signals

Build/link tests should verify exported symbols. Functional tests should uppercase ASCII, Latin-1, Greek, Cyrillic, extended Latin, and fullwidth Latin values, and verify unmapped characters remain unchanged.
