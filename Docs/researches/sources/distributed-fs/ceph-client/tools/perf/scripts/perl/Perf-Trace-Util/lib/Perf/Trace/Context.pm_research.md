<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Context.pm -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Context.pm
Purpose: Perl module loader/exporter for the perf trace context XS extension.

Important APIs/types/functions: Exports `common_pc`, `common_flags`, and `common_lock_depth`. Uses `XSLoader::load('Perf::Trace::Context', $VERSION)` to load the compiled extension.

Control flow: Loading the module sets exporter metadata, loads XS symbols, and returns true. Perf scripts then call exported functions inside event handlers.

State and persistence: Only module metadata and exports are initialized. No persistent data is stored.

Dependencies and integration points: Depends on Perl 5.10, `Exporter`, `XSLoader`, and the compiled `Perf::Trace::Context` XS object. Used by Perl perf scripts that need fields not provided as handler arguments.

Risks: Missing or mismatched XS library prevents scripts from loading. Exported names must match the XS registration in `Context.c`.

Test signals: `check-perf-trace.pl` imports this module and prints uncommon context fields from real trace events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Context.pm -->
