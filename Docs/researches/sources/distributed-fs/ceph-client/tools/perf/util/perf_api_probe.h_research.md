
# sources/distributed-fs/ceph-client/tools/perf/util/perf_api_probe.h

Purpose: declares runtime kernel perf API capability probes.

Important APIs/types/functions: exposes boolean functions for AUX sample support, comm exec records, CPU-wide recording, context-switch records, text-poke records, sample identifiers, build-id records, and cgroup records.

Control flow: none in the header. Callers invoke probes before enabling optional perf_event_attr fields or modes.

State and persistence: no header state; implementation keeps only minimal process-local probe cache/fallback behavior.

Dependencies: booleans.

Integration points: included by recording/session setup code that needs feature gating across kernel versions and permission environments.

Risks: callers must treat false as "do not enable feature" rather than fatal unless the feature was explicitly required. Test signals are compile coverage and feature-gating tests on kernels with varied perf API support.
