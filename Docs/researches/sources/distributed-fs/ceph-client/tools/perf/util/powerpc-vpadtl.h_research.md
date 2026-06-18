# sources/distributed-fs/ceph-client/tools/perf/util/powerpc-vpadtl.h

## Purpose
This header exposes the PowerPC VPA DTL auxtrace integration point and defines the private auxtrace info layout indexes used by perf data records.

## Important APIs, Types, and Functions
It defines `POWERPC_VPADTL_TYPE`, `VPADTL_AUXTRACE_PRIV_MAX`, `VPADTL_AUXTRACE_PRIV_SIZE`, and declares `powerpc_vpadtl_process_auxtrace_info(union perf_event *event, struct perf_session *session)`.

## Control Flow
There is no runtime control flow in the header. The declared function is invoked when a PowerPC VPA DTL `PERF_RECORD_AUXTRACE_INFO` record is encountered.

## State and Persistence
The header declares no state. The private-size macro describes how much auxtrace private data is expected in the perf event record.

## Dependencies and Integration Points
It forward-declares `union perf_event`, `struct perf_session`, and `struct perf_pmu`, and is consumed by auxtrace dispatch code and the implementation file.

## Risks
The enum order is part of the perf data auxtrace private ABI for this decoder. Any change must remain compatible with recorded data producers.

## Test Signals
Build tests should ensure the header is usable with forward declarations only. Auxtrace tests should validate that records smaller than `VPADTL_AUXTRACE_PRIV_SIZE` are rejected by the implementation.
