# sources/distributed-fs/ceph-client/tools/perf/jvmti/jvmti_agent.c

### Purpose
`jvmti_agent.c` implements the low-level jitdump writer used by perf's Java JVMTI agent. It creates a perf-discoverable jitdump file and writes code load, debug info, and close records for JIT-compiled Java code.

### Important APIs, Types, And Functions
Public functions from `jvmti_agent.h` are `jvmti_open()`, `jvmti_close()`, `jvmti_write_code()`, and `jvmti_write_debug_info()`. Helpers include `create_jit_cache_dir()`, `perf_open_marker_file()`, `perf_close_marker_file()`, `get_e_machine()`, `perf_get_timestamp()`, and optional architecture timestamp support via `JITDUMP_USE_ARCH_TIMESTAMP`.

### Control Flow
`jvmti_open()` initializes timestamp mode, creates `$JITDUMPDIR/.debug/jit` or `$HOME/.debug/jit`, creates a dated temporary directory and `jit-<pid>.dump`, mmaps the file executable as a marker for perf, writes the jitdump header, and returns a `FILE *`. `jvmti_write_code()` writes a `JIT_CODE_LOAD` record, symbol name, and optional code bytes under `flockfile()`. `jvmti_write_debug_info()` writes source-line records. `jvmti_close()` writes `JIT_CODE_CLOSE`, closes the stream, and unmaps the marker.

### State And Persistence
Persistent output is the jitdump file under `.debug/jit`. Static state includes `jit_path`, `marker_addr`, timestamp mode, and a monotonically increasing code generation counter. Writes are protected at the `FILE *` level for multi-threaded JVM callbacks.

### Dependencies And Integration Points
It depends on perf's `util/jitdump.h`, Linux `/proc/self/exe` ELF headers, mmap marker behavior consumed by perf record/report, environment variables `JITDUMPDIR`, `HOME`, and `JITDUMP_USE_ARCH_TIMESTAMP`, and JVMTI-facing types from the header.

### Risks
Path construction can fail for long environment paths. `perf_open_marker_file()` leaks the raw fd path on some early error paths before `fdopen()`. Timestamp source must match perf's expectations. Debug info size calculations depend on all filenames being valid.

### Test Signals
Run a Java workload with the agent under `perf record`, then verify a jitdump file is produced, perf.data contains the marker mapping, `perf inject/report` resolves Java JIT symbols, and line info appears when available.
