# sources/distributed-fs/ceph-client/drivers/bus/omap-ocp2scp.c

## Purpose
This small platform bus driver enables TI OMAP OCP-to-SCP bridge nodes, populates their child devices, and applies a hardware timing workaround for non-AM437x variants. The bridge translates OCP accesses to SCP protocol for child PHY-like devices.

## Important APIs, Types, and Functions
`omap_ocp2scp_probe()` is the only substantive path. It calls `of_platform_populate()` for children, enables runtime PM on the bridge, maps the first MMIO resource when the timing workaround applies, and writes the `OCP2SCP_TIMING` register `SYNC2` field to `0x6`. `omap_ocp2scp_remove()` disables runtime PM and depopulates children. The OF match table recognizes `ti,omap-ocp2scp` and `ti,am437x-ocp2scp`.

## Control Flow
Probe first populates child resources from the bridge node. After `pm_runtime_enable()`, non-AM437x hardware gets a runtime PM get, a read-modify-write of `OCP2SCP_TIMING`, and a runtime PM put. Error unwinding disables runtime PM and depopulates children if mapping fails. AM437x skips the timing write entirely.

## State and Persistence
The driver has no private state. The only persistent hardware change is the `SYNC2` timing field, which remains programmed until reset or power-domain loss. Runtime PM state is owned by the core.

## Dependencies and Integration Points
It depends on OF child population, platform resources, MMIO accessors, and runtime PM. Its main integration point is child platform devices that sit behind the OCP2SCP bridge.

## Risks and Test Signals
The main risk is ordering: children are populated before the timing workaround, so early child access would depend on probe ordering and PM behavior. Missing MMIO resources on non-AM437x devices fail probe. Test signals include successful child device probing, absence of read-path errors on OMAP4/5/AM57xx, and runtime PM balance during probe/remove.
