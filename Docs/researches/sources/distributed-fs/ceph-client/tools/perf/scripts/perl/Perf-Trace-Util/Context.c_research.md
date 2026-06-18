<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/Context.c -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/Context.c
Purpose: Generated Perl XS bridge exposing selected perf scripting context fields to Perl perf scripts. It wraps libtraceevent helpers for common preempt count, common flags, and common lock depth.

Important APIs/types/functions: XS functions `XS_Perf__Trace__Context_common_pc`, `XS_Perf__Trace__Context_common_flags`, and `XS_Perf__Trace__Context_common_lock_depth` convert a Perl scalar integer back to `struct scripting_context *`, call `common_pc`, `common_flags`, or `common_lock_depth`, and return integer values. `boot_Perf__Trace__Context` registers these functions in the Perl module.

Control flow: Perl loads this extension through `Context.pm`. Each exported function validates a single argument, unwraps the pointer, calls the perf helper, pushes the result, and returns one value.

State and persistence: No persistent state; it operates on the live perf script context pointer passed for each event.

Dependencies and integration points: Depends on Perl XS headers and perf `util/trace-event.h`. It is generated from `Context.xs`, so edits should happen in the XS source, not here.

Risks: Pointer conversion trusts perf's generated script harness. ABI drift in `struct scripting_context` or helper availability would break runtime. The header warns that manual edits are overwritten.

Test signals: Perl `check-perf-trace.pl` exercises these functions via `common_pc`, `common_flags`, and `common_lock_depth`. Successful perf script execution validates the XS bridge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/Context.c -->
