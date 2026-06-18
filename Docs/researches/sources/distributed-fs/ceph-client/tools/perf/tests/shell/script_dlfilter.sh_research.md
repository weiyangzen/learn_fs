## sources/distributed-fs/ceph-client/tools/perf/tests/shell/script_dlfilter.sh

Purpose: validates `perf script --dlfilter` by compiling a small shared-object filter.
Important behavior: generates C code implementing `filter_event`, using `perf_dlfilter_fns.resolve_ip` to pass only samples whose symbol is `test_loop`.
Control flow: requires `cc`, records `perf test -w thloop`, compiles the filter against perf include files, links a shared object, and checks filtered script output contains `test_loop` and not unrelated perf symbols.
State and persistence: temp perf.data, C, object, and shared object files are removed.
Dependencies and integration: requires compiler, perf dlfilter header, dynamic loading, symbol resolution, and `thloop`.
Risks: compiler/include path issues are treated as skips; filtering validation is intentionally simple and may miss non-perf false positives.
Test signals: filtered output includes `test_loop` and excludes obvious `perf` symbols.
