# sources/distributed-fs/ceph-client/drivers/soc/tegra/common.c

## Purpose

`common.c` provides shared Tegra SoC helpers: machine detection and OPP table initialization for core devices that need process/speedo-aware operating points.

## Important APIs, Types, and Functions

`soc_is_tegra()` checks the machine compatible against older Tegra families. `tegra_core_dev_init_opp_state()` initializes a device's current OPP/performance state from its clock rate. `devm_tegra_core_dev_init_opp_table()` is exported and configures OPP supported-hardware filtering, optional OPP table loading, and optional initial state sync.

## Control Flow

Callers pass a device and `struct tegra_core_opp_params`. The helper sets a dummy clock-name config so even devices without DT OPPs can use the same rate path. For Tegra20 it uses `tegra_sku_info.soc_process_id`; for Tegra30/Tegra114 it uses `soc_speedo_id` to set `supported_hw`. It registers OPP config, returns `-ENODEV` on Tegra124+ where old supported-hw filtering is not used, otherwise loads the DT OPP table. If requested, it temporarily enables runtime PM, calls `dev_pm_opp_set_rate()` with the current clock rate to establish a GENPD performance vote, and restores runtime PM state.

## State and Persistence Behavior

No global mutable state is owned here. Device-managed OPP config/table allocations persist for the device lifetime. Runtime PM may be briefly enabled to cache GENPD performance state.

## Dependencies and Integration Points

It depends on OF machine matching, clocks, runtime PM, PM OPP, Tegra fuse SKU data, and `soc/tegra/common.h`. It integrates core Tegra devices with OPP and generic power-domain performance voting.

## Risks and Edge Cases

Returning `-ENODEV` for unsupported/newer paths is expected but callers must treat it correctly. If a device has no clock or zero clock rate, initialization fails. Temporarily enabling runtime PM can interact with drivers that assume RPM state is untouched. Supported-hardware bit shifts rely on fuse ids being in range.

## Test Signals

Test Tegra20/Tegra30/Tegra114 OPP filtering by process/speedo id, devices with empty OPP tables, `init_state` true/false, missing clock, zero clock, and runtime PM initially enabled or disabled.
