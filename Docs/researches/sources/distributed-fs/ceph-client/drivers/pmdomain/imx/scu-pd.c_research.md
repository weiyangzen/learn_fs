<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/scu-pd.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/scu-pd.c

## Purpose

`scu-pd.c` implements NXP i.MX SCU firmware-backed power domains. Each generated genpd maps to an SCU resource ID and changes resource power mode through SCFW RPCs rather than direct MMIO.

## Important APIs, types, and functions

RPC message structs encode get/set resource power mode. `struct imx_sc_pm_domain` embeds genpd, generated name, and resource ID. `struct imx_sc_pd_range` describes resource ranges. `imx_sc_pd_power()` sends ON or LP mode RPCs and keeps the console resource on for `no_console_suspend`. `imx_scu_pd_xlate()` maps DT resource IDs to compacted domains.

## Control flow

Probe gets the SCU IPC handle, chooses SoC range data, parses stdout's power-domain resource, expands owned resource ranges into genpds, reads initial firmware mode, and registers a onecell provider with custom resource-ID translation. Power callbacks send synchronous SCU RPCs.

## State and persistence behavior

Software state is generated domains, resource IDs, global SCU handle, and console resource ID. Actual power state persists in SCFW-managed resource modes. Initial genpd state is synchronized by querying firmware.

## Dependencies and integration points

It depends on i.MX SCU IPC/resource-management APIs, DT resource IDs, OF stdout parsing, genpd, and platform drivers. Consumers pass SCU resource IDs in `power-domains`.

## Risks and edge cases

The domain array is compacted after skipping unowned resources, so default index xlate would be wrong. `imx_sc_get_pd_power()` returns a response mode even after RPC error. Names can truncate at 20 bytes. Console protection only covers the parsed first specifier. No remove path deletes the provider because the driver is built-in.

## Test signals

Validate SCU handle acquisition, ownership filtering, names, custom xlate, initial mode sync, console keepalive, RPC failures, skipped resources, multi-domain consumers, and both SCU compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/scu-pd.c -->
