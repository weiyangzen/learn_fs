# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_group.c

## Purpose

`rcar_du_group.c` manages DU semi-global resources shared by one or two CRTCs: extended feature registers, pin/output routing, dot-clock routing, plane/timing associations, group start/stop/restart, DPAD levels, and Gen2/Gen3 VSP/DPAD routing.

## Important APIs, Types, and Functions

- `rcar_du_group_read()` and `rcar_du_group_write()` access group-relative registers.
- Setup helpers program pins (`DEFR6`), output/VSP routing (`DEFR8`), dot-clock routing (`DIDSR`), extended feature registers, CMM enable bits, DORCR, and DPTSR.
- `rcar_du_group_get()` initializes group registers on first use and increments `use_count`; `rcar_du_group_put()` decrements it.
- `rcar_du_group_start_stop()` tracks active CRTCs and starts/stops or restarts the hardware group as needed.
- `rcar_du_group_restart()` toggles reset/start for configuration changes requiring DRES.
- `rcar_du_set_dpad0_vsp1_routing()` updates DEFR8 with temporary clock enable for routes that can be changed while CRTCs are disabled.
- `rcar_du_group_set_routing()` programs DPAD1 source, fixed DPAD output levels, and DPAD0/VSP1 routing.

## Control Flow

The first CRTC to get a group triggers `rcar_du_group_setup()`, which programs generation-specific extended features, CMM routing, dot-clock routing, default plane priorities, and DPTSR. Starting a CRTC increments `used_crtcs`; if another CRTC is already active, the group is briefly stopped before restart because some bits only latch during reset. Stopping decrements `used_crtcs` and stops hardware only when the last CRTC stops.

Routing updates are called during CRTC setup/start. DPAD1 routing is set through DORCR, DPAD pins not currently driven by outputs are forced low through DOFLR, and DPAD0/VSP1 routing is applied through DEFR8 with special Gen2/Gen3 placement rules.

## State and Persistence Behavior

Persistent group state includes `use_count`, `used_crtcs`, `dptsr_planes`, `need_restart`, and generation/channel/CMM masks. Hardware state persists in group registers controlling extended features, CMM routing, dot-clock selection, plane priority/association, DPAD output levels, and start/reset bits.

## Dependencies and Integration Points

- Uses CRTC DSYSR helper, driver SoC info, register definitions, clocks, and group mutex.
- Called by CRTC setup/update paths and plane code when VSP1 sink changes.

## Risks and Edge Cases

- `rcar_du_group_put()` blindly decrements `use_count`; imbalance can underflow.
- Group restart causes visible flicker, and many routing/plane association changes still require it.
- Gen2/Gen3 routing rules are highly SoC-specific; wrong `dpad0_source`, `dpad1_source`, or `vspd1_sink` values program invalid routes.
- `rcar_du_set_dpad0_vsp1_routing()` enables a CRTC clock temporarily and assumes the selected CRTC exists for the group index.

## Test Signals

- Multi-CRTC tests should verify `used_crtcs` start/stop behavior and flicker-causing restart cases.
- Route tests should cover DPAD0/DPAD1, VSP1D to DU0/1/2, Gen2 versus Gen3 DEFR8 behavior, and single-channel Gen3/Gen4 groups.
- Plane association tests should inspect DPTSR and DS1PR/DS2PR after source/CRTC changes.
