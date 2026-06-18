# sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf-kernel.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf-kernel.h` mirrors s390 CPU Measurement Sampling Facility AUX trace sample block structures for userspace decoding.

## Important APIs, Types, and Functions

Constants are `S390_CPUMSF_PAGESZ` and `S390_CPUMSF_DIAG_DEF_FIRST`. Types are `struct hws_basic_entry` for basic-sampling data, `struct hws_diag_entry` for diagnostic data with flexible payload, `struct hws_combined_entry` for adjacent basic+diagnostic entries, and `struct hws_trailer_entry` for per-page trailer metadata, descriptor sizes, overflow count, timestamp, TOD base, and programming usage fields.

## Control Flow

There is no executable flow. AUX trace decoders validate page-sized buffers, read basic/diagnostic entries, and use trailer metadata to determine sizes and timestamps.

## State and Persistence Behavior

The header defines raw binary layouts only. It owns no memory or persistent state.

## Dependencies and Integration Points

It is consumed by `s390-cpumsf.c` for AUX trace dump and sample synthesis. Its layout must remain aligned with the s390 kernel PMU AUX trace ABI.

## Risks and Edge Cases

Bitfield order, endian conversion, page trailer positioning, and variable diagnostic descriptor sizes are high-risk areas. Older hardware may omit descriptor sizes, forcing decoder fallback by machine type.

## Test Signals

Tests should validate struct sizes and field extraction on known raw SDB pages, old-machine descriptor fallback cases, trailer timestamp conversion, invalid descriptor detection, and little-endian host decoding.
