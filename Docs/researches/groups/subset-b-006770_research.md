# subset-b-006770 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/scripting-engines/trace-event-python.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/scripting-engines/trace-event-python.c

`trace-event-python.c` implements perf script's Python scripting engine. It embeds CPython, loads a user Python script, converts perf samples, tracepoint payloads, stats, context switches, AUX errors, and db-export records into Python tuples/dictionaries, and registers the resulting callbacks through `python_scripting_ops`.

Important entry points are `python_start_script()`, `python_stop_script()`, `python_process_event()`, `python_process_switch()`, `python_process_auxtrace_error()`, `python_process_stat()`, `python_process_stat_interval()`, `python_process_throttle()`, and `python_generate_script()`. The exported `struct scripting_ops python_scripting_ops` binds those functions to the perf scripting framework. Global interpreter state is held in `main_module`, `main_dict`, and `tables_global`; the external `scripting_context` is exposed to Python via a `PyCapsule`.

The file has two major delivery modes. In normal script mode, perf events become calls to tracepoint-specific handlers such as `system__event`, a generic `process_event(dict)` handler, `context_switch`, `throttle`, `unthrottle`, `auxtrace_error`, `stat__<evsel>`, and `stat__interval`. In database export mode, `set_table_handlers()` checks Python globals such as `perf_db_export_mode`, `perf_db_export_calls`, and `perf_db_export_callchains`, initializes `struct db_export`, and routes samples and metadata through table handlers like `evsel_table`, `machine_table`, `thread_table`, `comm_table`, `dso_table`, `symbol_table`, `sample_table`, `call_path_table`, `call_return_table`, and `context_switch`.

The tracepoint path is compiled only with `HAVE_LIBTRACEEVENT`. `python_process_tracepoint()` resolves the `tep_event`, constructs the handler name, defines flag and symbolic fields once via `define_event_symbols()`, extracts common fields and event fields from raw payloads, optionally falls back to `trace_unhandled`, and appends an all-fields `perf_sample_dict` when the Python handler advertises one more argument. Numeric fields are decoded with `get_field_numeric_entry()`, arrays and strings are emitted as Unicode or byte arrays, and common metadata includes CPU, seconds/nanoseconds, PID, comm, and resolved callchain.

For non-tracepoint samples, `python_process_general_event()` builds a single comprehensive dictionary through `get_perf_sample_dict()`. That dictionary includes event name, raw `perf_event_attr`, sample ids, pid/tid/cpu/ip/time/period/address fields, read values, weight, data source and decoded memory info, raw bytes, comm, DSO/build-id/map/symbol information, callchain, branch stack, branch stack symbols, guest machine/vcpu data, cpumode, sample flags, IPC counters, and selected register dumps. Helpers such as `python_process_callchain()`, `python_process_brstack()`, `python_process_brstacksym()`, `set_sample_read_in_dict()`, `set_sample_datasrc_in_dict()`, `set_regs_in_dict()`, and `set_sym_in_dict()` isolate the object-building work.

Control flow starts in `python_start_script()`: it decodes `argv` to wide strings, appends the built-in `perf_trace_context` module, initializes Python, sets `sys.argv`, runs the user script file, initializes the main module and context capsule in `run_start_sub()`, invokes optional `trace_begin`, and configures db export callbacks. `python_stop_script()` calls optional `trace_end`, tears down db export state, decrefs retained Python objects, and finalizes CPython. `python_flush_script()` is currently a no-op. Error handling is intentionally fatal for Python callback failures and allocation failures: `handler_call_die()` prints the Python exception and calls `Py_FatalError()`.

State and persistence are process-local. The engine stores Python references, db-export callback pointers, call-return/call-path processors, and a global `struct tables`; it does not persist data itself except when `python_generate_script()` writes a generated `outfile.py`. Python callbacks may persist results externally. Reference ownership is delicate: most tuple setters transfer references to tuples, while `pydict_set_item_string_decref()` compensates for dictionary insertion not stealing references.

