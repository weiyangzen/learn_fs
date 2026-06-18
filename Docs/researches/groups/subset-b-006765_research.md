# subset-b-006765 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt.c

## Purpose

`intel-pt.c` is perf's Intel Processor Trace auxtrace decoder integration. It accepts recorded Intel PT AUX buffers, configures the packet decoder, walks executable mappings to reconstruct control flow, correlates trace timestamps with perf events, and synthesizes normal perf samples such as branches, instructions, cycles, transactions, PTWRITE, power events, interrupt events, and PEBS-via-PT records.

## Important APIs, Types, and Functions

The main state objects are `struct intel_pt`, which owns session-wide auxtrace state, synthesis options, timestamp conversion, queues, filters, VMCS time-correlation data, synthetic event IDs, and shared callchain/branch-stack buffers; and `struct intel_pt_queue`, which owns per-AUX-queue decoder state, current pid/tid/cpu, guest state, heap timestamp, sample flags, IPC counters, PEBS counter mapping, and buffer references. Public entry is `intel_pt_process_auxtrace_info()`, which parses `PERF_RECORD_AUXTRACE_INFO`, installs `session->auxtrace` callbacks, synthesizes event attrs, and queues AUX data. Other callback roots are `intel_pt_process_event()`, `intel_pt_process_auxtrace_event()`, `intel_pt_queue_data()`, `intel_pt_flush()`, `intel_pt_free_events()`, and `intel_pt_free()`.

Major helpers include `intel_pt_get_trace()` and `intel_pt_lookahead()` for AUX buffer delivery; `intel_pt_walk_next_insn()` for instruction decoding and DSO-backed code walking; `intel_pt_setup_queue()`/`intel_pt_process_queues()` for timestamp-ordered queue scheduling; `intel_pt_run_decoder()` and `intel_pt_sample()` for decoder-state consumption; `intel_pt_synth_*_sample()` for each synthetic sample family; PEBS helpers such as `intel_pt_do_synth_pebs_sample()` and `intel_pt_data_src_fmt()`; and sideband handlers for sched switches, context switches, AUX truncation, AUX output hardware IDs, ITRACE start, and text-poke cache invalidation.

## Control Flow

Initialization allocates `struct intel_pt`, reads auxtrace private fields such as PMU type, TSC conversion, capability bits, snapshot/per-cpu mode, filter string, and optional event-trace capability, then derives decoding mode from evsel config. It registers auxtrace callbacks, validates required sched-switch or context-switch sideband when the recording said it exists, enables logging if requested, builds time ranges, prepares callchain and branch-stack augmentation, synthesizes selected output events, prepares PEBS metadata, and queues AUX data either from pipe/sample mode or the auxtrace index.

During event processing, ordered perf sideband events advance PT decoding to the event timestamp. Timestamped mode keeps all queues in an auxtrace heap and decodes the oldest queue up to the next sideband timestamp. Timeless mode decodes by sample or exit events without heap ordering. Each decoder state is converted into zero or more synthetic samples, then branch states update thread stacks. Sideband events then update current CPU TID, guest vCPU TID, sched-switch synchronization, PEBS hardware-ID mapping, lost-trace errors, or instruction-cache invalidation. Flush drains all queues to `MAX_TIMESTAMP`.

## State and Persistence Behavior

The file persists no trace data itself. Runtime state lives in `struct intel_pt`, auxtrace queues, per-queue decoder instances, DSO auxtrace instruction caches, thread stacks, VMCS time-correlation RB trees, and synthetic event attrs delivered to the session. AUX buffers are lazily loaded from the perf data file and dropped when no longer referenced. Instruction-walk cache entries are stored per DSO and invalidated on `PERF_RECORD_TEXT_POKE`. Timestamp conversion uses recorded `time_shift`, `time_mult`, and `time_zero`; VM time-correlation can apply TSC offsets per VMCS.

## Dependencies and Integration Points

This file integrates perf session ordering, auxtrace queues/heaps, Intel PT decoder libraries, DSO/map/thread machinery, callchain and branch-stack code, perf synthetic event delivery, KVM guest machine tracking, perf time conversion, addr filters, event parsing metadata, and PEBS sample fields. It depends on x86 perf register constants and on sideband events being present when recordings use per-cpu maps or guest tracing.

## Risks and Edge Cases

High-risk areas are timestamp ordering, sideband synchronization, missing or stale mappings, snapshot/sampling overlap repair, guest machine resolution, text-poke invalidation, and PEBS data-source interpretation by CPU model. Pipe mode is explicitly warned as unreliable. `intel_pt_walk_next_insn()` can fail when maps or DSO bytes are missing, and disabled TNT forces quick mode because full code walking is impossible. Time-range filtering and VM time-correlation are mutually constrained. Sample synthesis must preserve sample types and ids exactly or downstream perf report/stat consumers misinterpret output.

## Test Signals

Useful tests include `perf record -e intel_pt//` followed by `perf report/script` branch, instruction, callchain, and last-branch synthesis; snapshot and AUX sample mode runs; truncated AUX records producing auxtrace errors; time-range decoding; text-poke workloads; PTWRITE/power-event/event-trace capable recordings; PEBS-via-PT events on supported E-core systems; guest-sideband traces; and pipe-mode warning coverage. Regression signals are ordered-events requirement failures, missing sched-switch/context-switch validation, memory leak checks around queue/free paths, and decoder error-event delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt.h

## Purpose

`intel-pt.h` is the public perf-util header for Intel Processor Trace. It names the PMU, defines the auxtrace-info private-field indexes shared between recording and decoding, and declares the small API used by recording setup and perf session auxtrace processing.

## Important APIs, Types, and Functions

`INTEL_PT_PMU_NAME` is `"intel_pt"`. The enum indexes fields in `perf_record_auxtrace_info.priv`, including PMU type, time conversion, TSC/MTC capability bits, return-compression bit, sched-switch availability, snapshot and per-cpu mmap mode, CYC capability, max non-turbo ratio, filter-string length, and `INTEL_PT_AUXTRACE_PRIV_MAX`. The declared functions are `intel_pt_recording_init()`, `intel_pt_process_auxtrace_info()`, and `intel_pt_pmu_default_config()`.

## Control Flow

The header has no executable flow. Recording code uses it to initialize Intel PT recording and populate auxtrace metadata. Reporting/inject code calls `intel_pt_process_auxtrace_info()` when it sees an Intel PT AUXTRACE_INFO record, which hands control to `intel-pt.c`.

## State and Persistence Behavior

The enum is a persistent ABI-like contract inside perf data files: producer and consumer must agree on each private-field position. Adding fields requires preserving old positions and checking record size in the decoder.

## Dependencies and Integration Points

It forward-declares perf session, tool, PMU, attr, auxtrace, and perf event types to avoid heavy includes. It integrates `builtin-record`-side Intel PT setup with perf report/script/inject auxtrace decoding.

## Risks and Edge Cases

The main risk is changing enum order or meaning, which breaks old perf.data decoding. Consumers must tolerate absent newer fields by checking record size, as `intel-pt.c` does with `intel_pt_has()`.

## Test Signals

Compatibility tests should record with one perf version and report with another, verify default PMU config generation, and check that old auxtrace-info records lacking newer enum fields still decode or fail gracefully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-tpebs.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/intel-tpebs.c

## Purpose

