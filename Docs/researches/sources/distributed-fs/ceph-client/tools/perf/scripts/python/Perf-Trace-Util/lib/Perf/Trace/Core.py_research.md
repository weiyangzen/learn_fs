<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/Core.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/Core.py
Purpose: Python utility module for perf script field formatting. It mirrors the Perl Core module by storing flag/symbol mappings and formatting common trace flags.

Important APIs/types/functions: `autodict` creates recursive defaultdicts. Global `flag_fields` and `symbolic_fields` store definitions. Public functions are `define_flag_field`, `define_flag_value`, `define_symbolic_field`, `define_symbolic_value`, `flag_str`, `symbol_str`, `trace_flag_str`, and `taskState`. `EventHeaders` wraps common event header fields with nanosecond timestamp helpers.

Control flow: Generated script prologues or scripts populate mapping dictionaries. Event handlers call `flag_str`/`symbol_str` to translate numeric fields. `trace_flag_str` scans the fixed trace flag map and joins matched bits.

State and persistence: Mapping dictionaries are process-global for one script replay. `EventHeaders` instances are per-event objects. No disk persistence.

Dependencies and integration points: Depends only on `collections.defaultdict`. Imported by Python perf scripts, especially `check-perf-trace.py`.

Risks: Missing mappings produce empty strings. `taskState` only covers a small subset of states. Global mutable maps can be overwritten if scripts define the same event/field keys differently.

Test signals: `check-perf-trace.py` validates symbolic and flag formatting against real tracepoint fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/Core.py -->
