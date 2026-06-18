# sources/distributed-fs/ceph-client/drivers/pmdomain/arm/scmi_perf_domain.c

Purpose: SCMI performance-domain provider that exposes firmware performance domains through genpd performance-state APIs and dynamic OPP tables.

Important APIs/types/functions: `struct scmi_perf_domain` wraps `generic_pm_domain` with SCMI perf ops, protocol handle, domain info, and domain ID. `scmi_pd_set_perf_state()` calls firmware `level_set`; `scmi_pd_attach_dev()` adds firmware-provided OPPs; `scmi_pd_detach_dev()` removes dynamic OPPs; `scmi_perf_domain_probe()` creates the provider; `scmi_perf_domain_remove()` tears it down.

Control flow: SCMI bus probe first requires a `#power-domain-cells` property, then obtains SCMI PERF protocol ops, queries domain count, allocates domains and onecell data, initializes each genpd as always-on with firmware OPP/dev-name flags and attach/detach/set-performance callbacks, registers the onecell provider, and stores driver data. Attach adds OPPs only for domains where firmware says performance can be set. Setting performance state rejects state 0 and warns on firmware failure.

State and persistence: per-domain state is firmware metadata and genpd/OPP registrations. Actual performance level state lives in SCMI firmware. Dynamic OPPs live only while devices are attached.

Dependencies/integration: depends on SCMI PERF protocol, genpd performance-state support, PM OPP core, OF onecell provider, and SCMI device matching for protocol `SCMI_PROTOCOL_PERF`.

Risks: the driver returns success for non-settable performance domains while still attaching devices, so consumers must handle lack of performance control. State 0 is invalid, which must match OPP mapping. Probe is skipped silently if the SCMI node is not a provider. Removal assumes registered domains exist only when probe completed.

Test signals: provider registration only with `#power-domain-cells`, correct domain count/names from firmware, dynamic OPP creation/removal on device attach/detach, successful nonzero performance-state changes, and clean removal with all genpds unregistered.
