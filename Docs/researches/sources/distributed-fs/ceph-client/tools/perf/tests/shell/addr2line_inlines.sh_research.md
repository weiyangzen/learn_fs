<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/addr2line_inlines.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/addr2line_inlines.sh

## Purpose

This shell test checks inline source-line unwinding in `perf script` using frame-pointer, DWARF, and LBR call graphs against the `inlineloop` perf test workload.

## Research

The script creates a temp directory, records `perf test -w inlineloop 1` into `perf.data`, runs `perf script --fields +srcline`, and greps for inlined `inlineloop.c:2.` entries plus a non-inlined parent on line `3.`. `test_fp`, `test_dwarf`, and `test_lbr` share the same validation; LBR skips when neither `cpu/caps/branches` nor `cpu_core/caps/branches` exists. State is temporary perf data and script output removed by traps. Dependencies are perf record/script, inline debug information, addr2line/srcline support, and architecture LBR support for the third case. Risks include compiler line-number changes, insufficient samples, and only DWARF truly supporting inline callchains despite fp/lbr coverage. Test signals are required grep matches and accumulated `err`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/addr2line_inlines.sh -->
