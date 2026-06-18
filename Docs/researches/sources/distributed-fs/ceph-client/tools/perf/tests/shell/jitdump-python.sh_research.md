<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/jitdump-python.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/jitdump-python.sh

## Purpose

This shell test validates Python `-Xperf_jit` JIT dump integration with perf record, perf inject, build-id cache, and symbolized report output.

## Research

The script sources `lib/setup_python.sh`, probes `${PYTHON} -Xperf_jit` for `sys.is_stack_trampoline_active`, skips if unavailable, and records an inline Python program with nested `foo`, `bar`, and `baz` functions under `perf record -k 1 -g --call-graph dwarf`. It extracts the target PID from `perf report`, runs `DEBUGINFOD_URLS='' perf inject -j`, adds generated `/tmp/jitted-$PID-*.so` files to the build-id cache, counts `py::(foo|bar|baz):<stdin>` symbols in `perf report -s sym`, removes JIT DSOs from the cache, and cleans files. State includes perf data, `.jit` data, `/tmp/jit-$PID.dump`, generated JIT DSOs, and build-id cache entries. Dependencies are a Python with perf JIT support, DWARF call graphs, perf inject JIT support, and shell glob behavior. Risks include PID extraction ambiguity, missing generated DSOs causing glob literal issues, low samples, and global build-id cache mutation. Passing signal is at least one matching Python JIT symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/jitdump-python.sh -->
