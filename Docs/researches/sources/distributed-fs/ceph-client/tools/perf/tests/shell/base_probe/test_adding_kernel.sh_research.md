<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_adding_kernel.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_adding_kernel.sh

## Purpose

This exclusive perf-probe test exercises kernel probe add/list/use/delete workflows, dry-run, force-add, wildcard probes, invalid variable handling, and return-value probing.

## Research

After sourcing common init and probe helper code, it defaults `TEST_PROBE` to `inode_permission`, detects missing debuginfo, checks kprobe availability, and clears probes between stages. It tests plain, `-a`, and `--add` probe creation; `perf list` and `perf probe -l`; `perf stat` use with nonzero counts; deletion; removed-list absence; dry-run non-persistence; duplicate rejection and `--force` suffixing; equal counts from duplicate probes; wildcard deletion; wildcard adding of `vfs_* $params`; an intentionally missing variable that must not segfault; and `%return $retval` recording plus `perf script` argument output. State is kernel tracing probe state, perf.data under current test dir, and logs. Dependencies include debugfs, debuginfo for several checks, `/proc` workloads, and regex helpers. Risks are intrusive probe mutation, kernel symbol/name drift, permission failures, and sample count flakiness. Test signals combine perf exit codes with strict output pattern checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_adding_kernel.sh -->
