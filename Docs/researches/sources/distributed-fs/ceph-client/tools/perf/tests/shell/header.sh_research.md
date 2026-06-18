<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/header.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/header.sh

## Purpose

This shell test validates `perf report --header-only -I` header output for file and pipe input modes.

## Research

`check_header_output` requires fields including captured time, hostname, OS release, arch, cpuid, nrcpus, event, cmdline, perf version, sibling topology, and total memory. `test_file` records `perf test -w noploop` to a temp file, reports its header, and checks fields. `test_pipe` streams `perf record -o -` directly into `perf report --header-only -I -i -` and applies the same checks. State is temporary perf.data and script output. Dependencies are perf record/report, header feature collection, topology data, and `noploop` workload. Risks include missing cpuid/topology fields on some architectures, pipe-mode metadata differences, and record permission issues. Passing signal is all expected field regexes found in both modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/header.sh -->
