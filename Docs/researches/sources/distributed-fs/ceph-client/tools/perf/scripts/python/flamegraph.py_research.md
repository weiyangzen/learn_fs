# sources/distributed-fs/ceph-client/tools/perf/scripts/python/flamegraph.py

## Purpose

`flamegraph.py` converts perf script sample events into a d3-flame-graph compatible stack tree and writes either an HTML flame graph or raw JSON. It is used by `perf script report flamegraph` and by the combined `perf script flamegraph ...` flow. It supports optional event-name filtering, output path selection, template selection, color scheme selection, and controlled template download.

## Important APIs, Types, and Functions

`Node` is the stack-tree node type. It stores `name`, `libtype` (`root`, `kernel`, or user-space empty string), sample `value`, and child nodes, and serializes to the compact JSON keys expected by the d3 template.

`FlameGraphCLI` owns parsed arguments and the root `Node("all", "root")`. `get_libtype_from_dso()` tags kernel frames from `[kernel.kallsyms]` or `/vmlinux`. `find_or_create_node()` performs linear child lookup and insertion. `process_event()` maps perf event dictionaries into folded tree paths. `get_report_header()` shells out to `perf report --header-only` unless input is `-`. `trace_end()` serializes the final tree, loads or downloads an HTML template when needed, substitutes JSON placeholders, validates the known CDN template MD5 when downloaded, and writes stdout or a file.

At module execution, `argparse` builds options and assigns perf-visible globals `process_event = cli.process_event` and `trace_end = cli.trace_end`.

## Control Flow and Data Flow

For each event, `process_event()` first filters by `event["ev_name"]` if `--event` was provided. It creates a top-level child per command, adding `(<pid>)` for user processes and treating pid `0` as kernel. If the event has a `callchain`, entries are reversed so the call stack is root-first and then inserted node by node. Without a callchain, the event's own `symbol` and `dso` become a single leaf. The leaf node's `value` increments by one sample.

At end of trace, the root stack is serialized. In JSON mode the output is `stacks.json` or the requested path. In HTML mode, the script reads a local d3-flame-graph template when present, may prompt or auto-download the upstream template when allowed, falls back to a minimal embedded HTML template on read failure, replaces `/** @options_json **/` and `/** @flamegraph_json **/`, and writes `flamegraph.html` or the requested output.

## State and Persistence Behavior

The main state is the in-memory tree of `Node` objects. Output is a JSON or HTML file unless `-o -` sends it to stdout. In HTML mode, the output embeds the complete stack JSON and report options. The script does not persist intermediate folded stacks. It may perform a network download for the template if the template path is missing and the user agrees or `--allow-download` is set.

## Dependencies and Integration Points

Dependencies are Python standard modules, perf's JSON-like Python event dictionaries, `perf report --header-only` for optional report context, and d3/d3-flame-graph assets referenced by the chosen HTML template. The wrapper `scripts/python/bin/flamegraph-report` invokes it under `perf script`.

The output schema uses d3-flame-graph's compact fields `n`, `l`, `v`, and `c`, with libtype tagging that can color kernel frames differently. HTML mode integrates with packaged `/usr/share/d3-flame-graph/d3-flamegraph-base.html` or the jsDelivr CDN.

## Risks and Edge Cases

Child lookup is linear, so traces with many siblings under the same node can be slower than a dict-backed tree. Events with missing expected keys such as `comm`, `sample`, or `callchain` can raise. Kernel/user classification relies on pid and DSO strings and can misclassify unusual samples. In live mode (`input == "-"`) the script refuses template download because stdin is occupied, so missing local templates require JSON output or preinstalled assets.

The downloaded template MD5 is hard-coded. Any upstream template change prompts the user or exits if declined. HTML output can depend on remote JavaScript/CSS if the minimal template is used or if the selected template references CDNs. `get_report_header()` failure is non-fatal but silently removes contextual header information except for a stderr message.

## Test Signals

Record with `perf record -g` and run `perf script report flamegraph`; verify `flamegraph.html` opens and contains non-empty stack data. Run `--format json -o -` on a small trace and validate JSON structure with root `all`. Run with `--event` on a multi-event perf.data and verify only that event contributes samples. Test missing template behavior with and without `--allow-download`, and test `input == "-"` live mode to ensure it does not prompt for download.
