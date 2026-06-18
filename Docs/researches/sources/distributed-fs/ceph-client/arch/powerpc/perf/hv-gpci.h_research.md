# sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-gpci.h

Purpose: small glue header for the hypervisor GPCI PMU. It defines the current counter-info version, capability bit masks, and parameters used by the request generator include to produce event format helpers and event attribute arrays.

Important APIs/types/functions: `COUNTER_INFO_VERSION_CURRENT`, `HV_GPCI_CM_GA`, `HV_GPCI_CM_EXPANDED`, `HV_GPCI_CM_LAB`, `REQUEST_FILE`, `NAME_LOWER`, `NAME_UPPER`, `ENABLE_EVENTS_COUNTERINFO_V6`, and the included `req-gen/perf.h` output. Consumers rely on generated symbols such as `hv_gpci_event_attrs`, `hv_gpci_event_attrs_v6`, event field extractors, and offset assertions.

Control flow and state: the file has no runtime control flow. At compile time it points the request generator at `../hv-gpci-requests.h` and asks it to emit `hv_gpci`-named code, including alternate counter-info-v6 event lists.

State and persistence behavior: no persistent or runtime state is owned here. The constants become compiled kernel ABI for sysfs `kernel_version` and generated event decoding.

Dependencies and integration points: included by `hv-gpci.c`; indirectly depends on `hv-gpci-requests.h` and `req-gen/perf.h`. It must stay synchronized with the hypervisor GPCI specification and with the generated request/event fields used by the perf PMU.

Risks: `COUNTER_INFO_VERSION_CURRENT` and capability masks are ABI-visible; stale version constants can mislead userspace even if the runtime event list probes an older firmware version. Incorrect generator macro names would break symbol names used by `hv-gpci.c`.

Test signals: compile the PowerPC perf tree, confirm generated `hv_gpci` symbols resolve, inspect sysfs `interface/kernel_version`, and run an event from both version-specific generated lists on suitable firmware.
