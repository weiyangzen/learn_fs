# sources/distributed-fs/ceph-client/drivers/sh/pm_runtime.c

Purpose: SuperH runtime PM glue that attaches the PM clock domain helpers to platform bus devices.

Important APIs and data: `default_pm_domain` uses `USE_PM_CLK_RUNTIME_OPS` and `USE_PLATFORM_PM_SLEEP_OPS`. `platform_bus_notifier` points at that domain and requests the default clock connection id. `sh_pm_runtime_init` registers the notifier with `platform_bus_type` through `pm_clk_add_notifier`.

Control flow: `core_initcall` installs the notifier early. Platform devices can then acquire PM clock runtime operations through the generic PM clock framework.

State and dependencies: static PM domain and notifier block. Dependencies include runtime PM, PM clock helpers, platform device bus, legacy SH clock APIs, and generic PM domains. Risks include applying a default domain to devices with custom PM expectations, missing clocks, and init ordering relative to platform device creation. Test signals are platform device runtime suspend/resume calling clock helpers, no boot-time notifier registration failures, and correct sleep ops for SH platform devices.