Dependencies include CPython C API, optional libtraceevent (`event-parse.h`), perf internals for events, evsels, callchains, threads, maps, symbols, db export, memory decoding, stats, thread maps, build IDs, and register naming. Integration points are perf script's scripting engine registry, generated Python handler scripts under perf's Python support tree, db-export consumers, AUX trace decoding, and tracepoint format metadata from libtraceevent.

Risks include fatal interpreter termination on script exceptions, strong assumptions about Python C API reference ownership, global interpreter state that is not designed for multiple independent Python sessions, `sprintf()`/fixed buffers in generated-script and handler-name paths, handler arity probing that depends on `__code__.co_argcount`, tracepoint support disappearing when built without libtraceevent, and many nullability assumptions around resolved threads/maps/symbols. `get_argument_count()` contains a suspicious duplicated assignment expression but functionally retrieves `__code__`.

Test signals should include running `perf script -s script.py` with tracepoint and non-tracepoint samples, exercising `process_event`, `trace_unhandled`, tracepoint-specific handlers with and without `perf_sample_dict`, db export mode with each table handler, callchain/branch-stack/register/data-source samples, context switch/throttle/AUX error/stat callbacks, generated script output from `perf script -g python`, and a build without libtraceevent to validate the fallback diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/scripting-engines/trace-event-python.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/session.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/session.c

`session.c` implements the core lifecycle and event-processing machinery for `struct perf_session`. It opens perf data, validates headers and event lists, creates machine/kernel maps, handles endian conversion, reads events from pipes, regular files, compressed records, and directory-style perf.data layouts, delivers events to `struct perf_tool` callbacks, maintains ordered-event queues, emits diagnostics, and exposes utility APIs for session metadata and lookup.

Construction is centered on `__perf_session__new()`. It allocates the session, initializes machines, ordered events, environment and decompression state, opens `struct perf_data` when supplied, reads and validates headers with `perf_session__open()`, initializes trace raw sample handling, opens directory data when needed, sets kallsyms defaults, assigns `evlist->session`, configures single-address-space state, and creates kernel maps for write/live sessions. `perf_session__delete()` frees auxtrace state, auxtrace indexes, debuginfo cache, kernel maps, decompressed event mmaps, environment, machines, evlist, data file handles, optional traceevent resources, and the session itself.

The public event-processing entry point is `perf_session__process_events()`. It registers the idle thread, then dispatches to `__perf_session__process_pipe_events()` for pipes, `__perf_session__process_dir_events()` for multi-file directory data, or `__perf_session__process_events()` for a regular perf.data file. All paths eventually use `perf_session__process_event()` or `perf_session__process_user_event()` to byte-swap, count, queue, skip, or deliver records.

Event delivery splits kernel record types from user/header record types. `perf_session__process_event()` swaps event payloads if the file endian differs, rejects malformed unknown headers, increments event stats, routes user records to `perf_session__process_user_event()`, and either queues timestamped events in `ordered_events` or immediately calls `perf_session__deliver_event()`. `perf_session__process_user_event()` handles metadata records such as `HEADER_ATTR`, `EVENT_UPDATE`, tracing data, build ids, finished rounds, ID index, AUX trace info/data/errors, thread/cpu maps, stat records, time conversion, feature records, compressed records, finished init, BPF metadata, and schedstat records.

Sample delivery is handled by `perf_session__deliver_event()` and `machines__deliver_event()`. Samples are parsed into `struct perf_sample`, first offered to auxtrace, then associated with an evsel and a host or guest machine via `machines__find_for_cpumode()`. The switch statement dispatches to the appropriate `perf_tool` callback for sample, mmap/mmap2, comm, namespace, cgroup, fork/exit, lost/lost-samples, read, throttle, AUX, itrace start, context switch, ksymbol, BPF, text poke, AUX output hw id, and deferred callchain records. It also updates loss/collision/partial counters and stores unresolved deferred-callchain samples until matching callchain records arrive.

The file contains a large endian-conversion table. `perf_event__attr_swap()` swaps `perf_event_attr` fields with size guards and reverses bitfields. Per-record helpers swap mmap, mmap2, comm, fork/exit, read, aux, itrace, switch, text poke, throttle, namespaces, cgroup, header attr, event update/type, tracing data, auxtrace info/data/error, thread map, CPU map, stat config/stat/round, and time conversion payloads. `perf_event_header__bswap()` swaps the common header, and `event_swap()` selects the correct payload swapper from `perf_event__swap_ops`.

