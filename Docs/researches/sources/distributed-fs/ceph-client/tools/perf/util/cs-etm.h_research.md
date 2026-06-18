# sources/distributed-fs/ceph-client/tools/perf/util/cs-etm.h

## Purpose

`cs-etm.h` defines the public constants, metadata layouts, packet structures, and exported helpers for perf's CoreSight ETM/ETE auxtrace support. It is the contract shared by `cs-etm.c`, decoder callbacks, and the auxtrace-info producer/consumer format.

## Important APIs, Types, and Functions

The header defines auxtrace-info header fields (`CS_HEADER_VERSION`, `CS_PMU_TYPE_CPUS`, `CS_ETM_SNAPSHOT`), current metadata version `CS_HEADER_CURRENT_VERSION`, ETMv3/ETMv4/ETE metadata indexes, magic values, trace-ID validation, ETMv3/ETMv4 exception numbers, `enum cs_etm_sample_type`, `enum cs_etm_isa`, `struct cs_etm_packet`, and `struct cs_etm_packet_queue`. Public functions include `cs_etm__process_auxtrace_info()`, `cs_etm_get_default_config()`, and, when OpenCSD support is enabled, queue accessors and timestamp conversion helpers.

## Control Flow

There is no executable control flow beyond inline fallbacks. The declarations let callers parse metadata blocks, identify trace architecture, validate trace IDs, interpret decoder packet state, and call into full CoreSight processing when `HAVE_CSTRACE_SUPPORT` is compiled in. Without OpenCSD, `cs_etm__process_auxtrace_info_full()` reports a clear unsupported-feature error.

## State and Persistence Behavior

The header encodes persistent `perf.data` metadata layout semantics. Version 1 introduced per-CPU parameter counts, and version 2 introduced hardware ID packet trace IDs while keeping legacy metadata fields. `struct cs_etm_packet_queue` represents transient decoder output buffering with timestamps and circular packet storage. Trace IDs are constrained to valid CoreSight ranges, with `0` reserved by perf for per-thread aggregation.

## Dependencies and Integration Points

Dependencies include `debug.h`, `util/event.h`, Linux bit helpers, perf session/PMU declarations, and OpenCSD types when available. The metadata indexes must match both perf recording code and `cs-etm.c` readers. The packet structure integrates decoder callbacks with sample synthesis and branch-stack handling.

## Risks and Edge Cases

Metadata layouts must remain append-only for versioned compatibility. Wrong parameter counts or magic values break old-file decoding. The ETMv4 and ETE index layouts intentionally overlap for common fields but diverge for `TRCDEVARCH` and timestamp-source fields. The trace ID validity macro treats invalid metadata IDs as a signal that hardware ID packets carry the real IDs.

## Test Signals

Builds should pass with and without `HAVE_CSTRACE_SUPPORT`. Compatibility tests should parse v0, v1, and v2 auxtrace-info blocks; ETMv3, ETMv4, and ETE magic values; valid and invalid trace IDs; and packet queues with discontinuity, exception, range, and empty states.
