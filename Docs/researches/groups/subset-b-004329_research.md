# subset-b-004329 research

Grouped research for the SJA1105 DSA driver files listed in work item `subset-b-004329`. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_dynamic_config.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_dynamic_config.c

## Purpose

This file implements the dynamic configuration interface for NXP SJA1105/SJA1110 Ethernet switches. Static configuration tables are normally uploaded as an all-at-once switch image, but several tables expose a register-like dynamic view that can be read, written, searched, or invalidated without resetting the switch. The file builds a per-family `struct sja1105_dynamic_table_ops` table and exposes the common runtime APIs `sja1105_dynamic_config_read()` and `sja1105_dynamic_config_write()`.

The driver treats a dynamic transaction as a packed compound buffer: an entry area followed by a 32-bit command area. Different switch generations put fields in different places, sometimes overlapping command and entry data. This file centralizes those packing quirks so higher-level paths in `sja1105_main.c`, `sja1105_ptp.c`, flower offload, VLAN, FDB, mirroring, CBS, and management-route TX can operate in terms of normal C table entries.

## Important APIs, Types, and Data

- `struct sja1105_dyn_cmd` is the internal command model. It carries `valid`, `rdwrset`, `errors`, `valident`, `index`, and the software-only `search` flag used to select HOSTCMD search behavior on P/Q/R/S/SJA1110.
- `enum sja1105_hostcmd` maps the generic read/write/delete/search model into the second/third-generation L2 lookup HOSTCMD field.
- `sja1105et_dyn_ops`, `sja1105pqrs_dyn_ops`, and `sja1110_dyn_ops` are the exported operation tables indexed by `enum sja1105_blk_idx`. Each row defines command packing, entry packing, access flags, entry limit, packed size, and base SPI address for one dynamic block.
- `sja1105_dynamic_config_read()` validates the block/index/access mode, packs a read or search command, optionally packs the search key into the entry buffer, writes the command via SPI, waits for completion, and unpacks the resulting entry.
- `sja1105_dynamic_config_write()` validates write/delete support, packs a write or invalidate command, optionally packs the entry, writes it via SPI, and polls for completion/error status.
- `sja1105et_fdb_hash()` implements the first-generation FDB bin hash over VID and MAC address using the configured L2 lookup polynomial.

The command/entry packers cover virtual link lookup/policing, L2 lookup and management routes, VLAN lookup, L2 forwarding, MAC configuration, L2 lookup/general/AVB parameters, retagging, CBS, SJA1110 xMII params, L2 policing, and L2 forwarding params.

## Control Flow

The common read path checks `blk_idx`, `ops->max_entry_count`, `OP_SEARCH`, `OP_READ`, buffer size, and packing callbacks. It sets `cmd.valid`, `cmd.rdwrset = SPI_READ`, chooses either a numeric index or search command, sets `cmd.valident`, packs the command, and packs the entry only for searches. It holds `priv->dynamic_config_lock` around the SPI command and completion poll. Completion polling reads back the same dynamic buffer, unpacks the command, waits until hardware clears VALID, checks VALIDENT unless `OP_VALID_ANYWAY` is set, and unpacks the entry if requested.

The write path is similar but requires `OP_WRITE`, rejects negative indexes, and requires `OP_DEL` when `keep == false`. It sets `cmd.valident = keep`, packs the command before packing the entry, and skips entry packing for pure invalidation. Completion checks hardware error bits but does not require VALIDENT.

Several packers deliberately violate a clean command/entry split because the hardware layout does. L2 lookup indexes are physically stored in entry fields on some generations, VLAN indexes are the VLAN ID field, SJA1110 VLAN validity is inferred from `TYPE_ENTRY`, and `lockeds` is read from command writeback but belongs semantically to the FDB entry. Management route packers reuse L2 lookup command layouts while forcing the management-route bit.

## State and Persistence Behavior

Dynamic writes immediately modify switch hardware and are also generally made against entries stored in `priv->static_config` by callers. That dual update is essential because `sja1105_static_config_reload()` resets and reuploads the static image, so runtime FDB/VLAN/MAC/CBS/flooding/mirroring state must be replayable from software. This file itself does not persist state beyond the stack transaction buffer; it enforces serialized hardware access through `priv->dynamic_config_lock`.

`sja1105et_fdb_hash()` depends on the current static L2 lookup params table, so changes to the polynomial affect the bin selected for first-generation FDB operations.

