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
