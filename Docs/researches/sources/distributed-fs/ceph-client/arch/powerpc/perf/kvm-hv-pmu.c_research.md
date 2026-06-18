# sources/distributed-fs/ceph-client/arch/powerpc/perf/kvm-hv-pmu.c

Purpose: implements a system-wide `kvm-hv` PMU for nestedv2 Book3S-HV guests, exposing L0 host-wide memory usage statistics to perf in an L1 environment.

Important APIs/types/functions: `kvmppc_pmu`, `kvmppc_register_pmu`, `kvmppc_init_hostwide`, `kvmppc_update_l0_stats`, `kvmppc_pmu_event_update`, `hostwide_get_size`, `hostwide_fill_info`, `hostwide_refresh_info`, `gsb_ops_l0_stats`, and event IDs `KVMPPC_EVENT_HOST_*`.

Control flow and state: module init checks `kvmhv_is_nestedv2`, allocates a guest-state message and buffer for L0 stats, includes the five supported GSIDs, fills the request buffer, and registers the PMU. Each perf read/add/del refreshes L0 stats under `lock_l0_stats`, selects the configured statistic, and adds a positive delta to the perf count. Module exit frees the GSB/GSM and unregisters the PMU.

State and persistence behavior: no persistent storage. Runtime state is global `l0_stats`, one guest-state message, one guest-state buffer, a parser, and a spinlock. Event `prev_count` and `count` track deltas; max-style counters only increase the perf count when the returned value grows.

Dependencies and integration points: depends on nested KVM-HV v2 support, guest-state-buffer helpers (`kvmppc_gsb_*`, `kvmppc_gsm_*`, `kvmppc_gse_*`), perf PMU registration, and L0 support for host-wide GSIDs. Sysfs exposes event names and `format/event`.

Risks: if `perf_pmu_register` fails after `kvmppc_init_hostwide`, init returns without freeing allocated GSM/GSB; all reads serialize on one spinlock and perform a hypervisor communication path; counter semantics are delta-only and ignore decreases; unsupported nested versions silently skip registration with `-EOPNOTSUPP`.

Test signals: build as module/built-in with KVM Book3S-HV; boot nestedv2; verify `/sys/bus/event_source/devices/kvm-hv`; run `perf stat -e kvm-hv/host_heap/` and related events while changing nested guest memory/page-table load; test unload cleanup and non-nested registration failure.