The regular-file reader uses `struct reader`, `reader__init()`, `reader__mmap()`, `reader__read_event()`, and `reader__process_events()`. On 64-bit builds it prefers one large mapping; on 32-bit builds it uses 32 MiB windows. `prefetch_event()` validates whether an event header and full event fit in the current mapping and signals remap or invalid input. Compressed records append decompressed event buffers to `session->active_decomp`; `__perf_session__process_decomp_events()` drains complete events from the current decompression queue. Directory processing constructs one reader per data file and round-robins them in 2 MiB slices to match ordered-event behavior.

Pipe processing reads one header and variable-sized body at a time through `perf_data__read()`, reallocates the buffer as needed, processes compressed output after each event, updates optional progress, and performs final ordered/deferred/auxtrace/thread-stack flushes. Regular and directory paths do the same final flush sequence and warn about observed losses or malformed data unless `tool->no_warn` is set. The global `volatile sig_atomic_t session_done` and `session_done()` macro allow processing loops to stop on signal-driven cancellation.

State is held in `struct perf_session`: header/env, machines, evlist, auxtrace, time conversion, ordered-event queue, data pointer, tool callbacks, compression/decompression data, mmap bookkeeping, byte counters, and active decompression context. Additional transient state includes deferred samples in `evlist`, reader mmaps and zstd state, ordered-event queues, auxtrace event queues, and per-evlist stats. Persistent interaction is limited to reading and occasionally seeking within perf.data files, mmaping file contents, in-place update mappings when requested, and metadata derived from perf.data paths.

Other public utilities include `perf_session__peek_event()` and `perf_session__peek_events()` for random inspection, `perf_session__queue_event()`, `perf_session__deliver_synth_event()`, `perf_session__deliver_synth_attr_event()`, `perf_session__findnew()`, `perf_session__register_idle_thread()`, `perf_session__has_traces()`, `perf_session__has_switch_events()`, DSO/machine/stat fprintf helpers, `perf_session__dump_kmaps()`, `perf_session__find_first_evtype()`, `perf_session__cpu_bitmap()`, `perf_session__fprintf_info()`, `perf_event__process_id_index()` for guest/id metadata, `perf_session__dsos_hit_all()`, `perf_session__env()`, and `perf_session__e_machine()`.

Dependencies are broad perf internals: data/header parsing, evlist/evsel/sample parsing, machines/threads/maps/symbols, auxtrace, ordered events, zstd compression helpers, UI progress/warnings, perf stats, thread stacks, build/kernel map management, CPU maps, and Linux mmap/read/lseek APIs. Integration points are nearly every perf command that records, reads, reports, scripts, injects, or transforms perf.data.

Risks include malformed perf.data causing invalid sizes or remap loops, endian-swap correctness across every record variant, stale or missing sample ids causing dropped samples, deferred callchain memory growth if matching records never arrive until flush, compressed-event partial buffers, directory reader fairness and ordering assumptions, reliance on `sample_id_all` for ordered processing, use of writable private mappings for swap-on-read, and careful cleanup of mmaps/zstd/decompressed buffers on errors. `prefetch_event()` explicitly treats overlarge events as possible fuzzed or compressed input.

Test signals should cover perf.data read/write compatibility, pipe mode, directory mode, compressed and uncompressed records, opposite-endian fixtures, unknown/future event records, AUX trace records, ordered versus unordered delivery, lost/lost-samples warnings, deferred callchain merge and final flush, guest ID index records, CPU bitmap validation, random `peek_event()` reads, early termination via `session_done`, and sanitizer/fuzzer runs over event-size and payload-boundary handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/session.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/session.h

`session.h` declares the central `struct perf_session` type and the public API for creating, processing, inspecting, and reporting perf sessions. A perf session represents the active state for live or file-backed perf data: header/environment, machines, events, auxtrace, ordered-event processing, compression/decompression, data source, and tool callback integration.

