<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/ti/ti_sci_pm_domains.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/ti/ti_sci_pm_domains.c

Purpose: TI SCI firmware-backed generic PM domain provider. It discovers device IDs referenced by DT consumers, creates sparse domains, and forwards power and sleep constraints through TI SCI protocol ops.

Important APIs/types/functions: `ti_sci_genpd_provider` stores SCI handle, domain list, and onecell data. `ti_sci_pm_domain` stores device ID, exclusive/shared request flag, genpd, and provider link. Key functions include `ti_sci_pd_power_on/off()`, sleep-only `ti_sci_pd_suspend()`, `ti_sci_pd_xlate()`, `ti_sci_pm_pd_is_on()`, and `ti_sci_pm_domain_probe()`.

Control flow: probe gets the TI SCI handle, scans every DT node with `power-domains`, parses references to this provider, deduplicates IDs, creates one domain per unique SCI device ID, determines initial state via optional `is_on`, and builds a sparse array indexed by max ID. Xlate accepts one or two cells; the optional second cell sets exclusive mode before returning the genpd. Power-on requests the device exclusively or shared; power-off puts it. Suspend applies latency and wakeup constraints when firmware supports the constraint API.

State/persistence: firmware owns actual device state. Software tracks domain objects in a list and a sparse onecell array; `exclusive` is mutable per xlate/consumer and therefore reflects the latest xlate call for that domain.

Dependencies/integration: depends on `ti_sci_protocol`, PM QoS, runtime PM, generic PM domains, DT binding `ti,sci-pm-domain`, and `dt-bindings/soc/ti,sci_pm_domain.h`.

Risks: mutating `exclusive` in `ti_sci_pd_xlate()` can be ambiguous if multiple consumers of the same SCI ID specify different access modes. The scan only creates domains referenced by existing DT consumers, so unreferenced firmware devices are not exposed. Constraint conversion truncates usec to msec. If firmware lacks `is_on`, domains are initialized off.

Test signals: DTs with repeated and sparse SCI IDs, one-cell and two-cell phandles, shared/exclusive request behavior, suspend with PM QoS latency and wake-capable devices, and missing constraint/is_on firmware operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/ti/ti_sci_pm_domains.c -->