## Dependencies and Integration Points

The implementation depends on `sja1105_packing()`, `sja1105_pack()`, and `sja1105_unpack()` from the local packing infrastructure, static table entry packers from `sja1105_static_config.c`, SPI transfer helpers from `sja1105_spi.c`, Linux `read_poll_timeout()`, and `priv->info->dyn_ops` selected in `sja1105_spi.c` chip info tables. The exported dynamic ops arrays are referenced by `struct sja1105_info`.

Important consumers include FDB add/delete/dump and fast-age, VLAN add/delete, bridge forwarding/flood changes, MAC speed/STP/PVID/drop settings, CBS offload, mirror config, management routes for control-packet TX, PTP AVB parameter changes, and SJA1110 dynamic table operations.

## Risks and Edge Cases

- The hardware layouts are generation-specific and sometimes contradictory; the packers contain several intentional hacks. A bitfield mistake can silently corrupt hardware table entries.
- `SJA1105_MAX_DYN_CMD_SIZE` must remain large enough for all `packed_size` values; both public paths reject oversized ops, but adding new tables requires care.
- Some operations report missing entries via VALIDENT while others legitimately lack it and require `OP_VALID_ANYWAY`; wrong access flags can turn valid reads into `-ENOENT` or hide missing entries.
- Search is only supported where `OP_SEARCH` is set; callers using `SJA1105_SEARCH` with unsupported tables receive `-EOPNOTSUPP`.
- Dynamic transactions are serialized only by `dynamic_config_lock`; callers that also mutate `priv->static_config` need their own higher-level locks such as `fdb_lock` or `mgmt_lock`.
- First-generation FDB bin handling relies on the configured CRC polynomial and four-way bin semantics, so changing L2 lookup params can alter FDB placement.

## Test Signals

Useful validation signals include successful probe/static upload followed by dynamic VLAN/FDB/bridge operations, `bridge fdb show` traversing entries without SPI errors, `bridge vlan` add/delete reflecting in traffic behavior, CBS/mirror/tc-flower offloads returning success and affecting forwarding, management-route control packets leaving expected ports, and absence of `-EAGAIN` timeout, `-EINVAL` hardware error, or `-ENOENT` surprises during dynamic reads. Tests should cover E/T, P/Q/R/S, and SJA1110 because command packing and access flags differ materially.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_dynamic_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_dynamic_config.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_dynamic_config.h

## Purpose

This header declares the dynamic configuration contract shared by the SJA1105 driver. It exposes the table-operation descriptor used by `sja1105_dynamic_config.c`, the management-route entry format consumed by control-packet TX, the special search index, and the per-generation dynamic ops arrays selected by chip metadata.

## Important APIs, Types, and Data

- `SJA1105_SEARCH` is `-1` and is passed as the index to `sja1105_dynamic_config_read()` for hardware-assisted lookup on tables with search support.
- `struct sja1105_dyn_cmd` is forward-declared so command packing callbacks can accept it without exposing internal fields to all users.
- `struct sja1105_dynamic_table_ops` defines `entry_packing`, `cmd_packing`, `max_entry_count`, `packed_size`, `addr`, and `access`. This is the core ABI between the chip info table and the generic dynamic read/write helpers.
- `struct sja1105_mgmt_entry` models management-route entries with timestamp selection, destination MAC, destination ports, enforce/ack flag, and index.
- `sja1105et_dyn_ops`, `sja1105pqrs_dyn_ops`, and `sja1110_dyn_ops` are declared for use in `struct sja1105_info`.

## Control Flow

The header itself has no runtime control flow. At probe, chip identification selects a `struct sja1105_info`, whose `dyn_ops` pointer references one of the arrays declared here. Runtime code then passes block indexes to the generic dynamic helpers, which dispatch through the `entry_packing` and `cmd_packing` callbacks stored in `struct sja1105_dynamic_table_ops`.

## State and Persistence Behavior

No storage is allocated here. The important persistence implication is structural: `struct sja1105_dynamic_table_ops` describes the hardware address and packing used to modify live switch state, while callers typically keep a matching copy in `priv->static_config` for replay across static config reloads.

## Dependencies and Integration Points

The header includes `sja1105.h` for block indexes and driver core types, and `<linux/packing.h>` for `enum packing_op`. It is consumed by dynamic config implementation and all files that need access to `SJA1105_SEARCH`, management routes, or the dynamic ops arrays via chip info.