The key types are `struct decomp_data`, `struct perf_session`, and `struct decomp`. `decomp_data` links decompressed event buffers and their zstd context. `perf_session` owns `struct perf_header`, `struct machines`, an `evlist`, auxtrace hooks/options/indexes, optional libtraceevent state, last time-conversion record, trace repipe flag, single-mmap bookkeeping, `ordered_events`, `perf_data`, `perf_tool`, compression byte counters, global zstd state, and active decompression context. `struct decomp` describes one mmap-backed decompressed buffer with file position/path, mapping length, head offset, size, and inline data.

Construction APIs are `__perf_session__new()` and the inline `perf_session__new()` wrapper, followed by `perf_session__delete()`. Processing APIs include `perf_session__process_events()`, `perf_session__queue_event()`, `perf_session__deliver_synth_event()`, and `perf_session__deliver_synth_attr_event()`. Inspection APIs include `perf_session__peek_event()`, `perf_session__peek_events()`, `perf_session__has_traces()`, `perf_session__has_switch_events()`, `perf_session__find_machine()`, `perf_session__findnew_machine()`, `perf_session__findnew()`, and `perf_session__find_first_evtype()`.

The header also exports byte-order and metadata helpers: `perf_event_header__bswap()`, `perf_event__attr_swap()`, `perf_event__process_id_index()`, `perf_event__process_finished_round()`, `perf_session__set_id_hdr_size()`, `perf_session__create_kernel_maps()`, `perf_session__register_idle_thread()`, `perf_session__cpu_bitmap()`, `perf_session__env()`, and `perf_session__e_machine()`. Reporting helpers include `perf_session__fprintf()`, `perf_session__fprintf_dsos()`, `perf_session__fprintf_dsos_buildid()`, `perf_session__fprintf_nr_events()`, `perf_session__dump_kmaps()`, and `perf_session__fprintf_info()`.

State and persistence behavior are defined by ownership boundaries rather than implementation. `perf_session` owns and releases most of the runtime graph rooted at machines, evlist, auxtrace, environment, and decompression buffers. The `data` pointer connects the session to persisted perf.data input or output, while `tool` connects it to command-specific callbacks. `one_mmap` fields allow fast random access into a single mmapped data file.

Dependencies include perf event/header/data abstractions, machine state, ordered events, compression helpers, Linux rbtrees and perf_event ABI definitions, and optional libtraceevent through `trace-event.h`. Integration points are all perf utility code that needs a stable session object, especially report/script/inject/record-style tools and auxtrace decoders.

Risks include mismanaged ownership between `perf_data`, `evlist`, and session deletion, stale `active_decomp` pointers, incorrect assumptions about whether `one_mmap_addr` is valid, and callers bypassing validation before using peek or event-processing APIs. Because many callbacks are declared against forward types, ABI consistency with the implementing C files is essential.

Test signals should verify construction/destruction in read, write, live/no-data, pipe, and directory modes; synthetic event delivery; byte-swap declarations matching implementations; machine lookup helpers; CPU bitmap behavior; and cleanup of compression and auxtrace resources under early errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/session.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/setns.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/setns.c

`setns.c` provides a tiny compatibility wrapper for `setns(2)`. It defines `int setns(int fd, int nstype)` and directly invokes `syscall(__NR_setns, fd, nstype)`.

The file exists for build environments or libc versions where the libc `setns()` declaration/symbol is not available to perf. The API matches the Linux system call wrapper: `fd` identifies an opened namespace file descriptor and `nstype` constrains the namespace type or is zero.

There is no internal state and no persistence. The function returns the kernel syscall result directly, with errors surfaced through `-1` and `errno` as with `syscall(2)`.

Dependencies are `namespaces.h`, `<unistd.h>`, and `<sys/syscall.h>`. Integration points are perf namespace-handling code that must enter target namespaces, for example side-band build-id or symbol collection.

Risks are mostly portability and symbol-collision related: if libc already exposes `setns`, build configuration must avoid duplicate definitions; if `__NR_setns` is absent on a target architecture, compilation fails. Runtime permission and namespace-type failures are delegated to the kernel.