`intel-tpebs.c` implements perf stat support for Intel TPEBS retirement-latency events. It runs a hidden `perf record` process for the selected latency events, reads sampled `weight3` values from the record stream, summarizes them, and feeds the chosen mean/min/max/last latency back into the evsel count slot used by perf stat metrics.

## Important APIs, Types, and Functions

Global controls are `tpebs_recording` and `tpebs_mode`. `struct tpebs_retire_lat` links each retire-latency evsel to the generated event string, accumulated `struct stats`, last observed value, and started flag. Public functions are `evsel__tpebs_open()`, `evsel__tpebs_read()`, and `evsel__tpebs_close()`. Internal flow uses `evsel__tpebs_prepare()`, `evsel__tpebs_event()`, `evsel__tpebs_start_perf_record()`, `__sample_reader()`, `process_sample_event()`, `tpebs_send_record_cmd()`, and `tpebs_stop()`.

## Control Flow

Opening a retire-latency evsel prepares all matching evsels in the evlist, creates control and ack pipes, starts `perf record -W --synth=no --control=fd:... -o -` with generated `name=tpebs_event_<evsel>` event aliases, starts a reader thread, and enables recording through the control channel. The reader creates a read-mode perf session over the child stdout and updates per-event stats for samples that belong to the measured workload or inherited children. Reads ping the record process before the first result, select a latency value according to `tpebs_mode`, and write it into the first CPU/thread count cell. Close removes the event and stops the child/reader when the last TPEBS event is gone.

## State and Persistence Behavior

State is process-local and protected by a lazily initialized mutex: the global results list, child process descriptor, pipe file descriptors, and reader thread. No data is persisted to disk because the child writes perf data to stdout. Counts are synthetic and accumulate into `evsel->counts` and optionally `prev_raw_counts`.

## Dependencies and Integration Points

It depends on perf run-command control protocol tags, perf session reading, evlist/evsel metadata, workload pid/inherit state, procfs parent traversal, `struct stats`, CPU map formatting, mutex annotations, and perf stat count storage. It integrates with `evsel__open/read/close` paths for retire-latency events.

## Risks and Edge Cases

The code is concurrency-sensitive: `tpebs_send_record_cmd()` temporarily drops the mutex to avoid starving the reader. Ack timeouts, early child exit, pipe setup failure, thread creation failure, and evlist purge races are handled but remain high-risk. The event-string conversion assumes an `R` modifier and slash/colon layout in `evsel->name`. Child-process filtering through `/proc/<pid>/status` can race with process exit. If no samples arrive, the code falls back to precomputed latency values and warns once.

## Test Signals

Tests should cover multiple retire-latency evsels, CPU list propagation, workload pid filtering with and without inherit, child exit before ack, no-sample fallback for all modes, evlist purge/close races, and first-cell-only count updates. Integration smoke tests should verify that perf stat metrics change when TPEBS samples are available and that hidden `perf record` exits cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-tpebs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-tpebs.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/intel-tpebs.h

## Purpose

`intel-tpebs.h` declares the small interface that lets evsel/perf-stat code use TPEBS retirement-latency sampling when enabled.

## Important APIs, Types, and Functions

`enum tpebs_mode` selects aggregation: mean, min, max, or last. `tpebs_recording` enables the feature and `tpebs_mode` selects the read behavior. The API consists of `evsel__tpebs_open()`, `evsel__tpebs_close()`, and `evsel__tpebs_read()`.

## Control Flow

Callers open TPEBS around retire-latency evsel open, read a synthesized latency count from the first CPU/thread slot during stat reads, and close when the evsel is closed. The implementation in `intel-tpebs.c` owns the child process and reader thread.

## State and Persistence Behavior

The header exposes process-global mode state but no persistent storage. The underlying implementation stores sampled stats in memory only.

## Dependencies and Integration Points

It forward-declares `struct evlist` and `struct evsel` and is included by evsel/stat paths that need optional TPEBS hooks.

## Risks and Edge Cases

Callers must gate by `tpebs_recording` and use only retire-latency evsels. The enum order is used by command-line parsing and should remain stable.

## Test Signals

Compile tests should ensure non-TPEBS builds still see declarations. Runtime tests should check every `tpebs_mode` and open/read/close symmetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-tpebs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intlist.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/intlist.c

## Purpose

`intlist.c` implements a sorted set/list of unsigned long integers on top of perf's generic red-black-tree `rblist` helper.

## Important APIs, Types, and Functions

The file implements `intlist__new()`, `intlist__delete()`, `intlist__add()`, `intlist__remove()`, `intlist__find()`, `intlist__findnew()`, and `intlist__entry()`. Internal callbacks `intlist__node_new()`, `intlist__node_delete()`, and `intlist__node_cmp()` adapt `struct int_node` to `rblist`.

## Control Flow

Construction initializes `rblist` callbacks and optionally parses a comma-separated decimal list. Adding and lookup pass the integer value cast through `void *` into rblist. Parsing loops over `strtol()`, requiring each token to end in comma or NUL, and aborts by deleting the list on malformed input or allocation failure.

## State and Persistence Behavior

State is entirely heap-resident in `struct intlist`; each `struct int_node` stores the key and a caller-owned `priv` pointer. There is no serialization.

## Dependencies and Integration Points

It depends on `rblist`, Linux rb-tree helpers, `container_of`, and errno values. Users include filters and KVM/stat helpers needing ordered integer sets.

## Risks and Edge Cases

The integer is cast through `void *`, which is conventional in this codebase but depends on pointer width being able to carry `unsigned long`. `strtol()` permits leading whitespace and signs but the destination is unsigned long; negative inputs can wrap. Duplicate behavior is inherited from `rblist__add_node()`. Empty or trailing-comma strings should be validated by callers/tests.

## Test Signals

Unit tests should cover sorted insertion, duplicate insertion behavior, lookup without creation, findnew creation, removal during safe iteration, parsing valid comma lists, invalid separators, empty input, and negative or overflow-like values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intlist.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/intlist.h

## Purpose

`intlist.h` declares the integer rblist wrapper and iteration helpers used by perf utility code.

## Important APIs, Types, and Functions

`struct int_node` embeds an rb node, an unsigned long key `i`, and a `priv` pointer. `struct intlist` wraps `struct rblist`. The header declares create/delete/add/remove/find/findnew/entry functions and inline helpers for membership, emptiness, count, first/next, and safe/unsafe iteration macros.

## Control Flow

Inline iteration starts at `rb_first_cached()` and follows `rb_next()`. The safe macro stores the next pointer before each loop body so callers may remove the current node.

## State and Persistence Behavior

The header defines in-memory tree layout only. `priv` lifetime is not managed by intlist.

## Dependencies and Integration Points

It includes Linux rb-tree and perf `rblist.h`, and is consumed by filters such as pid lists in KVM/stat code.

## Risks and Edge Cases

`intlist__for_each_entry_safe` initializes `n` from `intlist__next(pos)` even when `pos` is NULL; the inline next handles NULL, so this is safe but worth preserving. Callers must not free `priv` implicitly through `intlist__delete()`.

## Test Signals

Compile tests should cover macro use in empty and non-empty lists. Runtime tests should remove nodes during safe iteration and confirm sorted traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/iostat.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/iostat.c

## Purpose

`iostat.c` provides weak default implementations for perf iostat hooks on platforms that do not supply architecture-specific support.

## Important APIs, Types, and Functions

