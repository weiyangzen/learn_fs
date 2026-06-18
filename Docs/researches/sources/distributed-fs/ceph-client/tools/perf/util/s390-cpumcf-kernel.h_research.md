# sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumcf-kernel.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumcf-kernel.h` mirrors s390 CPU Measurement Counter Facility raw data structures and event constants needed by perf userspace decoders.

## Important APIs, Types, and Functions

Constants include `S390_CPUMCF_DIAG_DEF`, `PERF_EVENT_CPUM_CF_DIAG`, `PERF_EVENT_CPUM_SF_DIAG`, `PERF_EVENT_PAI_CRYPTO_ALL`, `PERF_EVENT_PAI_NNPA_ALL`, and counter-set identifiers `CPUMF_CTR_SET_BASIC`, `USER`, `CRYPTO`, `EXT`, and `MT_DIAG`. Types are `struct cf_ctrset_entry` for an 8-byte counter-set header and `struct cf_trailer_entry` for the 64-byte trailer with flags, versions, CPU speed, TOD timestamp/base, programming usage fields, and machine type.

## Control Flow

There is no executable flow. Decoders cast raw big-endian buffers to these layouts and convert fields before validation/printing.

## State and Persistence Behavior

The header defines raw event layouts only. It owns no storage and persists no state.

## Dependencies and Integration Points

It is used by `s390-sample-raw.c` and `s390-cpumsf.c` to decode counter-set diagnostic raw samples and combined sampling/counter events. The structures must match the kernel/perf ABI for s390 PMU data.

## Risks and Edge Cases

Bitfield layout and endian interpretation are architecture-sensitive. Any drift from kernel layout breaks raw decoding. User-space code must convert big-endian fields explicitly when running on other endian hosts.

## Test Signals

Binary fixture tests with known counter-set headers/trailers, endian conversion checks, struct size/layout checks against kernel ABI, and decoder validation tests are appropriate.
