# sources/distributed-fs/ceph-client/drivers/interconnect/samsung/exynos.c

## Purpose

This file implements a generic Exynos interconnect provider used by Exynos bus/devfreq devices. It presents each bus device as a single interconnect node and translates interconnect bandwidth requests into `DEV_PM_QOS_MIN_FREQUENCY` constraints on the parent bus device. The driver is intentionally small: it relies on the interconnect core for aggregation and on PM QoS/devfreq for frequency enforcement.

## Important APIs, Types, And Functions

`struct exynos_icc_priv` stores the platform device pointer, embedded `struct icc_provider`, the single `struct icc_node`, a `dev_pm_qos_request`, and the `bus_clk_ratio` used to translate bandwidth to frequency. `exynos_icc_get_parent()` reads the optional `interconnects` phandle from the bus node and resolves it through `of_icc_get_from_provider()`. `exynos_generic_icc_set()` is the provider `.set` callback; it computes source and destination minimum frequencies from `max(avg_bw, peak_bw) / bus_clk_ratio` and updates PM QoS for both endpoint devices. `exynos_generic_icc_xlate()` returns the provider's single node only when the phandle target matches the parent bus device OF node.

`exynos_generic_icc_probe()` allocates state, configures provider callbacks (`set`, `aggregate = icc_std_aggregate`, `xlate`, `inter_set = true`), creates one `icc_node` named from the parent OF node, reads optional `samsung,data-clock-ratio`, adds a PM QoS request to the parent bus device, links to an optional parent interconnect node, and registers the provider. `exynos_generic_icc_remove()` deregisters the provider and removes nodes.

## Control Flow

The module platform driver binds to platform devices named `exynos-generic-icc`. Probe works bottom-up from the parent bus device: create provider state, register a node, install PM QoS, link to parent if present, then register with the interconnect core. Bandwidth requests flow from client drivers through the interconnect framework, which aggregates requests and calls `.set`; the driver then updates source and destination PM QoS constraints. Error paths unwind the PM QoS request and node registration.

## State And Persistence

Runtime state is per platform device and devm-managed except for interconnect node and PM QoS request cleanup. The bus clock ratio is effectively persistent DT policy, defaulting to `EXYNOS_ICC_DEFAULT_BUS_CLK_RATIO` when unspecified. No on-disk state exists. The externally persistent interface is device tree: parent/child `interconnects` links and `samsung,data-clock-ratio` determine path shape and frequency scaling.

## Dependencies And Integration Points

The driver depends on the interconnect provider core, OF phandle parsing, PM QoS, platform devices, and devfreq-capable bus parents. It integrates with Exynos bus nodes created elsewhere, with clients that request interconnect bandwidth, and with `icc_sync_state` for late provider synchronization. The node ID is `pdev->id`, so platform-device ID allocation must be stable and unique for each provider instance.

## Risks

Frequency conversion is approximate and sensitive to `bus_clk_ratio`; an incorrect ratio can underclock or overclock buses. `exynos_generic_icc_set()` updates source PM QoS first and destination second; if the destination update fails after source succeeds, the source constraint remains changed. Parent links are optional, so missing DT links can reduce path coverage without failing probe. `xlate()` strictly matches `spec->np` against the parent OF node, making DT provider placement important. Remove unregisters provider/nodes but relies on PM QoS devm/device lifetime to avoid stale constraints.

## Test Signals

Useful tests include Exynos boot with the driver builtin and modular, DT validation for `interconnects` and `samsung,data-clock-ratio`, interconnect client bandwidth changes reflected in PM QoS/devfreq frequency requests, parent-child path creation across multi-bus topologies, and fault injection for PM QoS update failures. `COMPILE_TEST` builds catch API drift in interconnect and PM QoS usage.
