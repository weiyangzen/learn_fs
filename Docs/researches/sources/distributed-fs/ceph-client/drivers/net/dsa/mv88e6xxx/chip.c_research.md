# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/chip.c

## Purpose

`chip.c` is the central Marvell 88E6xxx DSA switch-chip driver implementation. It binds an MDIO-discovered switch to the Linux DSA core, owns chip detection and reset, constructs the per-model capability table, registers DSA and phylink callbacks, initializes switch-global and per-port hardware state, and routes higher-level switchdev operations into the lower register helper modules (`global1`, `global2`, `port`, `phy`, `serdes`, `ptp`, `devlink`, `tcflower`, and `tcam`).

The file is not just glue. It is the policy layer that translates Linux networking objects such as bridges, VLANs, FDB/MDB entries, LAGs, mirror rules, timestamping, ethtool stats, and tag-protocol changes into switch registers while accounting for differences across many 88E6xxx families.

## Important APIs and Entry Points

- `mv88e6xxx_probe()`, `mv88e6xxx_remove()`, and `mv88e6xxx_shutdown()` implement the MDIO driver lifecycle.
- `mv88e6xxx_register_switch()` creates and registers the `struct dsa_switch` with `mv88e6xxx_switch_ops` and `mv88e6xxx_phylink_mac_ops`.
- `mv88e6xxx_setup()` is the main DSA setup path. It registers MDIO buses, applies errata, caches port CMODE values, flushes VTU/STU, initializes ports, PVT, ATU, broadcast entries, priorities, PTP, hwtstamp, stats, TCAM, and devlink resources.
- `mv88e6xxx_teardown()` releases devlink, hwtstamp, PTP, flower, and MDIO resources.
- `mv88e6xxx_read()`, `mv88e6xxx_write()`, `mv88e6xxx_wait_mask()`, and `mv88e6xxx_wait_bit()` are exported register-access helpers used by sibling modules. They require `chip->reg_lock`.
- `mv88e6xxx_vtu_walk()` is exported for iterating valid VTU entries through the chip's `vtu_getnext` operation.
- `mv88e6xxx_get_tag_protocol()` and `mv88e6xxx_change_tag_protocol()` implement DSA/EDSA tag protocol selection and CPU-port reprogramming.
- `mv88e6xxx_get_caps()`, `mv88e6xxx_mac_prepare()`, `mv88e6xxx_mac_config()`, `mv88e6xxx_mac_finish()`, `mv88e6xxx_mac_link_down()`, and `mv88e6xxx_mac_link_up()` implement phylink integration.
- DSA switchdev callbacks cover bridge membership, bridge flags, STP/MST, VLAN add/delete/filtering, FDB/MDB add/delete/dump, mirroring, LAG, timestamping, TC flower, devlink, ethtool stats/registers/EEPROM, and MTU changes.

## Model and Capability Tables

The file defines many `static const struct mv88e6xxx_ops` tables, one per effective silicon operation profile, then maps `enum mv88e6xxx_model` entries to `struct mv88e6xxx_info` records in `mv88e6xxx_table[]`.

The operation tables are the main polymorphic dispatch layer. They select concrete register helpers for PHY access, port link/speed/duplex, RGMII delay, frame/tag mode, flooding, policy, jumbo size, stats snapshots, CPU/egress ports, interrupts, reset, VTU/STU, SERDES, GPIO, AVB/PTP, PCS, TCAM, EEPROM, and errata. The info table records family, product number, name, port counts, internal PHY layout, GPIO and TCAM capacity, max VID/SID, register address bases, ageing coefficient, interrupt counts, stats-bank shape, PVT support, multi-chip/dual-chip addressing, EDSA support, PTP support, invalid ports, ATU move masks, and the selected ops table.

Only a few OF compatibles are matched directly (`marvell,mv88e6085`, `marvell,mv88e6190`, `marvell,mv88e6250`); after SMI setup, `mv88e6xxx_detect()` reads the port 0 switch ID, looks up the exact product in `mv88e6xxx_table[]`, and replaces the compatible-provided generic info with the probed model.

## Control Flow

Probe starts by obtaining platform-data or OF match data, allocating `struct mv88e6xxx_chip`, acquiring an optional reset GPIO, attempting single-chip SMI detection for address 16 when allowed, falling back to address-specific SMI init and switch-ID detection, choosing default DSA vs EDSA tagging from `edsa_support`, initializing PHY bookkeeping, optionally reading EEPROM length, resetting the switch, setting up interrupt delivery, and finally registering with DSA.

