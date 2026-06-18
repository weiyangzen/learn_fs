# sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx.c

## Purpose
This file is the DSA MDIO driver for the MaxLinear MxL862xx switch family. It registers an MDIO-backed `dsa_switch`, wraps the firmware command interface through `mxl862xx_api_wrap()`, sets up the internal PHY MDIO relay, programs bridge and VLAN forwarding resources, implements FDB/MDB/STP/bridge flag callbacks, and exposes ethtool and `rtnl_link_stats64` statistics.

## Important APIs, Types, and Functions
- `MXL862XX_API_READ`, `MXL862XX_API_WRITE`, and `MXL862XX_API_READ_QUIET` are local convenience wrappers over firmware commands defined in the companion API headers.
- `mxl862xx_get_tag_protocol()` always returns `DSA_TAG_PROTO_MXL862`, tying the driver to the MxL862 DSA tagger.
- `mxl862xx_phy_read_mmd()` and `mxl862xx_phy_write_mmd()` implement firmware-relayed internal PHY access and are exposed through the `mii_bus` hooks in `mxl862xx_setup_mdio()`.
- `mxl862xx_wait_ready()` polls firmware version and common config reads after reset.
- `mxl862xx_setup()` performs firmware reset/readiness, calculates per-port EVLAN/VLAN-filter table budgets, installs the shared drop meter, starts stats polling, and registers the internal MDIO bus.
- `mxl862xx_port_setup()` disables and flushes a port, configures service-port tagging and CTP assignment, creates standalone bridge/FID state for user ports, and allocates per-port ingress EVLAN, egress EVLAN, and VLAN Filter blocks.
- VLAN handling is split among `mxl862xx_vf_*()` helpers for membership filtering, `mxl862xx_evlan_*()` helpers for tag insertion/removal/PVID behavior, and DSA callbacks `mxl862xx_port_vlan_filtering()`, `mxl862xx_port_vlan_add()`, and `mxl862xx_port_vlan_del()`.
- Bridge behavior is implemented by `mxl862xx_allocate_bridge()`, `mxl862xx_free_bridge()`, `mxl862xx_sync_bridge_members()`, `mxl862xx_set_bridge_port()`, `mxl862xx_port_bridge_join()`, and `mxl862xx_port_bridge_leave()`.
- FDB and MDB callbacks program firmware MAC table entries through `MXL862XX_MAC_TABLEENTRY*` commands.
- Statistics come from `mxl862xx_read_rmon()`, ethtool callbacks, periodic `mxl862xx_stats_poll()`, and `mxl862xx_get_stats64()`.
- Driver lifecycle is `mxl862xx_probe()`, `mxl862xx_remove()`, `mxl862xx_shutdown()`, and the `mdio_driver`/OF match table.

## Control Flow
Probe allocates `mxl862xx_priv` and `dsa_switch`, initializes host transport state with `mxl862xx_host_init()`, initializes per-port work and stats locks, and calls `dsa_register_switch()`. DSA then calls `mxl862xx_setup()`, which resets the chip, waits for firmware, sizes hardware VLAN resources based on user-port count, sets up a zero-rate drop meter, starts delayed stats polling, and registers the child MDIO bus.

Per-port setup first disables DMA paths and flushes MAC learning. CPU ports enable service-port tagging and are assigned to the default bridge. User ports get an individual firmware bridge for standalone operation, initially block unknown unicast/multicast host flooding while allowing broadcast, then allocate ingress EVLAN, egress EVLAN, and VLAN Filter blocks.

Bridge join allocates one firmware bridge per DSA bridge number if needed, then reprograms all current bridge members. `mxl862xx_set_bridge_port()` is the main convergence point: it builds the bridge port map, assigns the correct bridge/FID, applies learning and flood-block meter state, enables EVLAN/VF blocks when applicable, and switches between IVL/SVL by setting VLAN-based MAC learning flags.

