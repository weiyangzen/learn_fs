<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_json_output_lint.py -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_json_output_lint.py

## Purpose

This Python linter validates line-delimited `perf stat -j` JSON output against expected keys, value types, and option-specific field counts.

## Research

The script parses flags describing the perf stat mode, reads JSON lines from stdin or `--file`, wraps them into an array, and validates each object. Helpers accept float/int, counter sentinel strings (`<not counted>`, `<not supported>`), metric `none`, and metric thresholds from a fixed set. `check_json_output` rejects unknown keys unless `--metric-only`, checks object length against expected counts for modes such as interval, system-wide, per-core/socket/node/die/cluster/cache, per-thread, event, and metric-only, with allowances for isolated metric values/groups and threshold fields. State is the input lines and parsed args. Dependencies are perf JSON schema documented in the man page and Python `json`. Risks include field-count churn as perf adds keys, `metric-unit`/metric-only exceptions masking unknown keys, and reading all input into memory. Passing signal is no RuntimeError; on failure it prints the original input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_json_output_lint.py -->