Test signals include compiling on libc versions with and without native `setns`, running namespace-aware perf flows, and checking that invalid descriptors/type masks return the expected kernel errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/setns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/setup.py -->
# sources/distributed-fs/ceph-client/tools/perf/util/setup.py

`setup.py` builds perf's Python extension module named `perf`. It adapts compiler flags from the surrounding Linux/perf build, filters incompatible Python sysconfig flags for clang, and defines custom setuptools commands so extension artifacts are emitted into build directories selected by environment variables.

Required environment inputs are `CC` and `srctree`; the script asserts both. `CC` may include extra options, as in cross or Yocto builds, so the script splits the executable from `cc_options`. It detects clang by running `CC -v` and checking stderr for `clang version`. `src_feature_tests` points at `tools/build/feature`, and `clang_has_option()` compiles `test-hello.c` with a candidate option to detect unsupported clang flags.

When clang is used, the script mutates `sysconfig.get_config_vars()` for `CFLAGS` and `OPT`, removing `-specs=...` and removing options that the detected clang cannot handle, including `-mcet`, `-fcf-protection`, `-fstack-clash-protection`, `-fstack-protector-strong`, `-fno-semantic-interposition`, `-ffat-lto-objects`, `-ftree-loop-distribute-patterns`, and `-gno-variable-location-views`. This prevents Python's build configuration from injecting GCC-oriented flags into the perf extension build.

The custom `build_ext` and `install_lib` classes override `finalize_options()` to force `build_lib`, `build_temp`, and install build directory values from `PYTHON_EXTBUILD_LIB` and `PYTHON_EXTBUILD_TMP`. The `perf` extension compiles `tools/perf/util/python.c`, includes `util/include`, and appends warning/aliasing flags. Clang gets `-Wno-unused-command-line-argument` and optionally `-Wno-cast-function-type-mismatch`; non-clang gets `-Wno-cast-function-type`. All builds add `-fno-strict-aliasing`, write-string/unused/redundant-decl suppressions, and `-Wno-declaration-after-statement`.

State and persistence are build-system side effects: it reads environment variables and compiler diagnostics, mutates Python sysconfig variables in-process, and writes compiled extension outputs through setuptools into the configured build directories. It does not persist configuration files.

Dependencies include Python setuptools, sysconfig, subprocess, regex substitution, shell-like splitting, the Linux source tree, a working C compiler, and the perf `util/python.c` source. Integration points are perf's Makefile/build flow for Python bindings and distro/cross-build systems that set `CC`, `CFLAGS`, `srctree`, and Python extension build directories.

Risks include naive `cc.split()` handling quoted compiler paths or options, possible blocking or partial stderr reads from `Popen([cc, "-v"])`, repeated compiler probes for clang options, assertions producing abrupt failures when environment variables are omitted, and direct mutation of global sysconfig flags affecting any later setuptools behavior in the same process. `build_lib` and `build_tmp` may be `None` if the expected environment variables are missing.

Test signals should include GCC and clang builds, clang builds with GCC-only Python flags, cross-build `CC` values with sysroot/options, missing environment variable failures, build directory overrides, and importing the resulting `perf` Python module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/setup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sharded_mutex.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/sharded_mutex.c

`sharded_mutex.c` implements allocation and destruction for a hash-sharded mutex pool. The pool lets many logical objects share a fixed number of mutexes selected by hash, reducing per-object memory overhead at the cost of possible lock collisions.

`sharded_mutex__new(size_t num_shards)` rounds the requested shard count up to the next power of two by computing `cap_bits`, allocates one `struct sharded_mutex` plus `1 << cap_bits` flexible-array mutexes, stores `cap_bits`, initializes each mutex with `mutex_init()`, and returns the pool. Allocation failure returns `NULL`.

`sharded_mutex__delete(struct sharded_mutex *sm)` destroys each mutex with `mutex_destroy()` and frees the allocation. It assumes `sm` is non-null and that no thread still owns or waits on any shard.

State is entirely heap-local to the returned pool. There is no persistence. The power-of-two capacity is persisted in `cap_bits`, and callers use the inline getter from the header to map hashes to mutexes.

