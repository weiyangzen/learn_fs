<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/Context.c -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/Context.c
Purpose: Python C extension module `perf_trace_context` exposing selected perf script context helpers to Python scripts. It provides common trace fields, instruction bytes, itrace option parsing, source line/source code lookup, and perf config access.

Important APIs/types/functions: Helper `get_args` unwraps the Python capsule holding `struct scripting_context`. Exported methods include `common_pc`, `common_flags`, `common_lock_depth` when libtraceevent is available, `perf_sample_insn`, `perf_set_itrace_options`, `perf_sample_srcline`, `perf_sample_srccode`, and `perf_config_get`. `PyInit_perf_trace_context` registers the module and a placeholder `perf_script_context` attribute.

Control flow: Python scripts pass the current perf script context capsule. Each function validates arguments, accesses fields such as sample/al/session/map, calls perf utility helpers, converts results to Python objects, and returns them. Source lookup uses DSO/map address translation and optionally fetches a source line.

State and persistence: No module-level mutable state beyond module initialization. It reads live perf session/sample context and perf config; no files are written, but source lookup may read debug/source files through perf helpers.

Dependencies and integration points: Depends on Python C API and many perf internals: config, trace-event, event, symbol, thread, map, maps, auxtrace, session, srcline, and srccode. Used by Python perf scripts such as `check-perf-trace.py`, `arm-cs-trace-disasm.py`, and `event_analyzing_sample.py`.

Risks: Strongly coupled to perf internal structs and Python C API. `perf_set_itrace_options` refuses changes after synth opts are already set. Source and instruction lookup can return `None` when maps or debug data are missing.

Test signals: Python trace script self-tests, CoreSight disassembly/source printing, and PEBS sample analysis exercise the exported methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/Context.c -->
