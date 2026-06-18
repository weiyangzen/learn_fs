<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread_10.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread_10.sh

## Purpose

This CoreSight shell test records the unrolled-loop workload with 10 threads and verifies basic AUX trace packet counts.

## Research

The script sets `TEST=unroll_loop_thread`, sources `coresight.sh`, uses `ARGS="10"` and `DATV="10"`, records with `perf record $PERFRECOPT -o "$DATA" "$BIN" $ARGS`, then calls `perf_dump_aux_verify "$DATA" 10 10 10`. State is a perf data file and helper statistics. Dependencies are the built workload, arm64 CoreSight ETM PMU, and perf report dump decoding. Risks include trace loss due to high instruction volume, skipped test on missing binary/PMU, and threshold sensitivity to hardware buffer configuration. Passing signal is packet counts meeting all three minimums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread_10.sh -->