Reset is staged. `mv88e6xxx_switch_reset()` disables all ports, waits for transmit queues to drain, toggles an optional reset GPIO with pre/post EEPROM wait hooks where supported, then calls the model-specific software reset op. Errata paths, such as MV88E6390 hidden register programming, can force disabled states and reset again during setup.

DSA setup then proceeds under `reg_lock` through deterministic hardware programming: register MDIO buses before PHY users need them; cache CMODE for phylink capability reporting; flush VTU/STU; configure each non-unused and non-invalid port; initialize IRL, switch MAC, PHYs, PVT, ATU, broadcast forwarding, POT/RMU/reserved management handling, trunk state, device mapping, priority maps, PTP/hwtstamp, statistics, and TCAM. Devlink resources/params/regions are deliberately initialized after dropping `reg_lock` to avoid lock-order inversion with devlink locks.

Removal unregisters the DSA switch, frees VTU/ATU problem IRQs, G2/G1 or polling IRQ resources, and destroys PHY state. Shutdown calls `dsa_switch_shutdown()` and clears driver data.

## Register Access and Locking

All switch register accesses are serialized by `chip->reg_lock`. `mv88e6xxx_read()` and `mv88e6xxx_write()` assert the lock is held and delegate to SMI helpers. Most DSA callbacks acquire this mutex before touching hardware and release it before returning. IRQ setup contains explicit lock dropping around `request_threaded_irq()` because the IRQ handler also takes the same lock. Devlink setup is likewise intentionally done without the register lock because devlink callbacks later take locks in the opposite order.

Stats access additionally uses `stats_mutex` in `struct mv88e6xxx_chip` conceptually for snapshot/dump serialization, though the main stats paths in this file use the register lock and model stats hooks. The PTP cyclecounter comment in the header requires `reg_lock` for clock reads.

## Interrupt Handling

Global1 interrupts are exposed through a nested irqdomain. `mv88e6xxx_g1_irq_setup_common()` creates mappings, masks hardware interrupt bits, and clears status by reading it. `mv88e6xxx_g1_irq_thread_work()` reads status, dispatches nested IRQs with `handle_nested_irq()`, and loops while enabled status bits remain set. If a platform IRQ is unavailable, `mv88e6xxx_irq_poll_setup()` starts a kthread worker that polls Global1 status every 100 ms.

Probe also configures Global2 interrupts when available and installs ATU/VTU problem interrupt handlers through helper modules. Teardown frees those resources in reverse order.

## Phylink and Port MAC Behavior

The file contains family-specific capability functions such as `mv88e6095_phylink_get_caps()`, `mv88e6250_phylink_get_caps()`, `mv88e6352_phylink_get_caps()`, `mv88e6390x_phylink_get_caps()`, and `mv88e6393x_phylink_get_caps()`. They translate cached CMODE values and model-specific programmable ports into `supported_interfaces` and `mac_capabilities`, including 10/100/1000, 2.5G, 5G, 10G, SGMII, 1000BASE-X, 2500BASE-X, XAUI/RXAUI, USXGMII, RGMII variants, RMII, and internal PHY modes.

MAC configuration handles PPU-updated internal PHY ports differently from fixed or in-band links. `mv88e6xxx_mac_prepare()` may force a link down before in-band interface changes. `mv88e6xxx_mac_finish()` can unforce links after configuration and records the selected interface. Link up/down callbacks program speed/duplex and synchronize link only when the switch cannot update that port automatically or fixed-link mode is used.

## VLAN, FID, ATU, STU, and MST State

The driver maintains a software `fid_bitmap` alongside hardware VTU/FID state. `mv88e6xxx_port_vlan_join()` creates a VTU entry when missing, allocates and flushes a new FID through `mv88e6xxx_atu_new()`, writes the VTU, seeds broadcast entries, and records the FID as used. `mv88e6xxx_port_vlan_leave()` removes a port from a VLAN, purges empty VLANs, releases associated MST/STU state, clears the FID bit, and removes ATU entries for that FID/port.

Two private VLAN/FID concepts are central:

- `MV88E6XXX_VID_STANDALONE`/`MV88E6XXX_FID_STANDALONE` isolate standalone ports and can use VTU policy trapping on DSA paths.
- `MV88E6XXX_VID_BRIDGED`/`MV88E6XXX_FID_BRIDGED` back VLAN-unaware bridge operation.

`mv88e6xxx_port_commit_pvid()` computes a port PVID and untagged-drop behavior from the port's bridge membership and bridge VLAN filtering state. VLAN filtering toggles secure vs disabled 802.1Q mode and recommits PVIDs. VLAN deletion flushes the DSA switchdev workqueue first so FDB deletions complete while the VTU entry still maps the FID needed for ATU operations.

MST support is backed by hardware STU entries. `mv88e6xxx_mst_get()` allocates or refcounts an SID for a `(bridge, MSTI)` pair, initializes all user ports to blocking and non-user ports to disabled, then writes the STU. `mv88e6xxx_mst_put()` decrements references and purges unused STU entries except SID 0. `mv88e6xxx_vlan_msti_set()` retargets a VLAN's SID with rollback if the VTU update fails.

FDB/MDB and policy rules share ATU helper paths. `mv88e6xxx_port_db_load_purge()` resolves VID to FID, fetches or initializes an ATU entry, adjusts `portvec` and state, and writes load/purge. FDB add verifies the entry can be found afterward and reports `-ENOSPC` if the hardware failed to retain it.

## Bridge, PVT, Flooding, and Cross-Chip State

`mv88e6xxx_port_vlan()` computes allowed local egress ports for a source `(device, port)` or virtual bridge. Standalone user ports are limited to the upstream port; bridged user ports can egress local DSA/CPU ports and local members of the same bridge; DSA/CPU source ports can egress all local ports.

Local port VLAN maps are updated by `mv88e6xxx_port_vlan_map()`. Cross-chip forwarding uses the Port VLAN Table when the chip has PVT support. The driver can map a Linux bridge as a virtual single-port switch behind the CPU and uses that mapping for cross-chip bridge forwarding and `tx_fwd_offload`.

Bridge flags update hardware learning, unicast flood, multicast flood, broadcast flood, locked-port, and MAB state. Broadcast flood is implemented by adding or purging broadcast ATU entries in the private database and across all VTU VLANs, not merely by toggling a single flood bit.

## LAG, Mirroring, and Tag Protocols

LAG offload requires Global2 support, a non-zero DSA LAG ID, at most eight members, and hash-based TX selection. The driver writes trunk mapping entries for destination LAGs and eight trunk mask buckets using a fixed balance table. Local join enables trunk mode on the port then syncs masks and maps; failure clears trunk state. Cross-chip LAG join/leave updates masks/maps plus PVT entries for the remote source port.

Mirror add configures ingress or egress monitor destination ports through the model egress-port op. It refuses to change a monitor destination while another mirror of the same direction is active. Mirror delete disables the per-port mirror bit and restores the monitor destination to the upstream port once no other mirror of that direction remains.

Tag protocol changes allow DSA and conditionally EDSA. Unsupported EDSA is rejected; undocumented EDSA emits a warning. CPU ports are reprogrammed to DSA or Ethertype DSA frame/egress mode. On error, the old protocol is restored and already-updated CPU ports are unwound in reverse.

## EtHTool, Devlink, PTP, Hwtstamp, TCAM, and TC Flower Integration

The stats code maps hardware counters to ethtool strings, generic ethtool stats, standard MAC stats, and RMON histograms. It snapshots the stats unit before reads, handles family-specific bank selection, appends SERDES stats when supported, and appends per-port ATU/VTU violation counters kept in `chip->ports[]`.

Register dumps include 32 port registers plus optional SERDES register dumps. EEPROM access is passed to model ops and guarded by a fixed magic value for writes. MTU changes account for EDSA overhead on CPU/DSA ports and choose per-port jumbo-size or global max-frame-size programming based on hardware support.

PTP and hardware timestamping are set up only for models whose info has `ptp_support`; DSA callbacks are wired to `hwtstamp` and `ptp` helper modules. TC flower callbacks are wired to `tcflower` helpers and TCAM setup flushes model TCAM state when the chip has TCAM support. Devlink resource, parameter, info, and region callbacks are integrated through the sibling `devlink` module.

## Dependencies and Integration Points

This file integrates deeply with Linux kernel networking:

- DSA core (`struct dsa_switch_ops`, DSA port iteration helpers, tag protocols, bridge/LAG cross-chip callbacks).
- phylink (`struct phylink_mac_ops`, `phylink_config`, PCS selection).
- switchdev bridge/VLAN/FDB/MDB/MST objects.
- ethtool stats, RMON, EEPROM, RX flow classification.
- MDIO/MII bus registration and PHY/PCS access.
- irqdomain, threaded IRQs, nested IRQs, and kthread polling.
- devlink resources, params, info, and regions.
- PTP/hwtstamp, TC flower, TCAM, GPIO reset, OF/platform data.

Most low-level register operations live in sibling modules and are accessed through model ops or helpers included at the top of the file. This separation makes `chip.c` the coordinator and policy layer rather than the only register-definition location.

## State and Persistence Behavior

Runtime state is held in `struct mv88e6xxx_chip` and per-port `struct mv88e6xxx_port`: selected tag protocol, MDIO bus list, policy IDR, IRQ domains and worker, PTP/timecounter state, monitor ports, timestamp queues, port PVID and CMODE, mirror flags, MAB flags, devlink regions, MST list, FID bitmap, and TCAM entry list.

Hardware state is repeatedly reconstructed from Linux switch state rather than persisted across power loss. Suspend-to-RAM is explicitly rejected because DSA has no switch reconfiguration support after power cycling. EEPROM contents may be read/written for supported chips, but normal bridge/VLAN/FDB/LAG/PTP setup is volatile hardware configuration.

## Risks and Failure Modes

- Register access without `reg_lock` is a correctness hazard; exported read/write helpers assert this at runtime.
- Lock ordering matters. IRQ setup and devlink setup contain explicit lock avoidance because handlers and devlink callbacks take locks in different contexts.
- VLAN/FID/ATU ordering is subtle. VLAN deletion flushes switchdev work to prevent FDB deletion from racing after VTU removal; changing this can make ATU purges target the wrong or missing FID.
- Model tables are high risk: assigning the wrong operation table or capability field can expose unsupported hardware paths, break reset, use wrong stats bank selection, or misreport phylink capabilities.
- EDSA support differs between supported, unsupported, and empirically-undocumented models. Enabling EDSA on the wrong chip can break CPU-tag framing.
- PVT virtual bridge mapping depends on DSA tree indices and the finite 5-bit switch namespace; bridge capacity is derived at setup time and can be exhausted by topology.
- LAG offload assumes hash-based TX and supports at most eight members. Trunk masks must be updated consistently for local and cross-chip members.
- Broadcast flood state is stored through ATU entries across all VLANs, so missed VTU walk errors or partial updates can leave inconsistent broadcast behavior.
- Hardware reset around EEPROM loads has family-specific pre/post wait hooks; skipping those hooks can leave EEPROM-backed strap or mode state corrupted.
- Some paths return `-EOPNOTSUPP` deliberately to let switchdev fall back to software behavior; replacing those with hard failures would regress mixed hardware/software VLAN setups.

## Test Signals

Useful validation signals include successful MDIO probe and exact switch detection logs, DSA registration, absence of "Switch registers lock not held!" reports, successful bridge/VLAN/FDB/MDB operations through `bridge`, `ip link`, and `devlink`, correct ethtool stats/register dumps, phylink link-mode advertisement matching hardware ports, PTP clock registration on supported models, and IRQ or polling paths delivering ATU/VTU problem counters.

Targeted tests should cover:

- Probe/reset on at least one single-chip-addressing model and one multi-chip/dual-chip model.
- VLAN-aware and VLAN-unaware bridge join/leave, PVID changes, VLAN deletion racing with FDB deletion, and software fallback for unsupported VLANs.
- FDB/MDB add/delete/dump with unicast, multicast, VLAN-specific, and VLAN-unaware entries.
- MSTI assignment and STP state changes for STU-capable and STU-incapable chips.
- Tag protocol changes between DSA and EDSA, including unsupported and undocumented EDSA cases.
- LAG join/leave/change for local and cross-chip ports, over-limit member rejection, and non-hash TX rejection.
- Mirror add/delete with conflicting monitor destinations.
- PTP/hwtstamp, TC flower/TCAM, EEPROM, stats, and SERDES behavior on models that advertise those ops.
