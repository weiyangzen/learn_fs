<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/data_type_profiling.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/data_type_profiling.sh

## Purpose

This shell test validates `perf annotate --code-with-type` data type profiling for Rust and C workloads, in file and pipe modes.

## Research

The script first probes `perf mem record` support and skips if no PMU supports memory events. `test_basic_annotate` selects Rust `perf test -w code_with_type` expecting `# data-type: struct Buf`, or C `perf test -w datasym` expecting `# data-type: struct buf`. It skips the Rust case when `perf check feature -q rust` fails, records with `perf mem record` either to a file or stdout pipe, runs `perf annotate --code-with-type --stdio --percent-limit 1`, and greps for the target data-type header. State is temporary perf data and annotate output. Dependencies are perf mem PMU support, Rust workload build for Rust cases, debug/type info, and annotate type decoding. Risks include memory-event permission gaps, insufficient samples, type-name changes, and pipe mode hiding record errors. Passing signal is expected data-type text in all supported modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/data_type_profiling.sh -->