It defines global `enum iostat_mode_t iostat_mode = IOSTAT_NONE` and weak functions `iostat_prepare()`, `iostat_parse()`, `iostat_list()`, `iostat_release()`, `iostat_print_header_prefix()`, `iostat_print_metric()`, `iostat_prefix()`, and `iostat_print_counters()`.

## Control Flow

Unsupported builds return `-1` from prepare/parse and otherwise no-op. `iostat_parse()` prints a clear unsupported-platform error.

## State and Persistence Behavior

Only `iostat_mode` is mutable global state. No runtime allocations or persistent data are managed by this fallback file.

## Dependencies and Integration Points

It integrates with perf stat iostat command-line and output paths. Architecture/platform files can override the weak symbols with real implementations.

## Risks and Edge Cases

Weak-symbol behavior depends on linker support and build configuration. Callers must handle `-1` from prepare/parse and should not assume print hooks did anything on unsupported platforms.

## Test Signals

Build tests should verify unsupported platforms link and print the unsupported message. Supported-platform builds should verify strong symbols override these weak defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/iostat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/iostat.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/iostat.h

## Purpose

`iostat.h` declares the perf stat iostat mode interface and the hooks used by generic stat code and platform-specific implementations.

## Important APIs, Types, and Functions

`enum iostat_mode_t` has `IOSTAT_NONE`, `IOSTAT_RUN`, and `IOSTAT_LIST`. `iostat_print_counter_t` is a callback for printing an evsel count. The header declares prepare, parse, list, release, prefix, header, metric, and counter-print functions plus global `iostat_mode`.

## Control Flow

Generic command-line parsing calls `iostat_parse()`, setup calls `iostat_prepare()`, and output paths use prefix/header/metric/counter hooks. Release cleans platform-specific state.

## State and Persistence Behavior

The header exposes the global mode and opaque platform state through `evlist`/`perf_stat_config`; it does not define persistence.

## Dependencies and Integration Points

It includes parse-options, stat, parse-events, and evlist headers, tying iostat to perf stat event selection and output formatting.

## Risks and Edge Cases

The public callback signatures must stay aligned with generic stat code. Platform implementations must tolerate null or unsupported evlists and release partially prepared state.

## Test Signals

Command-line tests should cover `--iostat=list`, iostat run mode, unsupported-platform fallback, and output prefix/metric formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/iostat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/jit.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/jit.h

## Purpose

`jit.h` declares perf inject helpers for JIT dump processing.

## Important APIs, Types, and Functions

`jit_process()` processes one mmap filename that may be a jitdump marker, injects generated JIT ELF mmap records into an output perf data stream, and returns bytes written. `jit_inject_record()` is declared for record-side injection by filename.

## Control Flow

Perf inject/report paths call `jit_process()` when mmap records are seen. The implementation in `jitdump.c` detects `jit-<pid>.dump`, reads records, writes ELF files, emits mmap2 events, and may suppress anonymous JIT code mmaps after a pid is processed.

## State and Persistence Behavior

The interface writes derived ELF files and perf data records through implementation code. It has no state in the header.

## Dependencies and Integration Points

It includes `data.h` and uses perf session, perf data, machine, pid/tid, and byte-count types.

## Risks and Edge Cases

Callers must pass the correct namespace-aware filename and pid/tid from mmap records. Return codes distinguish no-op, processed, and error behavior and must be handled carefully by perf inject.

## Test Signals

Tests should feed jitdump mmap records and verify generated ELF files, mmap2 injection, byte counts, and anonymous-map suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/jit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/jitdump.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/jitdump.c

## Purpose

`jitdump.c` converts JIT runtime dump files into ELF images and injected perf mmap2 events so perf can symbolize JIT-generated code.

## Important APIs, Types, and Functions

`struct jit_buf_desc` carries input/output perf data, session/machine, namespace info, jitdump buffers, debug/unwind side data, output directory, byte count, and timestamp mode. Public `jit_process()` is the main entry. Important internal functions are `jit_open()`, `jit_get_next_entry()`, `jit_process_dump()`, `jit_repipe_code_load()`, `jit_repipe_code_move()`, `jit_repipe_debug_info()`, `jit_repipe_unwinding_info()`, `jit_emit_elf()`, `jit_detect()`, `convert_timestamp()`, `jit_add_pid()`, and `jit_has_pid()`.

## Control Flow

`jit_process()` finds or creates the thread for the mmap, obtains namespace info, detects `.../jit-<pid>.dump`, and if matched initializes a descriptor and calls `jit_inject()`. Opening validates header magic, byte order, version, flags, timestamp mode, and clock requirements. The dump loop reads each record prefix and payload, byte-swaps if needed, and dispatches load/move/debug/unwind records. Code-load records write a `jitted-<pid>-<index>.so` ELF with optional debug/unwind data, synthesize a `PERF_RECORD_MMAP2`, process it into the machine, write it to output, and mark the generated DSO hit. Code-move records synthesize updated mmap2 records for moved code.

## State and Persistence Behavior

The code creates persistent generated ELF files beside the jitdump file and injects persistent mmap2 records into the output perf data stream. It also marks processed pids in thread private data so later anonymous or memfd JIT code maps can be stripped. Debug and unwind side data are buffered until consumed by the next code-load record.

## Dependencies and Integration Points

It depends on jitdump format definitions, `genelf` writing, perf data output, perf event processing, build-id marking, namespace mount handling, DSO/machine/thread state, time conversion, and mmap2 sample-id layout. It integrates primarily with `perf inject --jit`.

## Risks and Edge Cases

Header validation, cross-endianness, namespace pid translation, arch timestamp conversion, path sizing, and record size validation are sensitive. `jit_open()` contains a subtle read-extra path where buffer-size bookkeeping must remain correct. Generated mmap event sizing depends on aligned filename length and `machine->id_hdr_size`. Clockid validation rejects non-arch timestamps unless events used `CLOCK_MONOTONIC`. Debug/unwind records must precede the code load they describe.

## Test Signals

Tests should include native and byte-swapped jitdump files, arch and monotonic timestamp modes, invalid flags/version, namespace pid cases, code load with debug/unwind info, code move, unknown records, generated ELF symbolization, build-id generation, and anonymous-map suppression after a processed pid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/jitdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/jitdump.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/jitdump.h

## Purpose

`jitdump.h` defines the on-disk jitdump file format structures and constants used by JIT runtimes and perf's jitdump reader.

## Important APIs, Types, and Functions

It defines magic values, version, alignment macros, timestamp flag bits, `struct jitheader`, `enum jit_record_type`, record prefix `struct jr_prefix`, record payloads for code load, close, move, debug info, and unwinding info, `union jr_entry`, and inline helpers `debug_entry_next()` and `debug_entry_file()`.

## Control Flow

There is no runtime flow beyond inline pointer arithmetic for variable-length debug entries. `jitdump.c` reads a header, then repeatedly reads a `jr_prefix` followed by `total_size` bytes and interprets the union by record id.

## State and Persistence Behavior

These structures are the persistent ABI of jitdump files. Header flags indicate whether record timestamps are perf-clock values or architecture timestamps requiring conversion.

## Dependencies and Integration Points

The header depends on fixed-width integer types, time headers, and string length for inline helpers. It integrates JIT runtimes that emit dumps with perf inject/report tooling.

## Risks and Edge Cases