## Risks and Edge Cases

- `entry_packing` returns `size_t` only for prototype compatibility with static table packers; callers should not rely on meaningful return values for every dynamic packer.
- `addr` is the lowest SPI address for the compound entry/command buffer, not necessarily the command word address.
- `access` is a compact flag byte whose bit definitions are private to the C file; adding external users would require keeping those semantics synchronized.

## Test Signals

Build coverage is the main signal for this header: all dynamic config users should compile with the callback prototypes, and chip info tables should resolve all three exported ops arrays. Runtime test signals are inherited from dynamic read/write users such as FDB, VLAN, MAC config, and management-route TX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_dynamic_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_ethtool.c

## Purpose

This file implements ethtool statistics support for SJA1105/SJA1110 switch ports. It maps hardware diagnostic counter registers into DSA ethtool string, count, and value callbacks. First-generation E/T devices expose MAC and high-level counters, while later devices add Ethernet statistics.

## Important APIs, Types, and Data

- `enum sja1105_counter_index` gives stable array indexes for MAC, high-level 1, high-level 2, and P/Q/R/S-only ETHER counters.
- `struct sja1105_port_counter` describes one exported counter: stats area, ethtool name, register offset, bit range, and whether the counter spans 64 bits.
- `sja1105_port_counters[]` is the central hardware-to-ethtool mapping.
- `sja1105_port_counter_read()` reads the relevant register area through SPI and unpacks the requested bitfield.
- `sja1105_get_ethtool_stats()`, `sja1105_get_strings()`, and `sja1105_get_sset_count()` are wired into `dsa_switch_ops`.

## Control Flow

The DSA ethtool callbacks choose a maximum counter index based on `priv->info->device_id`: E/T stops at `__MAX_SJA1105ET_PORT_COUNTER`; all other supported chips use `__MAX_SJA1105PQRS_PORT_COUNTER`. Empty names are skipped, allowing sparse enum positions. Stats reading loops through the selected counters, calls `sja1105_port_counter_read()`, and fills the output array in the same order as `get_strings()` and `get_sset_count()`.

The low-level read computes the base register from `priv->info->regs->stats[c->area][port]`, adds the counter offset, reads 4 or 8 bytes with `sja1105_xfer_buf()`, and unpacks the configured bit range into a 64-bit value.

## State and Persistence Behavior

This file has no persistent software state. It reads hardware counters in place and reports the current values. It does not clear counters, cache values, or preserve values across switch reset; reset behavior is entirely determined by hardware.

## Dependencies and Integration Points

The code depends on register base arrays in `struct sja1105_regs`, SPI helper `sja1105_xfer_buf()`, and packing helper `sja1105_unpack()`. It integrates with DSA through `.get_ethtool_stats`, `.get_strings`, and `.get_sset_count` in `sja1105_main.c`.

## Risks and Edge Cases

- Counter layout differs by generation; using the wrong max counter limit or register map would expose invalid names or read reserved locations.
- Some counters are subfields within one 32-bit word; incorrect start/end bits would produce plausible but wrong values.
- The stats loop logs and stops at the first SPI read error, leaving later output entries unchanged by this callback.
- 64-bit counters require an 8-byte SPI read, so SPI master transfer limits and chunking must support that path.

## Test Signals

`ethtool -S <port>` should show the same number and order of names as `get_sset_count()` reports. On E/T, ETHER-only counters should be absent; on P/Q/R/S/SJA1110 they should be present. Traffic generation should increment RX/TX frame and byte counters, while error injection or VLAN drops should move the corresponding diagnostic counters. SPI failures should produce a driver error message and not crash the stats path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_flower.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_flower.c

## Purpose

This file implements tc-flower classifier offload for the SJA1105 driver. It supports a narrow key/action subset that maps onto hardware L2 policing and virtual-link machinery: broadcast policers, PCP-based traffic-class policers, virtual-link redirect/trap/drop, and gate actions.

## Important APIs, Types, and Data

