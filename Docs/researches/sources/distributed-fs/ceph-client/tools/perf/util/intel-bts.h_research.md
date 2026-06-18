# sources/distributed-fs/ceph-client/tools/perf/util/intel-bts.h

Purpose: public interface and AUXTRACE private metadata contract for perf's Intel BTS support.

Important APIs and types: defines `INTEL_BTS_PMU_NAME` as `"intel_bts"`. The anonymous enum defines indices into the auxtrace-info private array: PMU type, time conversion fields, `cap_user_time_zero`, snapshot mode, and max. `INTEL_BTS_AUXTRACE_PRIV_SIZE` expresses the private payload size in bytes. Declares `intel_bts_recording_init()` for recording setup and `intel_bts_process_auxtrace_info()` for report/inject decode setup.

Control flow: record-side code uses the PMU name and private indices to serialize metadata. Process-side code passes AUXTRACE_INFO events to `intel_bts_process_auxtrace_info()`, which installs the runtime auxtrace callbacks implemented in `intel-bts.c`.

State and persistence: the enum is a persisted file-format contract inside perf.data auxtrace-info records. Reordering or changing indices breaks compatibility with existing recordings.

Dependencies and integration: forward-declares perf session/tool/event and auxtrace types to keep the header light. Integrates perf record metadata generation with perf report/inject decode.

Risks: comment text says "Intel Processor Trace support" although this header is BTS-specific, which can confuse readers. The private array layout must stay stable.

Test signals: perf record/report round trips for BTS data, validation of private payload size, and compatibility tests against old perf.data files.