The ABI is packed only by C layout convention; producers and consumers must agree on sizes and alignment. Variable-length strings and debug entries require careful `total_size` validation by readers. Reserved flags must be rejected to avoid misinterpreting future formats.

## Test Signals

Format tests should validate magic, swapped magic, version, reserved flags, 8-byte alignment, debug-entry iteration, and each record type's serialized size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/jitdump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/arm64_exception_types.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/arm64_exception_types.h

## Purpose

`arm64_exception_types.h` provides ARM64 KVM exception and ESR exception-class constants plus macro tables that map numeric exit values to display names for `perf kvm stat`.

## Important APIs, Types, and Functions

The file defines `ARM_EXCEPTION_*` values, `HVC_STUB_ERR`, the `kvm_arm_exception_type` table macro, ESR exception-class constants `ESR_ELx_EC_*`, `ECN(x)`, and `kvm_arm_exception_class`.

## Control Flow

There is no executable control flow. `kvm-stat-arm64.c` expands these macros into `exit_reasons_table` arrays and selects the basic exception table or ESR class table depending on whether the exit reason is `ARM_EXCEPTION_TRAP`.

## State and Persistence Behavior

The mappings are static source metadata. They must track kernel UAPI/asm values so recorded tracepoint fields decode correctly.

## Dependencies and Integration Points

The constants mirror Linux ARM64 `asm/virt.h`, `asm/kvm_asm.h`, and `asm/esr.h` values and integrate with common `exit_event_decode_key()`.

## Risks and Edge Cases

Stale constants cause misleading VM-exit names. The class table intentionally omits some unallocated or newer EC values, so unknown values decode as `UNKNOWN`.

## Test Signals

Tests should feed ARM64 `kvm_exit` samples for IRQ, SERROR, TRAP with ESR EC, illegal exception, and unknown EC values and verify decoded names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/arm64_exception_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/book3s_hcalls.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/book3s_hcalls.h

## Purpose

`book3s_hcalls.h` is the PowerPC Book3S HV hypercall code-to-name mapping for `perf kvm stat hcall`.

## Important APIs, Types, and Functions

The single `kvm_trace_symbol_hcall` macro expands many `{code, "H_*"}` entries such as `H_REMOVE`, `H_ENTER`, `H_CEDE`, `H_REGISTER_VPA`, `H_GET_PERF_COUNT`, `H_RANDOM`, and `H_RTAS`.

## Control Flow

There is no local flow. `kvm-stat-powerpc.c` expands the macro into an `exit_reasons_table` and uses it when hcall enter events provide a `req` code.

## State and Persistence Behavior

The table is static decode metadata aligned with PowerPC hypervisor ABI codes. It stores no runtime data.

## Dependencies and Integration Points

It integrates with `kvm_hv:kvm_hcall_enter`/`kvm_hcall_exit` tracepoints and `hcall_event_decode_key()`.

## Risks and Edge Cases

Unknown or newly added hypercalls decode as `UNKNOWN`. Incorrect codes would corrupt reports without causing runtime failures.

## Test Signals

Sample-driven tests should cover common HCALLs and an unknown code, ensuring the hcall report key displays the expected name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/book3s_hcalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/book3s_hv_exits.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/book3s_hv_exits.h

## Purpose

`book3s_hv_exits.h` maps PowerPC Book3S HV interrupt/vector exit codes to display names for KVM VM-exit reports.

## Important APIs, Types, and Functions

The `kvm_trace_symbol_exit` macro lists vector codes such as `RETURN_TO_HOST`, `SYSTEM_RESET`, `MACHINE_CHECK`, storage and segment exceptions, `EXTERNAL`, `DECREMENTER`, hypervisor storage exits, `PERFMON`, `ALTIVEC`, and `VSX`.

## Control Flow

No executable flow exists. PowerPC KVM stat expands the macro into `hv_exit_reasons` and uses common exit-event begin/end logic.

## State and Persistence Behavior

The file is static decode metadata tied to PowerPC exception-vector values.

## Dependencies and Integration Points

It integrates with `kvm_hv:kvm_guest_exit` tracepoint `trap` fields and common KVM stat decoding.

## Risks and Edge Cases

Stale or missing vector codes lead to `UNKNOWN` or wrong display names. Values are architecture-specific and should not be reused for non-Book3S KVM.

## Test Signals

Tests should decode representative trap values, especially external/decrementer/storage exits and unknown values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/book3s_hv_exits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-arm64.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-arm64.c

## Purpose

`kvm-stat-arm64.c` provides ARM64-specific tracepoint names, exit-key extraction, and registration tables for `perf kvm stat`.

## Important APIs, Types, and Functions

It defines `arm64_exit_reasons` and `arm64_trap_exit_reasons`, event tracepoints `kvm:kvm_entry` and `kvm:kvm_exit`, `event_get_key()`, begin/end predicates, `exit_events`, `__kvm_reg_events_ops`, skip-event list, and exported functions `__cpu_isa_init_arm64()`, `__kvm_events_tp_arm64()`, `__kvm_reg_events_ops_arm64()`, and `__kvm_skip_events_arm64()`.

## Control Flow

Begin events match ARM64 KVM entry. End events match ARM64 KVM exit and call `event_get_key()`. Basic exits decode the `ret` trace field against exception types; TRAP exits switch to the `esr_ec` trace field and ESR exception-class table.

## State and Persistence Behavior

The module stores static tables only. Runtime state is written into `struct event_key` and `perf_kvm_stat.exit_reasons_isa`.

## Dependencies and Integration Points

It depends on common KVM stat APIs, `evsel__intval()`, ARM64 exception macros, and `EM_AARCH64` dispatch from `kvm-stat.c`.

## Risks and Edge Cases

Tracepoint field names must match kernel tracing. TRAP handling depends on `esr_ec` being present. Unknown exception classes fall through common decode as `UNKNOWN`.

## Test Signals

Tracepoint sample tests should cover entry/exit pairing, IRQ/SERROR exits, TRAP ESR decoding, and missing/unknown field behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-arm64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-loongarch.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-loongarch.c

## Purpose

`kvm-stat-loongarch.c` implements LoongArch KVM stat exit decoding, including special handling for guest privileged instruction traps.

## Important APIs, Types, and Functions

It defines LoongArch exception constants and `loongarch_exit_reasons`, tracepoints `kvm_enter`, `kvm_reenter`, `kvm_exit`, and `kvm_exit_gspr`, begin/end predicates, `event_gspr_get_key()`, child event table for `kvm_exit_gspr`, and exported arch hooks for ISA initialization, tracepoints, registered events, and skip events.

## Control Flow

Begin uses common `exit_event_begin()` on `kvm_exit`. End is either `kvm_enter` or `kvm_reenter`, reflecting LoongArch's adjacent reentry/entry behavior after exits. The child `kvm_exit_gspr` event decodes the trapped instruction word to classify CPUCFG, CSR, IOCSR, IDLE, or other privileged traps.

## State and Persistence Behavior

Static tables define names. `__cpu_isa_init_loongarch()` sets `exit_reasons_isa` to `loongarch64` and assigns the exit-reason table into the runtime KVM stat object.

## Dependencies and Integration Points

It depends on common KVM stat, tracepoint parsing, PMU headers, evsel field reads, and `EM_LOONGARCH` dispatch.

## Risks and Edge Cases