- `sja1105_rule_find()` searches `priv->flow_block.rules` by flower cookie and is shared with deletion/statistics paths.
- `sja1105_find_free_l2_policer()` scans `priv->flow_block.l2_policer_used` for a dynamic policer slot.
- `sja1105_setup_bcast_policer()` and `sja1105_setup_tc_policer()` allocate/update shared L2 policer entries and reload best-effort policing.
- `sja1105_flower_parse_key()` validates supported dissector keys and maps them into `struct sja1105_key` variants.
- `sja1105_policer_validate()` constrains police actions to the hardware-supported form.
- `sja1105_cls_flower_add()`, `sja1105_cls_flower_del()`, and `sja1105_cls_flower_stats()` are DSA classifier callbacks.
- `sja1105_flower_setup()` and `sja1105_flower_teardown()` initialize and free the rule list.

## Control Flow

Add starts by parsing keys. Unsupported dissector keys, control flags, source MAC matching, masked destination MAC matching, partial VID/PCP masks, protocol matching, or unknown key combinations are rejected with extack messages. Supported keys become broadcast, PCP traffic class, VLAN-aware virtual link, or VLAN-unaware virtual link keys.

The action loop handles `FLOW_ACTION_POLICE`, `TRAP`, `REDIRECT`, `DROP`, and `GATE`. Police actions validate conform/exceed behavior and unsupported rate fields, then install either a broadcast or TC policer. Redirect/trap/drop/gate delegate to `sja1105_vl_redirect()` or `sja1105_vl_gate()`. If a gate was requested, a redirect/trap must also be present so `DESTPORTS` is populated before scheduling is initialized. Virtual-link actions finish by reloading static config for `SJA1105_VIRTUAL_LINKS`.

Delete looks up the cookie. VL rules are delegated to `sja1105_vl_delete()`. Policer rules restore affected lookup entries to their per-port default `sharindx`, clear the port bit from the rule, free the dynamic policer if no ports remain, and reload best-effort policing. Stats are only meaningful for VL rules and use `sja1105_vl_stats()`.

## State and Persistence Behavior

Rules are stored in `priv->flow_block.rules`, and allocated dynamic policers are tracked in `priv->flow_block.l2_policer_used`. The actual policer configuration is written into `priv->static_config.tables[BLK_IDX_L2_POLICING].entries`; virtual-link helpers similarly mutate static tables. Because changes are committed through `sja1105_static_config_reload()`, they persist across the reset that reload itself performs, and the software copies remain authoritative for later reloads.

## Dependencies and Integration Points

The file depends on Linux flow dissector/action APIs, DSA classifier hooks, `sja1105_vl.*` helpers, `sja1105_static_config_reload()`, and the L2 policing table layout initialized in `sja1105_main.c`. It uses extack for user-facing rejection reasons and is wired into `.cls_flower_add`, `.cls_flower_del`, and `.cls_flower_stats`.

## Risks and Edge Cases

- Only exact supported key combinations work; broad flower rules can fail with `-EOPNOTSUPP`.
- Policer allocation is finite. The first `ds->num_ports` policers are reserved for matchall/per-port defaults, leaving the rest for flower.
- Updating a rule that spans multiple ports shares one policer index across those ports. Delete must carefully restore only the removed port and free the policer only when `port_mask` becomes zero.
- `sja1105_static_config_reload()` resets the switch, so active traffic and PTP/TAS state depend on reload preservation logic.
- Gate action without redirect/trap is explicitly rejected because scheduling needs a destination port mask.
- The code assumes static policing entries have their default `sharindx == port` when checking whether a port already has a broadcast or TC policer.

## Test Signals

Useful tests include tc flower police rules for broadcast DMAC and VLAN PCP, rejection of unsupported masks/actions with extack text, redirect/trap/drop virtual-link offloads with traffic verification, gate plus redirect/trap scheduling behavior, deleting shared policers from one of multiple ports, and `tc -s filter show` stats for VL rules. Static config reload messages after policer/VL changes are expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_flower.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_main.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_mdio.c

## Purpose

This file exposes several SPI-backed MDIO buses for SJA1105/SJA1110 hardware blocks. It lets phylink and the XPCS library access internal PCS blocks through Clause 45 MDIO operations and lets device-tree-described SJA1110 internal 100base-TX and 100base-T1 PHY buses be registered as Linux `mii_bus` instances.

## Important APIs, Types, and Data

