# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_main.c

## Purpose

This is the primary DSA switch driver for NXP SJA1105/SJA1110 devices. It owns probe/remove/shutdown, device-tree parsing, static configuration construction and reload, DSA operation callbacks, bridge/VLAN/FDB/MDB/flooding/STP integration, phylink integration, management-route TX, MTU/policer/CBS/mirror support, and subsystem bring-up/teardown for TAS, flower, PTP, MDIO, devlink, and tag_8021q.

## Important APIs, Types, and Data

Important externally wired functions include `sja1105_setup()`, `sja1105_teardown()`, `sja1105_static_config_reload()`, `sja1105_vlan_filtering()`, FDB/MDB/VLAN callbacks, bridge callbacks, timestamp callbacks, tc callbacks, and the SPI driver `sja1105_probe()`.

Key helper groups:

- Static config builders: `sja1105_init_mac_settings()`, `sja1105_init_mii_settings()`, `sja1105_init_static_fdb()`, `sja1105_init_static_vlan()`, `sja1105_init_l2_lookup_params()`, `sja1105_init_l2_forwarding()`, `sja1110_init_pcp_remapping()`, `sja1105_init_l2_forwarding_params()`, `sja1105_init_l2_policing()`, `sja1105_init_general_params()`, and `sja1105_init_avb_params()`.
- Runtime dynamic config users: `sja1105_drop_untagged()`, `sja1105_pvid_apply()`, `sja1105_set_port_speed()`, FDB add/delete implementations, flood-domain management, VLAN add/delete, bridge membership/STP changes, CBS shaper programming, mirror programming, multicast flood handling, and management-route TX.
- Reset/reload: `sja1105_static_config_reload()` preserves phylink speed replay, serializes with FDB and management TX, locks PTP, snapshots PHC time, uploads static config, restores PTP time, redoes clocking, and reloads CBS.
- Probe/device model: `sja1105_probe()` resets hardware, configures SPI limits, verifies device ID and part number, allocates `dsa_switch`, initializes locks, parses DT ports and RGMII delays, allocates CBS state, and registers the DSA switch.

## Control Flow

Probe requires an OF node, optionally toggles reset GPIO, sets up 8-bit SPI, calculates `priv->max_xfer_len` from controller limits, selects match data, verifies actual device ID/part number, allocates DSA state, initializes locks, parses port PHY modes/fixed links/RGMII delays, optionally allocates CBS state, and calls `dsa_register_switch()`.

DSA setup disables the SJA1110 microcontroller if required, constructs and uploads the static config, programs clocking, sets up TAS and flower state, registers the PTP clock, registers MDIO buses, sets up devlink, registers tag_8021q, and advertises DSA capabilities. Failure unwinds in reverse order.

Static config construction builds every hardware table from topology and defaults. User ports start disabled for ingress/egress/learning until STP state enables them. CPU/DSA ports drop untagged frames. Forwarding matrices initially connect user ports to CPU/DSA ports and CPU/DSA ports to all enabled ports, with special handling for H topologies. VLAN setup creates a default management VLAN. L2 policing initializes per-port shared policers and match lookup indirection.

Bridge and VLAN operations mutate software tables and push dynamic table updates where possible. VLAN filtering changes TPID values in general params and therefore needs a full static reload. VLAN membership changes use dynamic VLAN lookup writes. PVID changes update MAC config dynamically and may enable dropping untagged traffic depending on bridge VLAN membership, tag_8021q mode, and CPU/DSA role.

FDB operations differ by generation. E/T uses a CRC-selected four-way bin; P/Q/R/S/SJA1110 use hardware search and then linear probing for empty entries. Static FDB additions are mirrored into `priv->static_config` to survive resets. Dumps iterate all 1024 entries, filter by port, hide DSA tag VLANs, and skip multicast for FDB display. Fast-age scans dynamic entries and deletes unlocked entries for a port.

Management TX installs a management route with destination MAC/port, enqueues the skb through DSA, polls for hardware to clear the enforce/ack bit, optionally cleans the route, and hands TX timestamp clones to PTP. Deferred kthread work is required because SPI sleeps.

## State and Persistence Behavior

The driver keeps `priv->static_config` as the durable software mirror for hardware state that must survive switch resets. Runtime operations usually update this mirror before or while issuing dynamic writes. Full reloads reset the switch and reupload the mirror, then replay phylink link state and dynamic CBS shapers.

Other important state includes `bridge_pvid[]`, `tag_8021q_pvid[]`, `ucast_egress_floods`, `bcast_egress_floods`, `priv->cbs`, `flow_block` rule/policer state, PTP data, PCS pointers, MDIO bus pointers, and hardware timestamp enable bitmaps. Locks divide state domains: `fdb_lock` protects FDB/static reload interactions, `mgmt_lock` protects management route TX and reload, `dynamic_config_lock` serializes dynamic SPI table commands, `ptp_data.lock` serializes PHC operations, and `ts_id_lock` protects SJA1110 TX timestamp IDs.

## Dependencies and Integration Points

The file integrates with Linux SPI, GPIO reset, OF/MDIO/phylink, DSA, switchdev, bridge VLAN/FDB/MDB, tc qdisc/classifier offload, PTP, devlink, and tag_8021q. Internal dependencies include dynamic config, static config packing/upload, SPI register helpers, clocking, TAS, flower, VL, MDIO, PTP, devlink, and the SJA1105/SJA1110 tagging protocol.

## Risks and Edge Cases

- Many user-visible changes require switch reset because not all tables are dynamically writable. Reload must preserve PTP time and replay link state or traffic/timestamping can glitch.
- Static and dynamic state must stay synchronized. Updating hardware without updating `priv->static_config` will be lost on reload; updating the mirror without a successful dynamic write creates software/hardware divergence until reset.
- FDB add on E/T has collision eviction behavior when a bin is full; P/Q/R/S linear empty-entry search is expensive and can fail when full.
- `sja1105et_fdb_add()` computes an `index` before assigning `way = last_unused` in one branch, but the later write uses the recomputed `l2_lookup.index`; eviction logging and invalidation paths are the important behavior to watch.
- Only one VLAN-aware bridge is supported, 8021q uppers are rejected, and DSA tag VLAN range 3072-4095 is reserved.
- Management route TX has a short polling timeout and route cleanup is not supported on all generations.
- H-topology forwarding cuts are topology-sensitive and prevent loops by reducing DSA-to-CPU reachability.
- RGMII delay parsing supports legacy behavior for fixed links but warns that DT should use explicit delay properties.

## Test Signals

Probe should log the detected chip and successfully register DSA ports. Functional signals include phylink link-up/down changing speed and TX inhibit state, bridge join/leave altering forwarding, STP states controlling ingress/egress/learning, VLAN add/delete and filtering behavior, FDB/MDB add/delete/dump correctness, fast-age clearing dynamic entries, tag_8021q VLAN isolation, management frames and PTP traffic reaching intended ports, MTU/policer/CBS/mirror/tc offloads applying, and successful teardown without leaked MDIO/PTP/flower/TAS state. Reload paths should log a reset reason and preserve PHC continuity.
