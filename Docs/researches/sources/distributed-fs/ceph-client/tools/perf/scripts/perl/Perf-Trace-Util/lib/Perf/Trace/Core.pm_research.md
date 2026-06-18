<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Core.pm -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Core.pm
Purpose: Perl utility module for perf script field formatting. It stores symbolic and flag field definitions and formats numeric trace flags into readable strings.

Important APIs/types/functions: Exports `define_flag_field`, `define_flag_value`, `flag_str`, `dump_flag_fields`, `define_symbolic_field`, `define_symbolic_value`, `symbol_str`, `dump_symbolic_fields`, and `trace_flag_str`. Internal hashes `%flag_fields` and `%symbolic_fields` hold event/field mappings.

Control flow: Perf's script generator or scripts populate mappings with define functions. Event handlers call `flag_str` or `symbol_str` to translate integer values. `trace_flag_str` formats common flags using `%trace_flags`.

State and persistence: Mapping state is global to the Perl interpreter process and lasts for the perf script run. Nothing is persisted to disk.

Dependencies and integration points: Used by Perl scripts under `scripts/perl`. It mirrors the Python `Core.py` behavior for cross-language script support.

Risks: Undefined mappings return empty/undef strings, so missing generated definitions can silently reduce output quality. All state is global and unnamespaced beyond event/field keys.

Test signals: `check-perf-trace.pl` exercises `symbol_str`, `flag_str`, `trace_flag_str`, and unhandled-event reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Core.pm -->