- `sja1105_pcs_mdio_read_c45()` and `sja1105_pcs_mdio_write_c45()` implement direct C45 PCS accesses for SJA1105R/S-style PCS blocks.
- `sja1110_pcs_mdio_read_c45()` and `sja1110_pcs_mdio_write_c45()` implement SJA1110 PCS access through a bank register plus an 8-bit offset.
- `sja1105_base_t1_mdio_read_c22/write_c22` and `read_c45/write_c45` expose SJA1110 100base-T1 internal PHY MDIO windows.
- `sja1105_base_tx_mdio_read/write` expose SJA1110 100base-TX internal PHY registers.
- `sja1105_mdiobus_register()` registers PCS, base-TX, and base-T1 buses as available; `sja1105_mdiobus_unregister()` tears them down.
- `sja1105_mdiobus_pcs_register()` creates XPCS phylink PCS objects for SGMII/2500base-X ports.

## Control Flow

PCS C45 reads/writes encode `(mmd << 16) | reg`. Older PCS access only supports vendor MMDs and synthesizes PHY ID values for `MDIO_MMD_VEND2` ID registers. SJA1110 PCS access first checks `regs->pcs_base[phy]`, synthesizes PHY IDs, writes the bank portion to a dedicated bank register, then reads/writes the selected offset. Offset `0xff` is reserved and rejected.

100base-T1 access builds an SPI address from the internal MDIO base, PHY address, opcode, and xad/register field. Clause 45 reads/writes first write the target register address through `SJA1105_C45_ADDR`, then transfer data through `SJA1105_C45_DATA`. Clause 22 uses the register number directly. 100base-TX access is a simpler base-plus-register SPI window.

Registration first creates the PCS bus if chip info provides PCS callbacks. It masks PHY autoprobing, then creates XPCS PCS objects for active SGMII or 2500base-X ports. It then looks for an available `mdios` child node and optional compatible children for base-TX and base-T1. Errors unwind already registered buses.

## State and Persistence Behavior

The file stores allocated buses in `priv->mdio_pcs`, `priv->mdio_base_tx`, and `priv->mdio_base_t1`, and PCS handles in `priv->pcs[port]`. There is no persistent hardware configuration here beyond register writes performed through MDIO operations. Bus registrations persist for the DSA switch lifetime and are removed during teardown.

## Dependencies and Integration Points

Dependencies include Linux MDIO and OF MDIO helpers, `pcs-xpcs`, DSA port metadata, chip register maps in `struct sja1105_regs`, chip callback pointers in `struct sja1105_info`, and SPI register helpers `sja1105_xfer_u32()`. `sja1105_main.c` calls register/unregister during DSA setup/teardown and phylink selects `priv->pcs[port]` via `sja1105_mac_select_pcs()`.

## Risks and Edge Cases

- SJA1110 PCS banking is stateful in hardware. Concurrent accesses would rely on MDIO bus serialization; bypassing the bus could race the bank register.
- The code returns synthetic XPCS IDs for selected ID registers, so library matching depends on these constants.
- Unsupported MMDs on older PCS reads return `0xffff`, while writes return `-EINVAL`; callers need to tolerate that MDIO convention.
- Registration without an `mdios` node is valid after PCS registration, but internal PHY buses will be absent.
- If PCS creation fails partway through ports, all previously created PCS instances and the bus are unwound.

## Test Signals

On SGMII/2500base-X ports, phylink should receive a non-NULL PCS and XPCS probing should see the synthetic NXP IDs. Internal SJA1110 PHY nodes under `mdios` should appear as MDIO buses with stable IDs ending in `-base-tx` or `-base-t1`. Clause 22 and Clause 45 reads should return 16-bit values, unsupported/reserved accesses should fail cleanly, and DSA teardown should unregister all buses without dangling PCS pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_ptp.c

## Purpose

This file implements Precision Time Protocol hardware clock support and packet timestamping for SJA1105/SJA1110 switches. It registers a PHC, supports get/set/adjust time and frequency, exposes one configurable PTP_CLK pin for periodic output or external timestamp polling, manages hardware timestamp configuration per port, reconstructs partial timestamps on older chips, and handles SJA1110 meta-frame timestamp completion.

## Important APIs, Types, and Data

