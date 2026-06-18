<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt.h

## Purpose

`intel-pt.h` is the public perf-util header for Intel Processor Trace. It names the PMU, defines the auxtrace-info private-field indexes shared between recording and decoding, and declares the small API used by recording setup and perf session auxtrace processing.

## Important APIs, Types, and Functions

`INTEL_PT_PMU_NAME` is `"intel_pt"`. The enum indexes fields in `perf_record_auxtrace_info.priv`, including PMU type, time conversion, TSC/MTC capability bits, return-compression bit, sched-switch availability, snapshot and per-cpu mmap mode, CYC capability, max non-turbo ratio, filter-string length, and `INTEL_PT_AUXTRACE_PRIV_MAX`. The declared functions are `intel_pt_recording_init()`, `intel_pt_process_auxtrace_info()`, and `intel_pt_pmu_default_config()`.

## Control Flow

The header has no executable flow. Recording code uses it to initialize Intel PT recording and populate auxtrace metadata. Reporting/inject code calls `intel_pt_process_auxtrace_info()` when it sees an Intel PT AUXTRACE_INFO record, which hands control to `intel-pt.c`.

## State and Persistence Behavior

The enum is a persistent ABI-like contract inside perf data files: producer and consumer must agree on each private-field position. Adding fields requires preserving old positions and checking record size in the decoder.

## Dependencies and Integration Points

It forward-declares perf session, tool, PMU, attr, auxtrace, and perf event types to avoid heavy includes. It integrates `builtin-record`-side Intel PT setup with perf report/script/inject auxtrace decoding.

## Risks and Edge Cases

The main risk is changing enum order or meaning, which breaks old perf.data decoding. Consumers must tolerate absent newer fields by checking record size, as `intel-pt.c` does with `intel_pt_has()`.

## Test Signals

Compatibility tests should record with one perf version and report with another, verify default PMU config generation, and check that old auxtrace-info records lacking newer enum fields still decode or fail gracefully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt.h -->
