# sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-gpci.c

Purpose: registers the `hv_gpci` perf PMU for IBM Power LPAR systems that expose hypervisor "get performance counter info" counters through `H_GET_PERF_COUNTER_INFO`. It turns generated request encodings into perf events and exposes hypervisor capabilities and selected Power10+ topology/system-information requests through sysfs.

Important APIs/types/functions: `h_gpci_pmu`, `hv_gpci_init`, `single_gpci_request`, `h_gpci_event_init`, `h_gpci_event_update`, `ppc_hv_gpci_cpu_online/offline`, `systeminfo_gpci_request`, the processor topology/config/affinity `*_show` handlers, and `sysinfo_device_attr_create`. Request field formats are exported with `EVENT_DEFINE_RANGE_FORMAT`, while event names come from generated `hv_gpci_event_attrs` and `hv_gpci_event_attrs_v6`.

Control flow and state: initialization checks `FW_FEATURE_LPAR`, reads `hv_perf_caps`, installs CPU hotplug state, probes counter-info version with request `0x10`, chooses the v8 or v6 generated event table, registers the PMU, and conditionally adds Power10+ sysinfo attributes. Normal perf reads call a per-CPU `hv_gpci_reqb` buffer, issue the hcall, decode a big-endian byte range selected by `offset` and `length`, and accumulate deltas in `event->count`. Sysinfo files loop on `H_PARAMETER` partial responses and append hex records into one page.

State and persistence behavior: no persistent storage is written. Runtime state is a PMU registration, generated sysfs attribute groups, a single active collection CPU mask, hotplug migration via `perf_pmu_migrate_context`, per-CPU request buffers, and dynamically allocated sysinfo `device_attribute` objects that live for the lifetime of the PMU.

Dependencies and integration points: depends on PowerPC LPAR firmware, `plpar_hcall_norets`, `hv_perf_caps_get`, generated `req-gen/perf.h` artifacts from `hv-gpci.h`, perf core PMU callbacks, CPU hotplug, and PVR detection for Power10 sysinfo exposure. User integration is through `perf stat -e hv_gpci/.../` and `/sys/bus/event_source/devices/hv_gpci/{format,events,interface,cpumask}`.

Risks: sysinfo output is page-limited and can return `-EFBIG`; partial response cursor extraction is request-specific and easy to break with layout changes; `add_sysinfo_interface_files` allocates attributes without a visible free path after successful registration; hcall return-code handling maps many firmware failures to generic `-EIO`/`-EINVAL`; counters read as zero on read hcall failure, which can hide transient errors.

Test signals: build with PowerPC perf and LPAR support; boot on an LPAR with performance information enabled; verify `hv_gpci` appears under event sources, `cpumask` tracks CPU hotplug, known generated events can be read by `perf stat`, unsupported or unauthorized partitions return `EPERM`/fail cleanly, and Power10+ sysinfo files either contain hex records or report documented hcall errors.
