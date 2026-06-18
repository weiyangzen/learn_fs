<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/header.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/header.h

## Purpose
`header.h` declares perf.data header constants, on-disk structures, in-memory header state, feature I/O helpers, and public APIs for reading, writing, injecting, processing, and printing perf headers and feature events.

## Important APIs, types, and functions
The `HEADER_*` enum assigns stable feature IDs from tracing data and build IDs through topology, BPF, compression, PMU capabilities, CPU domain info, ELF machine flags, and cacheline size. `struct perf_file_section`, `struct perf_file_header`, and `struct perf_pipe_file_header` describe serialized file/pipe headers. `struct perf_header` holds version, byte-swap requirement, offsets, feature bitmap, feature limit, and `perf_env`. `struct feat_fd` abstracts feature read/write against either a file descriptor or memory buffer. `struct perf_header_feature_ops`, `feat_writer`, and `feat_copier` define feature operation contracts.

## Control flow
Callers create or use a `perf_session`, then call `perf_session__read_header` for input or `perf_session__write_header`/`perf_session__inject_header` for output. Feature readers can use `perf_header__process_sections`; pipe readers feed feature events to `perf_event__process_feature`. Event attr/update/build-id processing APIs let stream readers reconstruct evlists and environment while consuming records.

## State and persistence
The declarations preserve the source of truth for the perf.data ABI. `HEADER_FEAT_BITS` is fixed at 256, and `DECLARE_BITMAP(adds_features, HEADER_FEAT_BITS)` appears in both serialized and in-memory structures. Header version, swap state, data size/offset, and feature offset are persisted or derived during reads.

## Dependencies and integration points
The header depends on Linux perf ABI types, bitmaps, `perf_env`, cpumap, stdio, and forward declarations for perf session/tool/event types. Architecture-specific implementations override CPUID hooks declared here.

## Risks
Changing enum ordering, struct layout, bitmap width, or function contracts breaks perf.data compatibility. `struct feat_fd` permits either `buf` or `fd`; misuse can route feature I/O to the wrong backend. The file exposes weak architecture hooks whose default behavior intentionally omits CPUID, so callers must tolerate missing CPU identifiers.

## Test signals
Compilation across architectures, ABI-size assertions or fixture reads, cross-endian header fixture tests, pipe-mode feature processing, and perf inject/record/report round trips are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/header.h -->
