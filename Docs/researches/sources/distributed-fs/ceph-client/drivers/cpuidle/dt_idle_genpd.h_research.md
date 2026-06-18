<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_genpd.h -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_genpd.h

## Purpose

`dt_idle_genpd.h` is the public local interface for cpuidle DT/genpd helpers. It lets cpuidle platform drivers use CPU PM-domain topology when `CONFIG_DT_IDLE_GENPD` is enabled while compiling clean stubs otherwise.

## Important APIs, Types, And Functions

The enabled declarations cover `dt_idle_pd_free()`, `dt_idle_pd_alloc()`, `dt_idle_pd_init_topology()`, `dt_idle_pd_remove_topology()`, `dt_idle_attach_cpu()`, and `dt_idle_detach_cpu()`. Disabled builds return success or NULL-style no-op values and free nothing.

## Control Flow

There is no direct runtime flow beyond the inline stubs. The header shapes caller behavior: drivers can call these helpers unconditionally and interpret NULL/0 results when the feature is not compiled in.

## State And Persistence Behavior

The header does not allocate state. It controls whether PM-domain state can exist at all for a given build.

## Dependencies And Integration Points

It forward-declares `device_node` and `generic_pm_domain` and integrates with DT idle drivers that support hierarchical CPU idle state selection.

## Risks And Test Signals

Risks include callers failing to handle NULL from disabled stubs, assuming topology exists on non-genpd builds, and missing compile coverage for both branches. Test with `CONFIG_DT_IDLE_GENPD=y` and disabled builds, plus platform probe paths using all helper calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_genpd.h -->