Dependencies are `sharded_mutex.h`, `mutex.h`, and standard allocation. Integration points are perf data structures that need low-overhead per-object locking with stable hashes.

Risks include undefined behavior for `num_shards == 0` if callers expect no mutexes, shift overflow for extremely large `num_shards`, no cleanup path if a later `mutex_init()` could fail on a platform where it returns errors, and null dereference if `sharded_mutex__delete(NULL)` is called. Lock contention depends on shard count and hash quality.

Test signals should cover creation with one, exact power-of-two, and non-power-of-two shard counts; hash-to-shard distribution through the header inline; multithreaded lock/unlock use; deletion after all locks are released; and boundary handling for zero or very large counts if the caller surface permits them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sharded_mutex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sharded_mutex.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/sharded_mutex.h

`sharded_mutex.h` declares a compact lock-sharding abstraction for perf. It explains the motivation: a mutex per object can be memory-expensive, so objects with stable hashes can share a global pool of mutexes, accepting collisions when the shard count is too small.

The main type is `struct sharded_mutex`, containing `cap_bits` and a flexible array `struct mutex mutexes[]`. The mutex array size is `1 << cap_bits`, allowing fast hash masking through `hash_bits()`.

Public APIs are `sharded_mutex__new(size_t num_shards)`, `sharded_mutex__delete(struct sharded_mutex *sm)`, and the inline `sharded_mutex__get_mutex(struct sharded_mutex *sm, size_t hash)`. The getter returns `&sm->mutexes[hash_bits(hash, sm->cap_bits)]`, so callers can lock the returned mutex using the normal perf mutex API.

State is owned by the heap allocation created in the C file. The header does not track object-to-lock ownership; correctness depends on callers using the same hash for related critical sections and avoiding deletion while locks may still be used.

Dependencies are `mutex.h` and `hashmap.h` for the mutex type and `hash_bits()`. Integration points are shared perf containers or caches that need coarse but scalable synchronization.

Risks include collision-induced contention, deadlocks if callers acquire multiple shard mutexes without a consistent order, invalid access after deletion, and poor behavior if `cap_bits` is derived from an unsuitable shard count. The flexible-array layout ties allocation and initialization tightly to `sharded_mutex__new()`.

Test signals include deterministic mapping for known hashes, concurrent callers sharing identical hashes, contention under intentionally small shard counts, and static/build checks that the flexible-array allocation matches the header layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sharded_mutex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sideband_evlist.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/sideband_evlist.c

`sideband_evlist.c` manages a side-band perf event list and polling thread. It is used to collect auxiliary events while another perf workflow runs, delivering each side-band event to a callback associated with its evsel.

`evlist__add_sb_event()` ensures `sample_id_all` is enabled on the supplied attribute, creates a new evsel at the current evlist index, stores the side-band callback and opaque data in `evsel->side_band`, and appends it to the evlist. `evlist__set_cb()` applies one callback/data pair to all evsels and configures `sample_id_all`, watermark mode, and wakeup watermark for low-latency side-band delivery.

`evlist__start_sb_thread()` prepares and starts collection. It creates maps for the target, configures sample id positions when multiple events exist, opens each evsel on the requested CPUs/threads, mmaps the evlist, enables all counters, clears `evlist->thread.done`, and starts `perf_evlist__poll_thread()` with pthreads. On any setup failure it deletes the evlist and returns `-1`; a null evlist is treated as success/no-op.

The polling thread calls `unshare(CLONE_FS)` first so later namespace transitions with `setns(2)` are not blocked by a shared filesystem context. It then loops until drained: while not draining it polls with a 1000 ms timeout, iterates every mmap, initializes reading, consumes all available events, maps each event back to an evsel through `evlist__event2evsel()`, calls `evsel->side_band.cb(event, data)` when available, logs a warning for unmapped events, consumes the mmap record, and marks data seen. Once `evlist->thread.done` is set, it stops polling and exits after a pass with no remaining data.

`evlist__stop_sb_thread()` sets the done flag, joins the thread, and deletes the evlist. Ownership therefore transfers to the start/stop helpers: failure and normal stop both free the evlist, so callers must not use it afterward.

