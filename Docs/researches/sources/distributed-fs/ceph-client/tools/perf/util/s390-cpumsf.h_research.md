# sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf.h` declares the s390 CPU Measurement Sampling Facility auxtrace recording and report-processing entry points.

## Important APIs, Types, and Functions

It forward-declares `union perf_event`, `struct perf_session`, and `struct perf_pmu`, then declares `s390_cpumsf_recording_init` and `s390_cpumsf_process_auxtrace_info`.

## Control Flow

No executable flow exists in the header. Recording code calls the recording initializer for the s390 cpumsf PMU, and report/inject code calls the AUXTRACE_INFO processor to install decoding callbacks.

## State and Persistence Behavior

State is created by the implementation and attached to recording or session auxtrace machinery. The header itself owns no state.

## Dependencies and Integration Points

It is the public integration point between architecture-specific s390 auxtrace support and generic perf record/report auxtrace code.

## Risks and Edge Cases

Callers must only use these functions when the matching s390 PMU/AUXTRACE type is present. Error reporting is through integer return codes and an out-parameter for recording initialization.

## Test Signals

Compile coverage, recording initialization tests on s390-capable PMU fixtures, and AUXTRACE_INFO processing tests validate the declarations.