Instruction decoding in `event_gspr_get_key()` is pattern-based and must match kernel trace semantics. Begin/end pairing differs from other architectures, so regressions can invert measured durations. Unknown privileged traps collapse to `Others`.

## Test Signals

Tests should cover `kvm_reenter` and `kvm_enter` as end events, ordinary exit reasons, GSPR instruction classification for CPUCFG/CSR/IOCSR/IDLE, and unknown instruction fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-loongarch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-powerpc.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-powerpc.c

## Purpose

`kvm-stat-powerpc.c` provides PowerPC Book3S HV KVM stat support for VM exits and hypercalls, plus a default guest-profiling event choice.

## Important APIs, Types, and Functions

It defines `hv_exit_reasons`, `hcall_reasons`, Book3S HV tracepoint list, hcall key/decode functions, `hcall_events`, `exit_events`, registered event ops for `vmexit` and `hcall`, `is_tracepoint_available()`, `ppc__setup_book3s_hv()`, `ppc__setup_kvm_tp()`, `__setup_kvm_events_tp_powerpc()`, `__cpu_isa_init_powerpc()`, and `__kvm_add_default_arch_event_powerpc()`.

## Control Flow

Setup creates a temporary evlist and verifies all Book3S HV tracepoints can be parsed. On success it publishes them in `__kvm_events_tp`, sets HV exit reasons, and labels the ISA `HV`. VM-exit events use common begin/end logic. HCALL events begin on `kvm_hcall_enter`, read the `req` field, and end on `kvm_hcall_exit`. Default event augmentation adds `trace_imc/trace_cycles/` when the user did not specify `-e` and the PMU event is available.

## State and Persistence Behavior

The module has a static mutable tracepoint pointer array populated at setup. Runtime KVM state receives exit-reason table and ISA label. Default event injection duplicates strings into argv.

## Dependencies and Integration Points

It depends on Book3S HV tracepoints, parse-events, PMU event discovery, parse-options, common KVM stat, and PowerPC hcall/exit mapping headers.

## Risks and Edge Cases

Only Book3S HV is supported; missing tracepoints cause setup failure. The temporary evlist allocated in setup is not visibly deleted in this file, so leak checks should inspect caller/build behavior. Default event injection returns `-EINVAL` if `trace_imc/trace_cycles` is unavailable. HCALL unknown codes log debug and decode as `UNKNOWN`.

## Test Signals

Tests should cover tracepoint availability success/failure, VM-exit and hcall reports, default event insertion with and without user `-e`, unavailable trace_imc fallback, and unknown hcall codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-powerpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-riscv.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-riscv.c

## Purpose

`kvm-stat-riscv.c` supplies RISC-V KVM stat tracepoint and trap-cause decoding.

## Important APIs, Types, and Functions

It defines `riscv_exit_reasons`, tracepoints `kvm:kvm_entry` and `kvm:kvm_exit`, `event_get_key()`, begin/end predicates, `exit_events`, registration ops, skip events, and exported RISC-V hook functions.

## Control Flow

Begin matches RISC-V KVM entry. End matches RISC-V KVM exit, reads the `scause` field, masks off the interrupt high bit with `CAUSE_IRQ_FLAG(64)`, and decodes the remaining cause through the RISC-V trap table.

## State and Persistence Behavior

Static tables are immutable. Runtime state is limited to event keys and `exit_reasons_isa = "riscv64"`.

## Dependencies and Integration Points

It depends on common KVM stat, evsel field extraction, `riscv_trap_types.h`, and `EM_RISCV` dispatch.

## Risks and Edge Cases

The code currently hardcodes `xlen = 64` with a TODO for 32-bit support. Masking interrupt causes means interrupt and exception numeric namespaces share the same decode table after removing the high bit. Kernel tracepoint field-name changes would break decoding.

## Test Signals

Tests should cover exception and interrupt `scause` values, high-bit masking, unknown traps, and future 32-bit RISC-V behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-riscv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-s390.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-s390.c

## Purpose

`kvm-stat-s390.c` implements IBM s390 SIE KVM stat decoding, including child tracepoints that refine intercept reasons.

## Important APIs, Types, and Functions

It expands SIE tables from `asm/sie.h`, defines child key extractors for intercepted instruction, SIGP, diagnose, and program-intercept events, lists tracepoints from SIE enter/exit through child handlers, registers `vmexit` ops, skips `"Wait state"`, and exports s390 hook functions.

## Control Flow

Common exit begin/end handles SIE enter/exit. Child events override the key table and key value: instruction intercept decodes the instruction word through `icpt_insn_decoder()`, SIGP reads `order_code`, diagnose reads `code`, and program intercept reads `code`.

## State and Persistence Behavior

Static decode tables come from kernel UAPI. `__cpu_isa_init_s390()` enables support only when `cpuid` contains `"IBM"`, then sets SIE table and ISA label.

## Dependencies and Integration Points

It depends on common KVM stat, evsel field extraction, and s390 SIE UAPI macros. It is selected by `EM_S390`.

## Risks and Edge Cases

Non-IBM cpuid returns `-ENOTSUP`. Child event field names must match tracepoints. Wait-state skip affects report visibility and should stay aligned with user expectations.

## Test Signals

Tests should cover IBM and non-IBM cpuid, SIE intercept decoding, all child event tables, wait-state skipping, and unknown intercept codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-s390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-x86.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-x86.c

## Purpose

`kvm-stat-x86.c` provides x86 KVM stat support for VM exits, MMIO, PIO, and MSR emulation timing, plus Intel-specific default event selection.

## Important APIs, Types, and Functions

It defines VMX and SVM exit-reason tables, common `exit_events`, `mmio_events`, `ioport_events`, `msr_events`, tracepoints `kvm_entry`, `kvm_exit`, `kvm_mmio`, `kvm_pio`, and `kvm_msr`, registered event ops for `vmexit`, `mmio`, `ioport`, and `msr`, skip event `"HLT"`, `__cpu_isa_init_x86()`, `__kvm_add_default_arch_event_x86()`, and exported table accessors.

## Control Flow

VM-exit duration uses common `kvm_exit` to `kvm_entry` pairing. MMIO write duration runs from `kvm_mmio` write to entry; MMIO read duration runs from exit to `kvm_mmio` read. PIO and MSR durations run from their tracepoint to entry. Decode functions format GPA plus R/W, port plus PIN/POUT, or MSR ECX plus R/W. ISA init chooses VMX for Intel and SVM for AMD/Hygon. Intel default-event logic adds `-e cycles` when the user did not provide an event or `--pfm-events`.

## State and Persistence Behavior

Static tables define supported events. Runtime state is in event keys and KVM stat ISA fields. Default event injection mutates argv by adding duplicated strings.

## Dependencies and Integration Points

It depends on x86 UAPI VMX/SVM/KVM exit macros, common KVM stat, x86 CPU detection, parse-options, and evsel field extraction.

## Risks and Edge Cases

MMIO read/write pairing is asymmetric and easy to regress. Intel default event selection avoids PEBS guest-sampling failure by not using `cycles:P`; tests should preserve that behavior. Unsupported vendor strings return `-ENOTSUP`. Tracepoint field-name changes break key extraction.

## Test Signals

Tests should cover Intel/AMD/Hygon vendor init, unknown vendors, vmexit decode, MMIO read and write pairing, PIO/MSR decode, HLT skipping, and default `cycles` insertion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-x86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/riscv_trap_types.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/riscv_trap_types.h