State is stored in the evlist, evsels, mmap buffers, and `evlist->thread` fields. There is no disk persistence. Runtime side effects include perf_event opens, mmap rings, pthread creation, and `CLONE_FS` unsharing in the polling thread.

Dependencies include perf evlist/evsel/mmap APIs, perf API probing for sample identifier support, Linux perf_event ABI, pthreads, scheduler namespace flags, and debug logging. Integration points include `perf record` or other tools that need side-band data such as namespaces, build IDs, or metadata while primary recording continues.

Risks include deleting the evlist internally on start failure, unsynchronized access to `evlist->thread.done` from another thread, ignoring `unshare(CLONE_FS)` failures, callback execution on the polling thread without isolation from slow or reentrant callbacks, possible missed warning context for unknown events, and ownership surprises because stop always deletes the evlist.

Test signals should include single and multiple side-band events, callback invocation and data pointer preservation, sample-id-all enforcement, startup failure paths for map/open/mmap/enable/thread-create failures, clean draining after setting done, callback behavior under bursts of mmap data, and namespace workloads that require `setns()` after thread creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sideband_evlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/smt.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/smt.c

`smt.c` provides helpers for determining whether simultaneous multithreading is active and whether a recording covers complete physical cores. This is used by perf logic that can make stronger assumptions when all sibling hardware threads for a core are included.

`smt_on()` returns a cached boolean. On first call it tries to read `devices/system/cpu/smt/active` from sysfs; value `1` means SMT is active. If that sysfs file is unavailable, it falls back to `cpu_topology__smt_on(online_topology())`. The result is stored in static `cached_result`, guarded by static `cached`.

`core_wide(bool system_wide, const char *user_requested_cpu_list)` first rejects non-system-wide recordings because partial process/thread recordings cannot be assumed to cover whole cores. If SMT is off, it returns true because each core has only one active hardware thread. If SMT is on, it delegates to `cpu_topology__core_wide(online_topology(), user_requested_cpu_list)` to verify that the requested CPU set includes all siblings for each selected core.

State is limited to the cached SMT result. There is no persistence, but the cache means runtime SMT hotplug or sysfs changes after the first call are not observed.

Dependencies include sysfs helpers from `api/fs/fs.h`, CPU topology helpers from `cputopo.h`, and the public declarations in `smt.h`. Integration points are perf record/report logic that needs to choose core-wide behavior, especially for features sensitive to SMT sibling coverage.

Risks include stale cache after SMT state changes, fallback topology accuracy when sysfs is missing, and interpreting a null or unusual `user_requested_cpu_list` according to `cpu_topology__core_wide()` semantics. The helpers assume `online_topology()` is initialized and valid.

Test signals should cover systems with SMT enabled and disabled, missing sysfs fallback, CPU lists that include all siblings versus partial siblings, non-system-wide recordings, and behavior across repeated calls to confirm caching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/smt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/smt.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/smt.h

`smt.h` declares perf helpers for SMT and core-wide recording checks. It exposes `smt_on()` and `core_wide()` to callers without exposing the sysfs/topology details used by the implementation.

`smt_on()` returns true when SMT, also known as hyperthreading, is enabled. `core_wide(bool system_wide, const char *user_requested_cpu_list)` returns true when the recording is system-wide and the requested CPU set covers all SMT threads for each core, or when SMT is disabled.

The header has no state of its own. State lives in the implementation's cache and in CPU topology/sysfs providers. There is no persistence.

Dependencies are intentionally minimal; the header only needs boolean support from the including context and include guards. Integration points are perf command code that needs a simple predicate before enabling core-wide optimizations or interpreting events as covering full cores.

Risks include callers assuming `core_wide()` only checks CPU lists while it also requires `system_wide`, or assuming `smt_on()` is dynamically refreshed. Compile units including this header must have `bool` available through prior includes or compiler defaults used by the perf tree.

Test signals should validate API use from C files, correct linkage to `smt.c`, and behavior for system-wide/non-system-wide and complete/partial CPU-list cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/smt.h -->
