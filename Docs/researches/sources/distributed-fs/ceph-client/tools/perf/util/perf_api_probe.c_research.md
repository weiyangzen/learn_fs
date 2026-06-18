
# sources/distributed-fs/ceph-client/tools/perf/util/perf_api_probe.c

Purpose: probes whether the running kernel accepts newer `perf_event_attr` fields and CPU-wide recording modes before perf enables related features.

Important APIs/types/functions: `perf_do_probe_api` parses a safe event, opens it once, applies a setup callback that toggles one attr field, opens it again, and interprets `EINVAL` as unsupported. `perf_probe_api` tries `software/cpu-clock/u` first, then core PMU `cycles` or `instructions` events. Setup callbacks toggle sample identifier, comm exec, context switch, text poke, build-id, and cgroup bits. Public probes are `perf_can_sample_identifier`, `perf_can_comm_exec`, `perf_can_record_switch_events`, `perf_can_record_text_poke_events`, `perf_can_record_cpu_wide`, `perf_can_aux_sample`, `perf_can_record_build_id`, and `perf_can_record_cgroup`.

Control flow: probe opens use close-on-exec flags and the first online CPU. If cpu-wide `pid=-1` fails with `EACCES`, a static `pid` fallback switches subsequent probes to `pid=0`. `perf_can_record_cpu_wide` directly opens a software CPU-clock event for `pid=-1,cpu=first`. `perf_can_aux_sample` deliberately sets only `aux_sample_size=1` and relies on `E2BIG` to indicate an old kernel attr size.

State and persistence: only static `pid` inside `perf_do_probe_api` persists to remember permission fallback. Probes create transient evlists and file descriptors, closing/deleting them before return.

Dependencies: sys_perf_event_open, evlist/evsel, parse-events, PMU scanning, online CPU maps, close-on-exec flag helper, errno, and kernel perf attr semantics.

Integration points: used by record/stat/session setup to gate features like sample identifiers, comm exec, switch/text-poke/build-id/cgroup records, CPU-wide recording, and AUX sample size.

Risks: probing can be affected by permissions, perf_event_paranoid, unavailable PMUs, or container restrictions, causing false negatives. `perf_can_aux_sample` only checks kernel attr-size support, not hardware AUX sampling. Test signals include unit/smoke probes on old and new kernels, permission-restricted environments, and feature-specific record tests.