## Purpose

`riscv_trap_types.h` defines RISC-V interrupt and exception cause constants and a macro table for KVM stat trap decoding.

## Important APIs, Types, and Functions

It defines `CAUSE_IRQ_FLAG(xlen)`, interrupt cause constants such as supervisor/VS/machine software, timer, external, guest external, and PMU overflow, exception causes such as illegal instruction, breakpoints, load/store/inst access and page faults, hypervisor/supervisor syscalls, guest page faults, and virtual instruction fault, plus `TRAP(x)` and `kvm_riscv_trap_class`.

## Control Flow

No executable flow exists. RISC-V KVM stat masks the interrupt flag from `scause` and decodes the remaining value with the macro-expanded table.

## State and Persistence Behavior

The file is static architecture decode metadata aligned with RISC-V cause numbers.

## Dependencies and Integration Points

It uses `_AC` from kernel-style constant macros and integrates with `kvm-stat-riscv.c`.

## Risks and Edge Cases

Interrupt and exception causes can share low numeric values after masking; the combined table must be interpreted in context. New RISC-V causes require updates. Current consumer assumes 64-bit xlen.

## Test Signals

Tests should validate interrupt-flag masking, each guest page fault cause, virtual instruction fault, PMU overflow, and unknown cause fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/riscv_trap_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat.c

## Purpose

`kvm-stat.c` is the common architecture-dispatch and default event helper layer for `perf kvm stat`.

## Important APIs, Types, and Functions

It implements common helpers `kvm_exit_event()`, `kvm_entry_event()`, `exit_event_get_key()`, `exit_event_begin()`, `exit_event_end()`, and `exit_event_decode_key()`. Dispatch functions include `setup_kvm_events_tp()`, `cpu_isa_init()`, `vcpu_id_str()`, `kvm_exit_reason()`, `kvm_entry_trace()`, `kvm_exit_trace()`, `kvm_events_tp()`, `kvm_reg_events_ops()`, `kvm_skip_events()`, and `kvm_add_default_arch_event()`.

## Control Flow

Common begin/end logic reads the evsel ELF machine, compares evsel names against architecture-specific entry/exit tracepoint names, and fills an `event_key` with the architecture-specific exit reason field. Dispatch switches on `e_machine` to call ARM64, LoongArch, PowerPC, RISC-V, s390, or x86 providers. Unsupported machines print errors and return failure/null.

## State and Persistence Behavior

No persistent state is owned here. It reads architecture tables and mutates `perf_kvm_stat` during ISA init and setup.

## Dependencies and Integration Points

It depends on evsel machine detection, tracepoint field extraction, common debug logging, and arch providers declared in `kvm-stat.h`. It is the central integration point between generic KVM stat code and per-architecture modules.

## Risks and Edge Cases

Unsupported `e_machine` values must fail clearly. `exit_event_decode_key()` assumes `key->exit_reasons` is set; architectures that rely on `kvm->exit_reasons` must ensure keys point to a valid table before decoding. Field-name dispatch must match kernel tracepoint definitions.

## Test Signals

Tests should exercise every architecture dispatch branch, unsupported machine handling, vCPU field-name selection, entry/exit trace names, skip-event tables, and default event injection for x86/PowerPC only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat.h

## Purpose

`kvm-stat.h` defines the shared types, callbacks, and arch hook declarations used by `perf kvm stat`.

## Important APIs, Types, and Functions

Key structures are `event_key`, `kvm_info`, `kvm_event_stats`, `kvm_event`, `child_event_ops`, `kvm_events_ops`, `exit_reasons_table`, `perf_kvm_stat`, and `kvm_reg_events_ops`. It declares common exit helpers, all per-architecture setup/ISA/table functions, tracepoint accessors, skip-event accessors, and default-event hooks under `HAVE_LIBTRACEEVENT`. It also provides refcounted `kvm_info` inline helpers and `STRDUP_FAIL_EXIT`.

## Control Flow

Generic KVM stat code uses `kvm_events_ops` callbacks to identify begin/end events, optional child events, and key decoding. Architecture code fills registered event ops and exit-reason tables. Refcount helpers increment/decrement/free `kvm_info` instances.

## State and Persistence Behavior

The header defines runtime aggregation state: per-event total and per-vCPU stats, histogram entry, total time/count/lost/duration counters, pid filters, display options, and live/report mode flags. State is in memory for one perf kvm stat run.

## Dependencies and Integration Points

It includes perf tool, sort, stat, symbol, record, errno, zalloc, and refcount support. It is shared by generic command code and all `kvm-stat-arch` modules.

## Risks and Edge Cases

Callback contracts must remain synchronized across all architectures. `STRDUP_FAIL_EXIT` assumes a local `ret` variable and `EXIT` label. Refcounting requires callers to use `kvm_info__zput()` to avoid leaks and dangling pointers.

## Test Signals

Compile tests should cover builds with and without `HAVE_LIBTRACEEVENT`. Runtime tests should cover event registration, child event decoding, refcount lifetime, per-vCPU resizing, pid-list filtering, and default-event argument mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kwork.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/kwork.h

## Purpose

`kwork.h` defines the data model and BPF hook interface for perf's kernel work analysis commands, covering IRQs, softirqs, workqueues, and scheduler work.

## Important APIs, Types, and Functions

It defines class/report/trace enums, `struct kwork_atom`, `kwork_atom_page`, `kwork_work`, `kwork_class`, `trace_kwork_handler`, `kwork_top_stat`, and `perf_kwork`. It declares BPF-backed prepare/read/start/finish/cleanup functions when `HAVE_BPF_SKEL` is set and inline failure/no-op stubs otherwise.

## Control Flow

Trace handlers classify raise/entry/exit/sched-switch events into classes and works. Work objects own atom lists by trace type and derived runtime, latency, and top statistics. `perf_kwork` holds global filters, options, class lists, atom page pool, sorted work roots, and callback to add/find work.

## State and Persistence Behavior

State is in-memory for a run. Atom pages pool fixed arrays of 128 atoms with a bitmap allocator. Works accumulate max/total runtime and latency, CPU usage, TGID, and kthread flags. Filters include CPU bitmap and time interval.

## Dependencies and Integration Points

It depends on perf tool/session/sample types, time utilities, Linux bitmaps/lists/rbtree/types, and optional BPF skeleton support. It integrates command-line options, tracepoint handlers, BPF collection, and report/top rendering code elsewhere.

## Risks and Edge Cases

The nested class/work/atom model requires consistent lifetime management and atom pairing. Missing BPF support returns `-1` from prepare/read and no-ops lifecycle hooks, so callers need fallback behavior. Fixed `MAX_NR_CPUS` bitmaps and atom-page pooling need bounds checks.

## Test Signals

Tests should cover tracepoint and BPF paths, IRQ/softirq/workqueue/sched classes, runtime/latency/top reports, CPU and time filters, atom allocation exhaustion/reuse, lost-event accounting, and no-BPF fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kwork.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/levenshtein.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/levenshtein.c

## Purpose

`levenshtein.c` implements weighted Damerau-Levenshtein string distance for perf suggestion and fuzzy matching code.

## Important APIs, Types, and Functions

The sole API is `levenshtein(const char *string1, const char *string2, int w, int s, int a, int d)`, where weights are swap, substitution, insertion/addition, and deletion penalties.