- `sja1105_hwtstamp_set()` and `sja1105_hwtstamp_get()` manage per-port TX/RX hardware timestamp enable bitmaps.
- `sja1105_get_ts_info()` reports ethtool timestamping capabilities and PHC index.
- `sja1105et_ptp_cmd_packing()` and `sja1105pqrs_ptp_cmd_packing()` pack generation-specific PTP command register layouts.
- `sja1105_ptp_commit()` reads/writes the PTP control register through chip-specific packing callbacks.
- `__sja1105_ptp_gettimex()`, `__sja1105_ptp_settime()`, and `__sja1105_ptp_adjtime()` are lock-expecting internal helpers used by PHC callbacks and static reload.
- `sja1105_ptp_clock_register()` initializes queues, PHC caps, timer, command defaults, registers the PHC, and resets the PTP clock.
- `sja1105_ptp_txtstamp_skb()`, `sja1105_rxtstamp()`, `sja1110_rxtstamp()`, `sja1110_txtstamp()`, and `sja1110_process_meta_tstamp()` implement TX/RX timestamp delivery.

## Control Flow

PHC operations all serialize on `ptp_data->lock`. `gettimex` reads `PTPCLKVAL` with optional system timestamping. `settime` switches the hardware to set mode, writes ticks converted from nanoseconds, and notifies TAS of a clock step. `adjtime` switches to add mode and writes a signed tick delta. `adjfine` converts scaled ppm into the hardware centered `PTPCLKRATE` representation and notifies TAS of frequency adjustment.

TX timestamping on SJA1105 clones the skb in `sja1105_port_txtstamp()`. Deferred management-route TX later calls `sja1105_ptp_txtstamp_skb()`, which polls the per-port egress timestamp register for the update bit, reads the current PHC, reconstructs a full timestamp from the partial hardware timestamp, and completes the skb timestamp. On SJA1110, `sja1110_txtstamp()` assigns an 8-bit timestamp ID and queues the clone; `sja1110_process_meta_tstamp()` matches a later TX meta timestamp by ID and completes it.

RX timestamping on SJA1105 queues skbs because reconstructing partial timestamps requires a sleepable PHC read. The PTP worker drains the queue, reconstructs timestamps, and reinjects packets via `netif_rx()`. SJA1110 receives full enough timestamps from tag/meta handling and stamps synchronously without deferral.

The PTP_CLK pin can be set to periodic output by programming start time and half-period registers, advancing start to a future base time, and issuing start/stop commands. External timestamp mode switches the AVB parameter pin function and polls `PTPSYNCTS` through a timer because hardware has no FIFO or interrupt.

## State and Persistence Behavior

Persistent driver state lives in `priv->ptp_data`: PHC pointer, caps, command shadow, RX/TX skb queues, external timestamp timer, last `ptpsyncts`, and the lock. Timestamp enablement lives in `priv->hwts_tx_en` and `priv->hwts_rx_en`. The PTP command shadow preserves mode bits such as `corrclk4ts` and `ptpclkadd` across command updates.

Switch static config reload in `sja1105_main.c` locks the PTP data, reads current time with system timestamp, resets/uploads config, sets the hardware time to zero, computes elapsed wall time, and adjusts PHC forward. That makes this file part of the reload persistence story.

## Dependencies and Integration Points

This implementation depends on Linux PTP clock APIs, skb timestamp APIs, timers, SPI helpers, DSA timestamp callbacks, SJA1105 tagger metadata, dynamic AVB parameter writes, and TAS hooks `sja1105_tas_clockstep()` and `sja1105_tas_adjfreq()`. Chip-specific timestamp width, egress timestamp size, register addresses, and optional SJA1110 TX timestamp support come from `struct sja1105_info` and `struct sja1105_regs`.

## Risks and Edge Cases

- E/T partial timestamps wrap in about 0.135 seconds, so queued RX/TX timestamp work must run within one wrap period or reconstruction can be wrong.
- SJA1110 TX timestamp IDs are 8-bit and wrap automatically; heavy outstanding TX timestamp load can misassociate if IDs are reused before meta frames arrive.
- External timestamp support polls a single register at a low rate and has no FIFO, so events faster than supported polling can be lost.
- PTP pin function is shared between periodic output and external timestamp; changing it dynamically writes AVB params and can disturb existing pin users.
- `ptp_clock_register()` error handling uses `IS_ERR_OR_NULL`; callers should handle registration failure and cleanup paths correctly.
- Static reload and PHC operations share the same lock; lock ordering with `fdb_lock` and `mgmt_lock` in reload must remain consistent to avoid deadlocks.

## Test Signals

