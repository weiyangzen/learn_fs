<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx8m-blk-ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx8m-blk-ctrl.c

## Purpose

`imx8m-blk-ctrl.c` implements i.MX8M block-control PM-domain providers for VPU, display, and media blocks. These domains sequence block resets, clocks, upstream GPC domains, bus domains, ICC paths, and notifier workarounds that cannot be expressed as plain genpd hierarchy.

## Important APIs, types, and functions

`struct imx8m_blk_ctrl` stores provider state, bus power-domain device, regmap, notifier, domain array, and onecell data. `struct imx8m_blk_ctrl_domain_data` describes clocks, ICC paths, upstream GPC name, reset mask, clock mask, and MIPI PHY reset mask. `imx8m_blk_ctrl_power_on/off()` implement sequencing. Several notifiers handle VPU, display, and media ADB/QoS quirks.

## Control flow

Probe maps registers, attaches the `bus` power domain, allocates one genpd per table entry, gets clocks and optional ICC paths, attaches named upstream GPC domains, initializes genpds as off with a special lock class, registers a onecell provider, registers a bus-domain notifier, and populates child devices. Power callbacks use runtime PM to drive upstream domains in the required sequence.

## State and persistence behavior

State persists in `BLK_SFT_RSTN`, `BLK_CLK_EN`, optional `BLK_MIPI_RESET_DIV`, VPU fuse-like registers, media/display QoS/cache registers, upstream GPC domain state, clocks, and ICC settings.

## Dependencies and integration points

The driver depends on genpd, runtime PM, regmap, clocks, ICC, OF platform population, and i.MX8M power binding IDs. It expects named power domains such as `bus`, `g1`, `g2`, `lcdif`, `mipi-csi`, and `isp`.

## Risks and edge cases

The runtime PM based hierarchy is deliberate, not accidental. Missing notifiers can hang ADB handshakes, absent ICC paths are tolerated except deferral, i.MX8MQ VPU reset masks are deliberately omitted to avoid hangs, and partial-probe cleanup must detach only initialized domains.

## Test signals

Validate each compatible, named domain attachment, onecell indexes, clock/ICC acquisition, notifier behavior, VPU fuse programming, media/display QoS, MIPI PHY reset bits, i.MX8MQ VPU reset avoidance, runtime PM on/off, system suspend/resume balance, and lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx8m-blk-ctrl.c -->
