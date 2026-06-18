# sources/distributed-fs/ceph-client/tools/perf/scripts/python/stackcollapse.py

Purpose: `stackcollapse.py` converts perf samples into folded stack lines suitable for flame graph tooling: `frame;frame;comm count`.

Important APIs and state: command options control PID/TID inclusion, comm inclusion, Java signature cleanup, and kernel annotation. `lines` is a `defaultdict(int)` keyed by folded stack string. `process_event` consumes perf sample dictionaries, and `trace_end` prints sorted results.

Control flow: each event builds a stack from `callchain` entries when present or from the sample symbol/DSO otherwise. `tidy_function_name` replaces semicolons, optionally tidies Java-style names, and annotates kernel kallsyms. The process name is appended as the logical root when enabled, optionally including pid/tid. The reversed stack string is counted. End-of-trace output is deterministic lexical order.

State and persistence: state accumulates in memory until `trace_end`; output is stdout only.

Dependencies, integration, risks, and tests: it depends on perf sample dictionaries with callchain entries, symbol names, DSO names, and sample PID/TID fields. Risks include memory growth proportional to distinct stacks, partial Java tidying, and `[unknown]` aggregation when symbols are missing. Test signals are folded-stack output accepted by flame graph tooling and stable counts for repeated stacks.
