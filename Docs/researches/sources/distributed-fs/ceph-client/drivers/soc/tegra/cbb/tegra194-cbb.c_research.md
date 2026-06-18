# sources/distributed-fs/ceph-client/drivers/soc/tegra/cbb/tegra194-cbb.c

## Purpose

`tegra194-cbb.c` handles Control Backbone/FlexNoC errors on Tegra194. It registers per-NoC platform devices, enables CBB error logging, decodes ErrLogger registers with route/aperture lookup tables, reports AXI/APB transaction details, and escalates fatal in-band CCPLEX errors.

## Important APIs, Types, and Functions

Key structures are `tegra194_cbb_packet_header`, `tegra194_cbb_aperture`, `tegra194_cbb_userbits`, `tegra194_cbb_noc_data`, `tegra194_axi2apb_bridge`, and `tegra194_cbb`. Large static tables map initiators, target flows, route ids, apertures, and error codes for CBB central, BPMP, AON, RCE, and SCE NoCs. Parse helpers include `cbbcentralnoc_parse_routeid()`, `bpmpnoc_parse_routeid()`, `aonnoc_parse_routeid()`, `scenoc_parse_routeid()`, `cbbcentralnoc_parse_userbits()`, and `clusternoc_parse_userbits()`. Runtime operations are exposed through `tegra194_cbb_ops`.

## Control Flow

Probe obtains SoC data from OF compatible strings, masks in-band SError through `tegra194_miscreg_mask_serror()` for CBB central, maps the ErrLogger register resource, resolves secure/nonsecure IRQs, optionally maps shared AXI2APB bridge status resources, adds the instance to a global `cbb_list`, and calls common CBB registration. Registration requests IRQs, enables stall and fault bits on three ErrLoggers, and creates debugfs. On interrupt or debugfs read, the driver scans all registered NoCs, reads three ErrVld bits, selects the first active ErrLogger, reads ErrLog0/1/2/3/4/5, decodes transaction type, error code, route id, target flow/subrange, reconstructed address, user bits, cache/protection attributes, and optional AXI2APB bridge raw status. It clears the ErrLogger after printing. Fatal SLV errors from CCPLEX can trigger `BUG()`, while DEC/SEC/UNS/DISC paths warn instead.

## State and Persistence Behavior

Each instance stores mapped registers, resource identity, IRQ numbers, decoded ErrLog snapshots, NoC metadata, and optional shared AXI2APB bridge mappings. A global spinlocked `cbb_list` tracks instances. Hardware error logger state persists until cleared via ErrClr. On resume noirq, error reporting is re-enabled.

## Dependencies and Integration Points

It depends on platform/OF resources, Tegra fuse/miscreg helpers, common CBB helpers, debugfs, IRQ handling, MMIO accessors, and FlexNoC register semantics. It integrates with DT compatibles such as `"nvidia,tegra194-cbb-noc"` and the `nvidia,axi2apb` phandle.

## Risks and Edge Cases

The file contains large hand-maintained lookup tables; wrong entries produce misleading diagnostics. `clusternoc_parse_userbits()` appears to extract `axprot` using `CLUSTER_NOC_AXCACHE` rather than `CLUSTER_NOC_AXPROT`, which is a bug signal. Several decoded indexes are used to index string arrays without full bounds checks. The ISR holds a spinlock while printing extensive diagnostics and may call `BUG()`. Only one active ErrLogger is printed because `print_errlog()` uses `else if`. Shared bridge mapping is reused from the first instance with bridges.

## Test Signals

Validate probe for all Tegra194 NoC compatibles, one/two IRQ layouts, AXI2APB phandle mapping, suspend/resume re-enable, debugfs reads, and injected SLV/DEC/SEC/UNS/TMO errors. Static review should check field masks, table bounds, and the suspected `CLUSTER_NOC_AXPROT` extraction issue.
