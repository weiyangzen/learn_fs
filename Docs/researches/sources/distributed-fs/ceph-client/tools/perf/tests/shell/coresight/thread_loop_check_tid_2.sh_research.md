<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop_check_tid_2.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop_check_tid_2.sh

## Purpose

This CoreSight test records `thread_loop` with 2 longer-running threads and verifies TID-to-AUX trace coverage.

## Research

The script is parallel to the 10-thread variant but uses `ARGS="2 20"` and data variant `check-tid-2th`. It enables `SHOW_TID`, records with `perf record -s` and the CoreSight event options, writes workload stdout to a file, then passes perf data and stdout to `perf_dump_aux_tid_verify`. State is temporary/current-directory perf data and stdout. Dependencies are `thread_loop`, CoreSight ETM, perf dump exposing `CID` or `VMID`, and enough runtime for both threads to produce trace. Risks include missing identifiers due to trace truncation or kernel format changes, and the longer loop increasing runtime on slow systems. Passing signal is every printed TID matched against AUX trace identifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop_check_tid_2.sh -->
