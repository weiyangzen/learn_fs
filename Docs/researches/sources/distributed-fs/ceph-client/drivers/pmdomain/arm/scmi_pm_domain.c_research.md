# sources/distributed-fs/ceph-client/drivers/pmdomain/arm/scmi_pm_domain.c

Purpose: SCMI generic power-domain provider for firmware-controlled on/off power domains.

Important APIs/types/functions: `struct scmi_pm_domain` wraps a genpd with SCMI protocol handle, firmware name, and domain index. `scmi_pd_power()` calls `state_set`; `scmi_pd_power_on/off()` set generic ON/OFF states. `scmi_pm_domain_probe()` builds domains from SCMI POWER protocol; `scmi_pm_domain_remove()` removes provider and genpds.

Control flow: probe gets SCMI POWER ops, reads domain count, allocates arrays, loops over firmware domains, reads each current state, re-sends ON state for domains already on so OSPM ownership is registered with firmware, initializes genpd with `GENPD_FLAG_ACTIVE_WAKEUP` and current off/on state, and registers an OF onecell provider. Remove deletes the provider and removes non-null genpds.

State and persistence: software stores domain index/name and genpd state; actual power state and OSPM ownership are tracked by SCMI firmware. The global `power_ops` pointer is shared by driver instances.

Dependencies/integration: depends on SCMI POWER protocol, generic PM domains, OF provider registration, and SCMI device matching for `SCMI_PROTOCOL_POWER`.

Risks: failed `state_get()` skips a domain and leaves a null onecell slot; consumers for that index will fail. Global `power_ops` is simple but not instance-isolated. Reasserting ON ownership at probe is important; removing it could let firmware turn off a boot-enabled domain unexpectedly.

Test signals: firmware domain count and names appear in logs, existing-on domains remain available after probe, power on/off calls produce SCMI state changes, null-slot behavior is acceptable for failed state reads, and provider removal cleans all initialized genpds.
