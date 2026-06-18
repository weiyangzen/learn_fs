# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/intel-bts.c

Purpose: implements perf record-side Intel Branch Trace Store AUX trace setup for the `intel_bts` PMU. It creates an `auxtrace_record` provider, configures record options, fills `PERF_RECORD_AUXTRACE_INFO`, and handles snapshot-mode head/old adjustment for BTS circular buffers.

Important APIs/types/functions: `struct intel_bts_recording` wraps `struct auxtrace_record` with PMU, evlist, snapshot mode, and per-mmap snapshot reference state. `intel_bts_recording_init()` is the exported initializer. `intel_bts_recording_options()` validates user options, finds the single BTS evsel, sets `needs_auxtrace_mmap`, defaults mmap sizes, and injects a dummy tracking event. `intel_bts_info_fill()` writes BTS PMU type and TSC conversion fields. `intel_bts_find_snapshot()` reconciles circular AUX buffer wrap semantics. `intel_bts_reference()` returns `rdtsc()` for JIT dump timestamp alignment.

Control flow: initialization finds `INTEL_BTS_PMU_NAME`, sets `JITDUMP_USE_ARCH_TIMESTAMP`, allocates the recorder, and installs callback pointers. During record setup, the BTS event is moved to the evlist front so its fd can back AUX mmaps; full tracing enables dummy tracking, and snapshot mode disables/enables the BTS evsel around snapshots. Snapshot finalization detects first wrap by scanning the tail of the buffer and then normalizes `old`/`head` to the full-trace monotonic model.

State and persistence: state is in process memory only: `snapshot_refs` grows by powers of two and stores per-mmap wrap booleans plus optional ref buffers. The output persisted to perf.data is the auxtrace info private array, including PMU type, TSC conversion, and snapshot flag. No standalone files are written by this file.

Dependencies and integration: depends on perf util evlist/evsel/session/mmap/record/auxtrace APIs, PMU discovery, `perf_read_tsc_conversion()`, `parse_event("dummy:u")`, page size, and x86 `rdtsc()`. It integrates with perf record's generic auxtrace lifecycle through the callback table returned as `struct auxtrace_record *`.

Risks: option validation is strict: more than one BTS event, per-CPU recording, sample mode, non-power-of-two AUX sizes, or snapshot size larger than AUX mmap all fail. Snapshot wrap detection is heuristic before explicit wrap has been observed, so small or all-zero buffers can be ambiguous. Allocation growth must be checked because snapshot callback failures abort recording.

Test signals: build with Intel BTS support, `perf record -e intel_bts// ...`, snapshot mode `perf record -S -e intel_bts// ...`, nonprivileged defaults, invalid AUX mmap sizes, duplicate BTS events, and perf.data decode checks for `PERF_AUXTRACE_INTEL_BTS` metadata.