## Control Flow

The function allocates three rows sized to `strlen(string2) + 1`, initializes insertion costs, then iterates over characters of `string1` and `string2`. For each cell it computes minimum cost among substitution, adjacent swap, deletion, and insertion. Rows rotate after each source character, and the result is the last row's final column.

## State and Persistence Behavior

All state is temporary heap memory. No persistent data is written.

## Dependencies and Integration Points

It depends on libc allocation/string functions and is declared by `levenshtein.h`. It is suitable for command/event-name suggestions.

## Risks and Edge Cases

The code does not check malloc failures before writing rows, so OOM can crash. The algorithm note says it calculates a true distance only when deletion and insertion weights are equal. Lengths are stored in `int`, so extremely long strings can overflow. It treats bytes, not Unicode characters.

## Test Signals

Tests should cover equal strings, insertion/deletion/substitution/swap, weighted penalties, empty strings, asymmetric add/delete penalties, long strings, and injected allocation-failure behavior if possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/levenshtein.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/levenshtein.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/levenshtein.h

## Purpose

`levenshtein.h` declares perf's weighted Damerau-Levenshtein distance helper.

## Important APIs, Types, and Functions

It declares `levenshtein()` with parameters for the two strings and swap, substitution, insertion, and deletion penalties. The parameter name `substition_penalty` contains a spelling mistake but is ABI-neutral in C declarations.

## Control Flow

The header has no control flow; callers invoke the implementation in `levenshtein.c`.

## State and Persistence Behavior

No state is defined.

## Dependencies and Integration Points

The header has only include guards and can be used by suggestion/fuzzy-match utilities.

## Risks and Edge Cases

Callers must pass valid NUL-terminated strings and nonnegative weights. The spelling typo should not be changed casually if external references depend on the name in documentation.

## Test Signals

Compile tests should include the header from C files, and functional tests should validate the implementation's distance values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/levenshtein.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libbfd.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/libbfd.c

## Purpose

`libbfd.c` implements perf's optional libbfd-backed source-line lookup, symbol loading for non-ELF objects, build-id/debuglink reading, and BPF disassembly support.

## Important APIs, Types, and Functions

`struct a2l_data` caches a BFD object, symbol table, lookup address, and found file/function/line. Important functions are `ensure_bfd_init()`, `addr2line_init()`, `slurp_symtab()`, `find_address_in_section()`, `libbfd__addr2line()`, `dso__free_a2l_libbfd()`, `dso__load_bfd_symbols()`, `libbfd__read_build_id()`, `libbfd_filename__read_debuglink()`, and `symbol__disassemble_bpf_libbfd()`.

## Control Flow

Initialization uses `pthread_once()` and installs recursive mutex callbacks for libbfd threading. Addr2line opens the DSO once per `struct dso`, caches symbols, maps over allocated sections, and optionally walks inline frames with `bfd_find_inliner_info()`. Non-ELF symbol loading opens a BFD file, canonicalizes symbols, derives PE text offsets when possible, sorts symbols, creates perf `struct symbol` entries, and fixes symbol ends/duplicates. Build-id and debuglink helpers open a file and read BFD metadata/sections. BPF disassembly uses libopcodes with BPF program info and optional BTF line info.

## State and Persistence Behavior

Per-DSO BFD state is cached through `dso__set_a2l()` and freed by `dso__free_a2l_libbfd()`. Symbol loading mutates the DSO symbol tree and text offset/end metadata. No on-disk state is written.

## Dependencies and Integration Points

It depends on libbfd/libopcodes, perf DSO/symbol/annotation/BPF metadata, BTF/libbpf when enabled, debug logging, and symbol configuration. It is compiled only when libbfd support is present, with header stubs otherwise.

## Risks and Edge Cases

Libbfd API version differences are handled by compatibility macros but remain a portability risk. Addr2line failures can be noisy unless warnings are disabled. BPF disassembly uses `abort()` on unexpected local BFD setup failures. Build-id reading leaks the opened fd if `bfd_fdopenr()` fails because BFD did not consume it. PE symbol length and text-offset calculation are specialized and need regression coverage.

## Test Signals

Tests should cover addr2line with and without inline frames, non-ELF/PE symbol loading, `.gnu_debuglink` reading, build-id reading, missing/corrupt files, BFD initialization once under threads, and BPF annotation with BTF line info and without libbpf support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libbfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libbfd.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/libbfd.h

## Purpose

`libbfd.h` declares perf's optional libbfd integration and provides stubs when libbfd support is absent.

## Important APIs, Types, and Functions

With `HAVE_LIBBFD_SUPPORT`, it declares addr2line, DSO a2l cleanup, symbol disassembly, build-id reading, debuglink reading, and BPF disassembly. Without libbfd, inline stubs return failure or no-op, with BPF disassembly returning `SYMBOL_ANNOTATE_ERRNO__NO_LIBOPCODES_FOR_BPF`.

## Control Flow

Build configuration selects real declarations or stubs at compile time. Callers can invoke the functions unconditionally and handle failure.

## State and Persistence Behavior

The header defines no state. Real implementations cache state in DSOs.

## Dependencies and Integration Points

It depends on perf annotate, build-id, DSO, inline-node, and symbol types. It integrates symbolization and annotation code with optional libbfd availability.

## Risks and Edge Cases

Stub return values must match caller expectations. Header comments use C++-style comments around preprocessor branches, which is accepted in this C codebase but should remain build-compatible.

## Test Signals

Build matrix tests should cover libbfd enabled and disabled, and callers should gracefully fall back when stubs return failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libbfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libdw.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/libdw.c

## Purpose

`libdw.c` implements perf's optional elfutils/libdwfl-backed address-to-source-line and inline-frame lookup.

## Important APIs, Types, and Functions

It defines `offline_callbacks`, `dso__free_libdw()`, `dso__libdw_dwfl()`, callback args for inline unwinding, `libdw_a2l_cb()`, and public `libdw__addr2line()`.

## Control Flow

`dso__libdw_dwfl()` lazily opens the DSO, starts a Dwfl session, reports the file offline, finalizes the report, and caches the Dwfl pointer in the DSO. `libdw__addr2line()` finds the module for an address, obtains DWARF bias, finds source line info, returns file/line, and optionally walks inline functions at the address. The inline callback rewrites caller srcline on the parent frame and appends inline symbols from parent toward leaf.

## State and Persistence Behavior

The Dwfl session is cached per DSO and released by `dso__free_libdw()`. Returned file strings and inline nodes are caller-owned/perf-owned. No persistent files are written.

## Dependencies and Integration Points

It depends on elfutils libdwfl, DSO accessors, srcline helpers, symbol/inline-node helpers, and dwarf auxiliary functions. It is an alternative addr2line backend to libbfd/LLVM.

## Risks and Edge Cases

File descriptor ownership depends on `dwfl_report_offline()` success. Inline srcline ownership is subtle: the callback may transfer or free `leaf_srcline` and existing list srclines. Missing DWARF, absent module, or invalid source line returns not-found without hard error.

## Test Signals

Tests should cover line lookup, missing debug info, inline chains, DSO cleanup, invalid files, and ownership under repeated lookups with leak checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libdw.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/libdw.h

## Purpose

`libdw.h` declares optional libdw addr2line support and no-op stubs for builds without elfutils support.

## Important APIs, Types, and Functions

