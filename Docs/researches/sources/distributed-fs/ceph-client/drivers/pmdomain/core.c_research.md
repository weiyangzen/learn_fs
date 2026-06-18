<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/core.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/core.c

## Purpose

`core.c` is the generic PM domain framework implementation. It registers/removes `struct generic_pm_domain` instances, attaches devices, links parent/child domains, handles runtime PM and system sleep callbacks, selects and accounts idle states, forwards performance-state votes, and exposes OF provider helpers plus debugfs state. It is infrastructure used by SoC providers, not a hardware driver.

## Important APIs, types, and functions

Key exported APIs are `pm_genpd_init()`, `pm_genpd_remove()`, device/subdomain add/remove helpers, OF provider helpers, DT attach helpers, performance-state helpers, wakeup/hrtimer helpers, hardware-mode helpers, and notifier helpers. Internals revolve around `gpd_list`, OF provider lists, `genpd_lock_ops`, `_genpd_power_on/off()`, `genpd_power_on/off()`, runtime suspend/resume callbacks, system noirq callbacks, `genpd_alloc_dev_data()`, and debugfs show functions.

## Control flow

Providers initialize genpd objects and register simple or onecell OF providers. Consumers attach through direct APIs or DT parsing, after which the core installs PM-domain callbacks on the device. Runtime suspend checks governor policy, suspends/stops the device, and powers off the domain if all devices and children permit it. Runtime resume restores performance votes, powers parents and the domain on, starts the device, and resumes the device. System sleep uses prepared/suspended counters and synchronous power transitions.

## State and persistence behavior

Per-domain state includes status, selected idle state, device and link lists, counters, flags, provider identity, performance state, CPU masks, notifier chains, and governor data. Per-device state tracks timing, QoS cache, runtime/default performance votes, hardware mode, and rpm-always-on. Hardware persistence is provider-owned; this file calls callbacks that write registers, firmware, clocks, regulators, or resets.

## Dependencies and integration points

It depends on runtime PM, PM QoS, OPP, PM clocks, OF, debugfs, CPU/cpuidle, workqueues, IDA, and the device model. It integrates with `power-domains`, `power-domain-names`, `domain-idle-states`, required OPPs, and provider `#power-domain-cells`.

## Risks and edge cases

Parent/child locking and rollback are delicate, IRQ-safe mismatches keep domains on, sync_state controls boot-on `stay_on` behavior, multi-domain virtual devices need careful detach and required-OPP handling, provider runtime PM can interact with system sleep, and removal fails while providers/devices/links/prepared users remain.

## Test signals

Test onecell/simple providers, runtime suspend/resume with QoS, system sleep, performance-state propagation and rollback, required OPP defaults, virtual-device attach by ID/name, sync_state power-off, debugfs accounting, invalid indexes, missing providers, removal while busy, IRQ-safe mismatches, and `pd_ignore_unused`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/core.c -->