VLAN-aware ingress uses fixed final EVLAN rules that insert the PVID for untagged/priority-tagged traffic, pass standard 802.1Q VID>0 traffic to VLAN Filter membership checks, and treats non-802.1Q TPIDs as untagged. Egress EVLAN rules are created only for untagged VIDs that need tag stripping. VLAN Filter entries track allowed VIDs per port and use a discard sentinel at index 0 when the active scan window would otherwise be empty.

Remove and shutdown stop delayed stats work, unregister or shut down DSA, shut down the host transport, and cancel deferred host-flood work. Port teardown only marks `setup_done = false`; EVLAN/VF firmware resources are reclaimed by firmware reset on next probe rather than freed individually.

## State and Persistence Behavior
The driver persists runtime state in `struct mxl862xx_priv` and `struct mxl862xx_port`. Per-port state includes standalone FID, flood-block bitmask, learning flag, setup guard, PVID, VLAN filtering mode, allocated VF/EVLAN block IDs, desired host flooding, deferred work, and accumulated stats. Bridge IDs are cached in `priv->bridges[]` by DSA bridge number. Hardware tables and meters persist in firmware until reset; software does not reconstruct them from persistent storage.

Stats are accumulated in software because RMON packet counters are 32-bit free-running values. `mxl862xx_stats_poll()` computes deltas against previous snapshots, handles 32-bit wrap with unsigned subtraction, and stores 64-bit accumulators under `stats_lock`. `MXL862XX_FLAG_WORK_STOPPED` prevents delayed work rescheduling during teardown.

Host flood changes are special because DSA may call `port_set_host_flood` under `netif_addr_lock`. The driver records the desired state and schedules `host_flood_work`, which takes RTNL, verifies `setup_done`, and writes firmware bridge forwarding configuration for the standalone FID.

## Dependencies and Integration Points
The file depends on Linux DSA, phylink, OF MDIO, bridge switchdev flags, ethtool stats APIs, and the companion MxL862xx firmware transport/API headers: `mxl862xx-api.h`, `mxl862xx-cmd.h`, and `mxl862xx-host.h`. It integrates with the DSA tagger via `DSA_TAG_PROTO_MXL862`, with internal PHYs via a child `mdio` node, and with firmware command structures whose fields require explicit CPU/little-endian conversions.

## Risks and Edge Cases
- EVLAN rule order is critical. The standard 802.1Q accept rules must precede broad `NO_FILTER` catchalls or valid tagged frames could be stripped or rewritten.
- VLAN resource sizing divides global EVLAN/VF tables among user ports. Large VLAN deployments can hit `-ENOSPC`, especially for untagged egress VIDs that consume EVLAN entries.
- Rollback after VLAN add/delete errors is best effort. The code restores software state and reprograms blocks, but there is no true firmware transaction.
- The shared zero-rate drop meter relies on direct register modification after firmware allocation to eliminate an initial bucket leak.
- `mxl862xx_vf_del_vid()` swaps the last active VF entry into a removed entry's gap; correctness depends on list/index consistency.
- Host flood work can race with teardown unless `setup_done` and RTNL ordering are preserved.
- FID allocation failures or partial port setup may leak firmware bridges until reset, which the code comments treat as tolerable.
- `mxl862xx_get_stats64()` returns accumulated values and schedules an immediate poll for freshness, so the current call may lag hardware by up to the poll interval.

## Test Signals
Useful test coverage would include module probe/remove/shutdown, child MDIO scan and PHY reads, DSA bridge join/leave with multiple bridges, standalone flooding behavior, bridge flags for learning and unknown UC/MC/broadcast flooding, VLAN-aware and VLAN-unaware traffic with PVID/untagged/tagged combinations, FDB/MDB add/delete/dump, STP state transitions with learning reapplication, RMON wraparound behavior, ethtool stat mapping, and fault injection for firmware command failures during VLAN add/delete rollback.