With `HAVE_LIBDW_SUPPORT`, it declares `libdw__addr2line()` and `dso__free_libdw()`. Without support, inline stubs return 0 or no-op.

## Control Flow

Build configuration selects real functions or stubs. Callers can attempt libdw lookup and fall back when 0 is returned.

## State and Persistence Behavior

The header defines no state; implementation caches Dwfl contexts in DSOs.

## Dependencies and Integration Points

It uses `u64` and forward declarations for DSO, inline nodes, and symbols. It integrates srcline resolution with optional libdw availability.

## Risks and Edge Cases

Stub behavior must remain consistent with "not found" rather than fatal error. Callers must free returned file strings only on success from real implementations.

## Test Signals

Build tests should cover libdw enabled and disabled. Runtime tests should verify fallback behavior when stubs return 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libdw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libunwind/arm64.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/libunwind/arm64.c

## Purpose

`libunwind/arm64.c` builds and exports ARM64 remote libunwind operations for perf, even when the host architecture differs.

## Important APIs, Types, and Functions

It defines `REMOTE_UNWIND_LIBUNWIND`, maps `LIBUNWIND__ARCH_REG_ID()` to `libunwind__arm64_reg_id()`, aliases `perf_event_arm_regs` to `perf_event_arm64_regs`, includes ARM64 perf-reg UAPI and the architecture unwind implementation, maps `NO_LIBUNWIND_DEBUG_FRAME_AARCH64` to the generic flag, includes local libunwind implementation, and exports `arm64_unwind_libunwind_ops`.

## Control Flow

Compile-time include composition generates architecture-specific unwind functions and assigns `_unwind_libunwind_ops` to the exported ARM64 ops pointer.

## State and Persistence Behavior

The exported ops pointer is static process state. Runtime unwind state is managed by generic libunwind code included here.

## Dependencies and Integration Points

It depends on libunwind headers, ARM64 perf register UAPI, `arch/arm64/util/unwind-libunwind.c`, and `util/unwind-libunwind-local.c`. It integrates with perf thread unwinding for ARM64 targets.

## Risks and Edge Cases

Because implementation files are included directly, macro ordering is critical. Debug-frame feature flags must match the target libunwind. Host/target register mapping must stay aligned with ARM64 UAPI.

## Test Signals

Cross-architecture unwind tests should sample ARM64 user stacks, verify register mapping, test builds with and without debug-frame support, and ensure host-non-ARM builds still expose ARM64 ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libunwind/arm64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libunwind/x86_32.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/libunwind/x86_32.c

## Purpose

`libunwind/x86_32.c` builds and exports 32-bit x86 remote libunwind operations for perf.

## Important APIs, Types, and Functions

It defines `REMOTE_UNWIND_LIBUNWIND`, maps `LIBUNWIND__ARCH_REG_ID()` to `libunwind__x86_reg_id()`, includes x86 perf-register UAPI and the x86 arch unwind implementation with `HAVE_ARCH_X86_64_SUPPORT` undefined, forces `NO_LIBUNWIND_DEBUG_FRAME` for non-ARM, includes local libunwind code, and exports `x86_32_unwind_libunwind_ops`.

## Control Flow

Compile-time macro setup specializes generic and arch unwind implementation files for x86_32 and publishes the resulting ops table.

## State and Persistence Behavior

The exported ops pointer is static process state. Actual unwind cursors and frames are handled by included generic code.

## Dependencies and Integration Points

It depends on libunwind x86 headers, x86 perf-reg UAPI, `arch/x86/util/unwind-libunwind.c`, and generic local unwind code. It integrates with perf unwinding of 32-bit x86 samples.

## Risks and Edge Cases

Macro leakage/order is the primary risk. Accidentally leaving x86_64 support enabled would build the wrong target behavior. Forcing no debug-frame support affects unwind quality and must match library capabilities.

## Test Signals

Tests should include 32-bit x86 stack unwinding, build checks on 64-bit hosts, register mapping validation, and no-debug-frame fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libunwind/x86_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/llvm-c-helpers.cpp -->
# sources/distributed-fs/ceph-client/tools/perf/util/llvm-c-helpers.cpp

## Purpose

`llvm-c-helpers.cpp` bridges perf C code to LLVM's C++ symbolizer APIs for addr2line, inline-frame lookup, and code/data symbol naming.

## Important APIs, Types, and Functions

It defines a process-lifetime `LLVMSymbolizer` from `get_symbolizer()`, `extract_file_and_line()`, exported C functions `llvm_addr2line()`, `llvm_name_for_code()`, and `llvm_name_for_data()`, and helper `make_symbol_relative_string()`.

## Control Flow

The symbolizer is lazily allocated with demangling disabled so perf's own demangler produces consistent names. `llvm_addr2line()` either calls `symbolizeInlinedCode()` and converts every frame into a heap-allocated `llvm_a2l_frame` array, or calls `symbolizeCode()` for a single file/line result. Name helpers call LLVM code/data symbolization and format `name+offset` when LLVM provides a start address distinct from the queried address.

## State and Persistence Behavior

The LLVM symbolizer instance is intentionally leaked until process exit to retain its cache. Returned strings and inline-frame arrays are heap allocated and caller-owned. No files are written.

## Dependencies and Integration Points

It depends on LLVM DebugInfo/Symbolize C++ APIs, Linux compiler/zalloc compatibility, perf DSO demangling, and the C header `llvm-c-helpers.h`. It lets C symbolization code use LLVM features without including LLVM C++ headers.

## Risks and Edge Cases

Memory ownership is strict: every filename/function string and frame array must be freed by the caller. On partial allocation failure the function frees frames allocated so far. `<invalid>` filenames map to NULL to match libbfd conventions. LLVM API behavior and warning profiles vary by version, reflected by diagnostic suppression for LLVM <= 15.

## Test Signals

Tests should cover simple addr2line, inline stacks, invalid addresses, allocation-failure cleanup, demangled C++ symbols through perf demangler, data symbol names, and LLVM version build compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/llvm-c-helpers.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/llvm-c-helpers.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/llvm-c-helpers.h

## Purpose

`llvm-c-helpers.h` exposes a C ABI for perf code to call LLVM C++ symbolization helpers.

## Important APIs, Types, and Functions

It defines `struct llvm_a2l_frame` with heap-owned filename, function name, and line fields. It declares `llvm_addr2line()`, `llvm_name_for_code()`, and `llvm_name_for_data()` inside `extern "C"` for C++ compatibility.

## Control Flow

Callers request source lookup with optional inline unwinding. A positive return from `llvm_addr2line()` is the number of frames; if inline unwinding is enabled, `inline_frames` receives a newly allocated array. Name helpers return a newly allocated symbol string or NULL.

## State and Persistence Behavior

The header defines no global state. It documents caller ownership of returned strings and arrays.

## Dependencies and Integration Points

It depends on `linux/compiler.h` for `u64` and C/C++ linkage macros. It integrates C perf symbolization paths with the C++ implementation file.

## Risks and Edge Cases

Callers must free nested frame strings and the frame array. Return value 1 can mean either no inline expansion or a one-frame inline result. Passing NULL output pointers must match implementation expectations, especially for `inline_frames` when unwinding.

## Test Signals

Build tests should include the header from C and C++ translation units. Runtime tests should validate ownership, NULL returns, inline-frame counts, and code/data name helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/llvm-c-helpers.h -->
