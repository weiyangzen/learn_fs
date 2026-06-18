<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop_check_tid_10.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop_check_tid_10.sh

## Purpose

This CoreSight test records `thread_loop` with 10 threads and verifies the AUX trace contains trace identifiers for every thread reported by the workload.

## Research

The script sets `TEST=thread_loop`, sources `coresight.sh`, uses `ARGS="10 1"`, captures perf data and stdout paths, runs `SHOW_TID=1 perf record -s $PERFRECOPT -o "$DATA" "$BIN" $ARGS > $STDO`, then calls `perf_dump_aux_tid_verify "$DATA" "$STDO"`. State is perf data plus a stdout file containing decimal TIDs. Dependencies are the `thread_loop` binary, CoreSight ETM, sample identifier recording via `-s`, and helper parsing of `CID=` or `VMID=` from perf dump output. Risks include missing CIDs due to kernel reporting differences, trace loss for short-running threads, and stdout/perf timing races. Passing signal is no missing TID in helper verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop_check_tid_10.sh -->
