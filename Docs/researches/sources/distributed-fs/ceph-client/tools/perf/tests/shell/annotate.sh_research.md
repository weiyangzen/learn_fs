<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/annotate.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/annotate.sh

## Purpose

This shell test verifies basic `perf annotate` output for file and pipe input modes, including target symbol visibility and disassembly output from default and explicit objdump disassemblers.

## Research

The script sources `lib/perf_has_symbol.sh` and skips unless the perf test binary has `noploop`. `test_basic` records `perf test -w noploop` either to a temp file or stdout pipe, runs `perf annotate --stdio --percent-limit 10`, checks for the `noploop` symbol and disassembly lines matching a percent/offset/instruction regex, repeats with an explicit symbol argument, then forces `--objdump=objdump`. State is temporary perf data and output, removed by traps. Dependencies are perf record/annotate, objdump, symbol availability, and sample generation in the workload. Integration covers annotate's input handling and disassembler plumbing. Risks include regex mismatch for nonstandard disassembly, low sample counts below percent limit, and missing debug/symbol setup. Passing signal is success in both Basic and Pipe modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/annotate.sh -->
