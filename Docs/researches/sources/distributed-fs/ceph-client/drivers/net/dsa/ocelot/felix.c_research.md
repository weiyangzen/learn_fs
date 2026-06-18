# sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/felix.c

## Purpose
`felix.c` is the common DSA front end for Ocelot-compatible switches that communicate with the host through an NPI Ethernet CPU port or the software-defined `ocelot-8021q` tag protocol. It converts DSA callbacks into Ocelot switch-library operations, manages tag protocol setup and migration, initializes register maps and ports from `felix_info`, handles timestamping and MMIO packet extraction, and exports registration helpers used by chip-specific drivers.

## Important APIs, Types, and Functions
- `felix_register_switch()` is the exported entry point for chip-specific front ends. It allocates `struct felix` and `dsa_switch`, initializes Ocelot core fields, sets the initial tag protocol, and calls `dsa_register_switch()`.
- `felix_port_to_netdev()` and `felix_netdev_to_port()` are exported adapters used by Ocelot ops for netdev/port translation.
- `felix_classify_db()` maps DSA FDB/MDB database objects to the Ocelot library's bridge-dev convention.
- Tag protocol management is implemented by `felix_change_tag_protocol()`, `felix_connect_tag_protocol()`, `felix_tag_npi_*()`, `felix_tag_8021q_*()`, and shared migration helpers.
- `felix_update_tag_8021q_rx_rule()`, `felix_tag_8021q_vlan_add_rx()`, `felix_tag_8021q_vlan_add_tx()`, and related delete/update helpers program ES0/IS1/IS2 VCAP rules that identify source ports and redirect TX traffic for tag_8021q.
- `felix_update_trapping_destinations()` rewrites trap rules when tag protocol and no-XTR-IRQ behavior require different CPU destinations.
- DSA bridge/FDB/MDB/LAG/VLAN/STP callbacks mostly wrap `ocelot_*` library functions while handling CPU/NPI special cases.
- Phylink callbacks delegate MAC config/link state to the Ocelot library and chip-specific `felix_info` callbacks.
- `felix_init_structs()` parses device tree ports, requests target and per-port regmaps, initializes regfields, creates Ocelot port objects, and optionally allocates the chip MDIO bus.
- `felix_setup()` initializes Ocelot hardware, timestamping, ports, serdes, QoS maps, IRQ, devlink shared buffers, initial tag protocol, and DSA capability flags.
- PTP/timestamping paths include `felix_hwtstamp_get()`, `felix_hwtstamp_set()`, `felix_rxtstamp()`, `felix_txtstamp()`, and `felix_port_deferred_xmit()`.
- Devlink, tc, mirror, policer, MRP, priority, MAC Merge, HSR, stats, and MTU callbacks are mapped through `felix_switch_ops`.

## Control Flow
Chip drivers call `felix_register_switch()` with a hardware-specific `felix_info`. During DSA setup, `felix_setup()` calls `felix_init_structs()` to populate the embedded `struct ocelot`, maps resources from either hardcoded PCI resources or parent MFD regmaps, initializes regfields and port structures, and invokes optional MDIO allocation. It then runs Ocelot initialization, optional PTP setup, per-port initialization, optional serdes setup, QoS map initialization, optional IRQ request, devlink shared-buffer registration, and initial tag protocol setup.

The tag-protocol path has two modes. NPI mode configures the hardware CPU port module through `felix_npi_port_init()`, supports only one active conduit, and forwards host traffic through the NPI PGID. `ocelot-8021q` mode registers the tag_8021q tagger, configures CPU/user port assignments, programs VCAP rules through DSA tag VLAN callbacks, drains the CPU extraction queue, and sets DSA's VLAN-aware PVID untagging workaround. Protocol changes set up the new mode first, migrate MDB and host flood destinations, update trap destinations, then tear down the old mode.

Packet switching callbacks mostly translate DSA object shapes into Ocelot calls. CPU/NPI ports are remapped to `PGID_CPU` or `ocelot->num_phys_ports` where the Ocelot library models CPU-facing resources differently from physical DSA port numbers.

Timestamp receive handling either reconstructs a full timestamp using the low timestamp from the tagger plus the current PTP time, or, when the no-XTR-IRQ workaround is active, discards the Ethernet notification skb and polls the MMIO extraction group for the original trapped PTP frame. TX timestamping records a clone in Ocelot state and deferred tag_8021q injection removes the clone on injection failure.

Teardown reverses tag protocol setup under RTNL, deinitializes ports, unregisters devlink shared buffers, tears down timestamping and Ocelot core state, and frees chip-specific MDIO resources.

## State and Persistence Behavior
`struct felix` stores the `dsa_switch`, hardware info, embedded `struct ocelot`, optional internal MDIO bus and PCS array, switch base address, current tag protocol, current tag protocol ops, TX kthread worker pointer, and host flood masks. The embedded `struct ocelot` stores most hardware state such as ports, regmaps, VCAP blocks, PTP state, forwarding domains, devlink state, stats, and tc offloads. Runtime state is rebuilt on probe and is not persisted across driver unload or hardware reset.

Host flood masks are stored independently of the current tag protocol so they can be reapplied to the proper CPU forwarding mask during tag protocol migration. The tag protocol pointer is updated only after the new protocol and shared resources are successfully configured.

## Dependencies and Integration Points
The file depends on DSA, DSA taggers `ocelot` and `ocelot-8021q`, the Ocelot switch library and register definitions, phylink, PTP classification and timestamping, devlink shared buffers, switchdev, tc flower/policer/mirror/offload APIs, MRP, HSR helpers, OF parsing, regmap, platform/PCI device abstractions, and chip-specific callbacks supplied through `struct felix_info`.

## Risks and Edge Cases
- `felix_update_tag_8021q_rx_rules()` assumes the ES0 rule exists when VLAN filtering changes; missing rules would lead to a null dereference path if setup sequencing is broken.
- Changing NPI conduit is constrained because user ports still assigned to the old conduit must be down. Violating this would strand traffic.
- No-XTR-IRQ timestamp workaround is delicate: Ethernet packets act as notifications only, while real timestamped frames are extracted over MMIO.
- `felix_mrp_del()` calls `ocelot_mrp_add()` rather than a delete helper, which is a suspicious behavior signal and should be checked against the Ocelot API.
- Many callbacks remap CPU/NPI ports. Off-by-one or stale `ocelot->npi` values can affect FDB/MDB/bridge flag behavior.
- Tag protocol migration is intended to be consistent because NPI setup cannot fail, but new protocol setup and shared migration still need careful rollback.
- `felix_port_deferred_xmit()` frees its work object only on success; the failure branch frees the skb but not `xmit_work`, which is worth auditing against allocation ownership.

## Test Signals
High-value tests include DSA probe/remove for each front end, NPI and `ocelot-8021q` tag protocol setup and live migration, conduit changes with ports up/down and LAG conduits, VLAN filtering toggles under tag_8021q, FDB/MDB on standalone/bridge/LAG/CPU databases, PTP RX/TX timestamping with and without extraction IRQ, tc flower traps and trap destination migration, devlink shared-buffer operations, HSR behavior under each tag protocol, and fault-injection around regmap/MDIO/IRQ/timestamp initialization failure paths.