`ethtool -T` should report hardware TX/RX/raw timestamping and a valid PHC index. `hwstamp_ctl` should enable/disable only `HWTSTAMP_TX_ON` and `HWTSTAMP_FILTER_PTP_V2_L2_EVENT`. `phc2sys` or `testptp` should exercise get/set/adjtime/adjfine. PTP event traffic should produce RX timestamps and management-route TX timestamps on older chips, while SJA1110 should complete TX timestamps through meta frames. Periodic output should toggle the PTP_CLK pin with requested period, and external timestamp mode should report events at the documented low-rate polling limit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_ptp.h

## Purpose

This header defines the SJA1105 PTP interface used by the driver when `CONFIG_NET_DSA_SJA1105_PTP` is enabled, and provides no-op stubs when it is disabled. It is the shared contract between main DSA operations, TAS scheduling, tagger timestamp handling, and the PTP implementation.

## Important APIs, Types, and Data

- `SJA1105_TICK_NS` defines the hardware clock tick as 8 ns.
- `ns_to_sja1105_ticks()` and `sja1105_ticks_to_ns()` convert between nanoseconds and hardware ticks.
- `future_base_time()` computes the first schedule base time at or after `now`.
- `ns_to_sja1105_delta()` and `sja1105_delta_to_ns()` convert TAS correction deltas in 200 ns units.
- `struct sja1105_ptp_cmd` mirrors PTP control bits for clock pin start/stop, schedule start/stop, reset, corrected clock timestamps, and add/set mode.
- `struct sja1105_ptp_data` stores PTP runtime state when enabled, or only a mutex when disabled.
- The header declares PHC registration, timestamp callbacks, hwtstamp callbacks, internal PHC get/set/adjust helpers, command commit, per-generation command packers, and SJA1110 meta timestamp handling.

## Control Flow

With PTP enabled, callers use the declared functions implemented in `sja1105_ptp.c`. With PTP disabled, the header substitutes inline stubs or `NULL` callback macros. This lets `sja1105_main.c` keep the same structure fields and DSA ops wiring while compiling out actual PHC/timestamp behavior.

The inline conversion helpers are used by PTP and TAS code to keep time arithmetic consistent. `future_base_time()` avoids starting periodic output or schedules in the past by advancing by an integer number of cycles.

## State and Persistence Behavior

When enabled, `struct sja1105_ptp_data` owns timers, queues, PHC registration state, command shadow, lock, EXTS enable state, and last sync timestamp. When disabled, only the lock remains because reload code still uses `priv->ptp_data.lock` for common lock ordering. Stubbed get/set/adjust functions return success, so reload code can compile and run without PTP hardware-clock preservation work.

## Dependencies and Integration Points

The header depends on Linux timer support and is guarded by `IS_ENABLED(CONFIG_NET_DSA_SJA1105_PTP)`. It integrates with `sja1105_main.c`, `sja1105_ptp.c`, `sja1105_tas.c`, and tagger metadata paths. Public callback declarations match DSA timestamp and hwtstamp operation signatures.

## Risks and Edge Cases

- When PTP is disabled, several DSA callbacks are `NULL`; call sites must tolerate disabled timestamp support.
- Stubbed internal PHC functions return zero without touching output values, so code that uses outputs must only do so in contexts where PTP is enabled or the value is otherwise irrelevant.
- Time conversion helpers use integer division and truncate sub-tick/sub-delta values.
- `future_base_time()` assumes positive cycle time; callers must validate cycle values.

## Test Signals

Build testing should cover both `CONFIG_NET_DSA_SJA1105_PTP=y/m` and disabled configurations. Enabled builds should expose PHC/timestamp callbacks and compile TAS users of conversion helpers. Disabled builds should still compile main reload logic, DSA ops should omit timestamp callbacks through `NULL` macros, and probe/setup should proceed without PTP clock registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_spi.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_spi.c

## Purpose

This file provides the SPI transport, reset/static-config upload logic, register maps, and chip capability descriptors for the SJA1105/SJA1110 driver. It is the hardware access foundation used by dynamic config, MDIO, PTP, ethtool stats, clocking, and main DSA operations.

## Important APIs, Types, and Data

