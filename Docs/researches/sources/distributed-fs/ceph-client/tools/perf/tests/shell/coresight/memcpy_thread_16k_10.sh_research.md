<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread_16k_10.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread_16k_10.sh

## Purpose

This CoreSight shell test records the `memcpy_thread` workload with 10 threads copying 16 KiB blocks and verifies basic AUX trace packet counts.

## Research

The script sets `TEST=memcpy_thread`, sources `coresight.sh`, uses `ARGS="16 10 1"` and data variant `16k_10`, runs `perf record $PERFRECOPT -o "$DATA" "$BIN" $ARGS`, then calls `perf_dump_aux_verify "$DATA" 10 10 10`. State is the perf data file and helper-generated stat CSV. Dependencies are the installed/build `memcpy_thread` binary, `cs_etm` PMU, CoreSight ETM trace support, and enough system resources to allocate buffers for 10 threads. Risks are trace loss, skipped test on missing PMU/binary, and workload timing variance. Test signal is meeting minimum `I_ATOM_F`, `I_ASYNC`, and `I_TRACE_INFO` counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread_16k_10.sh -->
