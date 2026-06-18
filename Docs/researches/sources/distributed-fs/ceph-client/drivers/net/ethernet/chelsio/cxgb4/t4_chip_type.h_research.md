# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_chip_type.h

## Purpose
Defines the compact chip-version/revision encoding used throughout the Chelsio T4/T5/T6 driver and provides helpers for chip family tests.

## Important APIs, Types, and Functions
Defines PCI device-ID version extraction with `CHELSIO_PCI_ID_VER`, family constants `CHELSIO_T4`, `CHELSIO_T5`, `CHELSIO_T6`, encoding/decoding macros `CHELSIO_CHIP_CODE`, `CHELSIO_CHIP_VERSION`, and `CHELSIO_CHIP_RELEASE`, enum values for `T4_A1`, `T4_A2`, `T5_A0`, `T5_A1`, `T6_A0`, first/last revision markers, and inline predicates `is_t4`, `is_t5`, and `is_t6`.

## Control Flow
Runtime logic is limited to inline family checks that compare `CHELSIO_CHIP_VERSION(chip)` against the family constants. All other behavior is compile-time macro expansion.

## State and Persistence Behavior
No mutable state exists. The encoded `enum chip_type` value is stored in adapter parameter structures elsewhere and acts as a stable hardware capability key across initialization, queue programming, register access, firmware selection, and debug collection.

## Dependencies and Integration Points
Included by `cxgb4.h`, which exposes `adapter->params.chip` to the whole driver. The predicates and version macro are used heavily in `sge.c`, `smt.c`, `cxgb4_main.c`, `t4_hw.c`, filter code, ethtool, debug collection, and ULD setup to select T4/T5/T6-specific register fields, WR formats, queue behavior, and feature availability.

## Risks
Incorrect encoding or PCI version extraction would misclassify hardware and select wrong firmware/register formats. Adding a new chip family requires updating constants, enum ranges, helper assumptions, firmware lookup, and every switch statement that treats unknown versions as errors. The helpers test only family, not revision-specific errata.

## Test Signals
Probe tests across T4/T5/T6 PCI IDs, firmware image selection, queue allocation on each family, debug register dump paths, and compile-time users of `is_t4`/`is_t5`/`is_t6` are the core validation signals.
