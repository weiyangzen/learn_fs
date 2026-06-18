<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/coresight.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/coresight.sh

## Purpose

This sourced shell library centralizes CoreSight perf record options, workload discovery, skip logic, AUX packet sanity checks, and TID/CID validation.

## Research

It sets `PERFRECOPT` to `-m ,16M -e cs_etm//u`, derives `TOOLS`, `DIR`, and `BIN` from the caller's `TEST`, skips if the binary is not executable or `perf list pmu` lacks `cs_etm`, and honors `PERF_TEST_CORESIGHT_DATADIR` and `PERF_TEST_CORESIGHT_STATDIR`. `perf_dump_aux_verify` dumps perf data, counts `I_ATOM_F`, `I_ASYNC`, and `I_TRACE_INFO`, appends CSV stats, and enforces caller-supplied minimums. `perf_dump_aux_tid_verify` reads decimal TIDs from workload stdout and compares them to hex `CID=` or fallback `VMID=` identifiers in the AUX dump. State includes perf temp dump files and stats CSVs. Dependencies are ETMv4-style perf dump text, CoreSight PMU, and caller-defined `TEST`/`DATV`. Risks include packet-name changes, lossy trace causing false failures, use of `dirname $0` when sourced, and a typo in comments only. Passing signals are packet thresholds and complete TID coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/coresight.sh -->