- `sja1105_xfer_buf()`, `sja1105_xfer_u64()`, and `sja1105_xfer_u32()` are exported SPI helpers for raw buffers and native-endian 64/32-bit register values.
- `sja1105_spi_message_pack()` builds the 4-byte SPI message header with access mode, read count, and address.
- `sja1105_xfer()` chunks large transfers according to `priv->max_xfer_len` and optionally asks the SPI core for system timestamps around PTP-sensitive transfers.
- Reset helpers `sja1105et_reset_cmd()`, `sja1105pqrs_reset_cmd()`, and `sja1110_reset_cmd()` implement generation-specific reset register writes.
- `sja1105_inhibit_tx()` toggles per-port TX inhibition through the port control register.
- `static_config_buf_prepare_for_upload()` validates, packs, and CRC-finalizes the static configuration image.
- `sja1105_static_config_upload()` inhibits TX, resets the switch, uploads the static config, checks status bits, and retries.
- `sja1105et_regs`, `sja1105pqrs_regs`, and `sja1110_regs` define per-generation register addresses.
- `sja1105e_info`, `sja1105t_info`, `sja1105p_info`, `sja1105q_info`, `sja1105r_info`, `sja1105s_info`, and `sja1110[a-d]_info` describe chip capabilities, callbacks, table ops, dynamic ops, tag protocol, PTP widths, port modes, internal PHYs, and register maps.

## Control Flow

All SPI transfers go through `sja1105_xfer()`. It splits a logical transfer into chunks, packs a header for the current register address, configures a two-transfer SPI message for header plus payload, chooses RX or TX buffer depending on access mode, attaches optional PTP system timestamp capture to the header for reads or data for writes, advances the buffer/register address, and calls `spi_sync_transfer()` for each chunk.

The typed helpers pack/unpack 32-bit and 64-bit values with the driver packing API so callers can use CPU-endian integers. The static upload path allocates a packed image, validates table constraints, packs all tables, recalculates final CRC, inhibits TX on all ports, waits for drain, resets into programming mode, writes the config area, reads status, checks device ID and CRC/config-valid bits, and retries up to ten times.

Chip info structures bind together the rest of the driver. Probe selects an initial info table from OF match data, verifies hardware identity in `sja1105_main.c`, and all later operations dispatch through callbacks and register maps from that selected info.

## State and Persistence Behavior

This file does not own high-level networking state, but it writes persistent hardware state during static config upload and reset. `priv->max_xfer_len` is computed at probe from SPI controller limits and controls all future chunking. Chip info structs are immutable capability tables. Register writes through SPI immediately affect hardware; static upload replaces the switch configuration and resets hardware state, so callers must maintain software mirrors for runtime changes.

## Dependencies and Integration Points

The code depends on Linux SPI APIs, the packing API, static config validation/packing/CRC helpers, DSA switch state for port counts, and chip-specific helper functions implemented in other files: dynamic ops, static table ops, FDB add/del, PTP command packers, timestamp functions, clocking setup, RGMII delay setup, SJA1110 microcontroller disable, and MDIO PCS callbacks. `sja1105_main.c` uses the info structures for device matching and DSA behavior.

## Risks and Edge Cases

- SPI master max transfer/message limits are runtime constraints. Probe ensures at least one 64-bit payload fits, and `sja1105_xfer()` chunks longer buffers; incorrect `max_xfer_len` would break static config upload and dynamic table operations.
- Read count is expressed in 32-bit words, so buffer lengths should be word-aligned for hardware register reads.
- Static upload retries but returns `-EIO` after repeated reset/upload/status failures. Status bit interpretation is critical for distinguishing device ID mismatch, local CRC, global CRC, and invalid config.
- TX inhibit before reset reduces PHY jabber risk; skipping it can generate malformed packets during reset.
- SJA1110 reset intentionally avoids a full cold reset to keep the microcontroller disabled; changing reset semantics can re-enable firmware that interferes with driver-owned config.
- Chip info tables are dense and generation-specific. Wrong callbacks or capability flags can misroute FDB algorithms, timestamp behavior, PCS access, port mode validation, or dynamic table packing.

## Test Signals

Probe should calculate an acceptable transfer size, verify device ID/part number, and report the detected chip. Static config upload should succeed without CRC/config status errors, including with SPI controllers that force chunking. Reset/reload paths should inhibit TX and recover. Register read/write users such as ethtool stats, MDIO, PTP, dynamic config, and clocking should work across E/T, P/Q/R/S, and SJA1110 variants. Device-tree compatible mismatches should warn and switch to the detected info table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_spi.c -->
