<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm_bus.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm_bus.c

## Purpose
Installs a default runtime PM domain for OMAP1 platform devices using the PM clock framework, so devices can gate interface/function clocks named `ick` and `fck`.

## Important APIs, Types, and Functions
Defines a `dev_pm_domain` using `USE_PM_CLK_RUNTIME_OPS` and `USE_PLATFORM_PM_SLEEP_OPS`, a `pm_clk_notifier_block`, and `core_initcall omap1_pm_runtime_init()`.

## Control Flow
At core init, OMAP1-only code registers a PM clock notifier on `platform_bus_type`. Devices later bound to the platform bus can have clocks associated and managed through the default PM domain.

## State and Persistence Behavior
Persistent state is the registered notifier and default PM domain. Clock state is managed by PM core callbacks rather than this file directly.

## Dependencies and Integration Points
Depends on runtime PM, PM clock framework, platform bus, clock names `ick` and `fck`, and `cpu_class_is_omap1()`.

## Risks
Devices without matching clocks or with nonstandard clock names get limited benefit. Registering this too broadly would affect non-OMAP1 devices, hence the CPU-class guard.

## Test Signals
Boot OMAP1 with runtime PM enabled and verify platform devices can runtime suspend/resume with `ick`/`fck` clocks toggled. Non-OMAP1 builds should return `-ENODEV`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm_bus.c -->
