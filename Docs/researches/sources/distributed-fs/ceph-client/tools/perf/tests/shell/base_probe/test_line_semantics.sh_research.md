<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_line_semantics.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_line_semantics.sh

## Purpose

This perf-probe test validates semantic parsing of `--line` descriptions for acceptable and unacceptable line patterns.

## Research

The script sources common init, skips without kprobe support, and records a DWARF hint when unavailable. It tests valid forms such as `func`, `func:10`, ranges, offsets, `func@source.c`, and `source.c:1+1`, requiring no “Semantic error”. It tests invalid forms such as nonnumeric line/range parts and a malformed lazy-pattern expression, requiring a semantic error. State is only accumulated test result and logs emitted by shared result helpers. Dependencies are perf probe parser, optional DWARF/source lookup, and regex output. Integration protects user-facing line syntax accepted by `perf probe --line`. Risks include valid syntax that still fails due to missing debuginfo, source file ambiguity, and wording changes around semantic errors. Test signal is matching parser acceptance/rejection for each pattern.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_line_semantics.sh -->
