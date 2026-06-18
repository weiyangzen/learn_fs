# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/chip.h

## Purpose

`chip.h` is the shared private contract for the Marvell 88E6xxx switch-chip driver. It defines the chip model taxonomy, per-model capability metadata, runtime state containers, operation tables, feature predicates, and exported helper prototypes used by `chip.c` and the sibling register/feature modules in `drivers/net/dsa/mv88e6xxx/`.

The header centralizes the driver’s internal object model: a `struct mv88e6xxx_chip` owns one physical switch, its DSA switch instance, register bus access, IRQ state, MDIO buses, policy rules, PTP state, per-port state, devlink regions, MST mappings, FID allocation bitmap, and TCAM entries.

## Important Types

- `enum mv88e6xxx_model` lists every supported switch model ID known to the driver, including 6020/6071/6085 through 6393X families.
- `enum mv88e6xxx_family` groups models by shared operation/capability families.
- `enum mv88e6xxx_edsa_support` records whether Ethertype DSA tags are unsupported, fully supported, or empirically supported despite documentation marking some forwarding cases reserved.
- `struct mv88e6xxx_info` is the per-model capability and address map record. It stores product number, port/PHY/GPIO/TCAM counts, register base addresses, max VID/SID, ageing coefficient, stats type, PVT support, invalid ports, SMI addressing mode, EDSA/PTP support, ATU move mask, internal PHY offset, and the selected `struct mv88e6xxx_ops`.
- `struct mv88e6xxx_chip` is the main runtime state object for one switch.
- `struct mv88e6xxx_port` stores per-port cached state: port index, firmware node, bridge PVID, SERDES stats, ATU/VTU violation counters, interface/CMODE, mirror flags, devlink region, PCS private data, LED state, and MAB state.
- `struct mv88e6xxx_atu_entry`, `struct mv88e6xxx_vtu_entry`, and `struct mv88e6xxx_stu_entry` model hardware ATU, VTU, and STU records.
- `struct mv88e6xxx_mst` tracks Linux bridge MSTI to hardware SID mappings with a refcount and cached STU entry.
- `struct mv88e6xxx_policy` represents ethtool RX classification rules mapped into switch policy/ATU state.
- `struct mv88e6xxx_irq` describes a nested interrupt controller with mask state, IRQ chip, domain, and IRQ count.
- `struct mv88e6xxx_port_hwtstamp` stores per-port timestamping state, queues, TX in-progress fields, and current hwtstamp config.
- `struct mv88e6xxx_tcam_key`, `struct mv88e6xxx_tcam_action`, and `struct mv88e6xxx_tcam_entry` describe TC flower/TCAM match and action state.

## Operation Tables and Internal APIs

`struct mv88e6xxx_ops` is the main model-specific virtual function table. It is intentionally broad because different 88E6xxx generations expose similar features through different registers or not at all. Important groups include:

- Setup and reset: `setup_errata`, `hardware_reset_pre`, `hardware_reset_post`, `reset`.
- Priority and rate units: `ieee_pri_map`, `ip_pri_map`, `irl_init_all`, `pot_clear`.
- EEPROM and switch MAC programming.
- PHY access: Clause 22 and Clause 45 read/write operations.
- PPU enable/disable.
- Port MAC/link configuration: RGMII delay, link force/unforce, SERDES link sync, pause, speed/duplex, max speed mode, frame mode, CMODE get/set, tag remap, jumbo/max frame size.
- Port policy and forwarding: unicast/multicast flood, EtherType, egress rate limiting, pause limits, learn limit, priority override, message port, upstream port, CPU port, ingress/egress monitor ports, cascade port, management reserved-to-CPU.
- Stats and SERDES stats/registers.
- ATU hash, VTU, and STU operations.
- Watchdog, GPIO, AVB/PTP, PTP clock, phylink capability, PCS, TCAM, and RMU hooks.

Other smaller operation structs isolate subsystems:

- `struct mv88e6xxx_bus_ops` abstracts SMI/PHY bus reads, writes, and init.
- `struct mv88e6xxx_irq_ops` abstracts child interrupt controller setup/action/free.
- `struct mv88e6xxx_gpio_ops` abstracts switch GPIO data, direction, and pin control.
- `struct mv88e6xxx_avb_ops` abstracts AVB/PTP/TAI register access.
- `struct mv88e6xxx_ptp_ops` abstracts PTP clock read/enable/verify, port/global enable, CPU port selection, and timestamp status registers.
- `struct mv88e6xxx_pcs_ops` abstracts PCS init, teardown, and phylink PCS selection.
- `struct mv88e6xxx_tcam_ops` abstracts TCAM entry insertion and flush.

The header exports register helpers implemented in `chip.c`: `mv88e6xxx_read()`, `mv88e6xxx_write()`, `mv88e6xxx_wait_mask()`, `mv88e6xxx_wait_bit()`, `mv88e6xxx_default_mdio_bus()`, and `mv88e6xxx_vtu_walk()`.

## Constants and Feature Predicates

Important constants include:

- `EDSA_HLEN`, used for CPU/DSA port MTU calculations.
- `MV88E6XXX_N_FID` and `MV88E6XXX_N_SID`, sizing software FID and SID management.
- `MV88E6XXX_FID_STANDALONE` and `MV88E6XXX_FID_BRIDGED`, the reserved databases used by standalone ports and VLAN-unaware bridging.
- PVT limits for 5-bit switch and 4-bit port addressing.
- `MV88E6XXX_MAX_GPIO`, `_MV88E6XXX_REGION_MAX`, `TCAM_MATCH_SIZE`, and stats type bits.

Inline helpers derive capabilities from `struct mv88e6xxx_info`:

- `mv88e6xxx_has_stu()` checks SID capacity plus STU load/get hooks.
- `mv88e6xxx_has_pvt()`, `mv88e6xxx_has_lag()`, and `mv88e6xxx_has_tcam()` gate PVT, LAG, and TCAM paths.
- `mv88e6xxx_num_databases()`, `mv88e6xxx_num_macs()`, `mv88e6xxx_num_ports()`, `mv88e6xxx_max_vid()`, `mv88e6xxx_max_sid()`, and `mv88e6xxx_num_gpio()` expose model limits.
- `mv88e6xxx_port_mask()` creates a local port bitmask from model port count.
- `mv88e6xxx_is_invalid_port()` checks the model invalid-port mask.
- `mv88e6xxx_port_set_mab()` stores per-port MAB state.
- `mv88e6xxx_reg_lock()` and `mv88e6xxx_reg_unlock()` wrap `chip->reg_lock`.

## Control Flow Role

This header does not execute control flow itself, but it defines the dispatch and state surfaces used by the implementation. `chip.c` fills a `struct mv88e6xxx_info` from the model table, then all major flows consult `chip->info` and `chip->info->ops` to decide whether a feature exists and which helper should program it. Sibling modules include this header to operate on the same `struct mv88e6xxx_chip` state and to implement functions assigned into the operation tables.

The operation-table design lets common DSA flows in `chip.c` call generic policy code while still using chip-family-specific register sequences. For example, VLAN add/delete logic can call `ops->vtu_getnext` and `ops->vtu_loadpurge`, phylink can call `ops->port_set_cmode` or `ops->port_set_speed_duplex`, and setup can conditionally invoke `ops->ptp_ops`, `ops->pcs_ops`, `ops->tcam_ops`, or `ops->gpio_ops`.

## State and Persistence Behavior

The major persistent-in-memory state fields are:

- `chip->tag_protocol`, selected DSA tagging mode.
- `chip->mdios`, registered internal and external MDIO buses.
- `chip->policies`, IDR of ethtool RX classification policies.
- `chip->g1_irq`, `chip->g2_irq`, IRQ numbers, names, worker, and polling work.
- `chip->gpio_data`, cached GPIO data.
- `chip->tstamp_cc`, `chip->tstamp_tc`, PTP clock info, TAI event work, pin config, and enable count.
- `chip->egress_dest_port` and `chip->ingress_dest_port`, current mirror destinations.
- `chip->port_hwtstamp[]` and `chip->ports[]`, per-port timestamping and switch-port state.
- `chip->regions[]`, devlink region handles.
- `chip->msts`, active bridge MST to SID mappings.
- `chip->fid_bitmap`, software allocation view of hardware FIDs.
- `chip->tcam.entries`, software list of TCAM entries.

This state is runtime driver state and is reconstructed during probe/setup. Hardware configuration is not expected to survive power loss; `chip.c` explicitly rejects suspend-to-RAM because DSA cannot yet restore switch configuration after power cycling.

## Dependencies and Integration Points

The header depends on kernel subsystems for IDR, VLAN, IRQ domains, GPIO descriptors, kthreads, LEDs, PHY, firmware properties, PTP clocks, timecounter/cyclecounter, and DSA. It is included by the main chip implementation and many sibling modules that implement register-specific operations. Because it exposes the full `struct mv88e6xxx_chip`, subsystem modules can share state without opaque accessors, but that also means field layout changes can have broad driver impact.

External integration is primarily through DSA and phylink, but the state objects also support ethtool, devlink, PTP/hwtstamp, TC flower/TCAM, GPIO, MDIO, and switchdev bridge/VLAN/FDB/MDB/MST workflows.

## Risks and Maintenance Concerns

- `struct mv88e6xxx_ops` is a large capability surface. Missing, mismatched, or incorrectly assigned function pointers can silently disable features or call wrong-family register sequences.
- Many feature predicates infer support from address fields or operation pointers. A model-info field set incorrectly can expose invalid paths such as TCAM, LAG, PVT, or STU.
- `struct mv88e6xxx_chip` is shared across modules and protected mostly by `reg_lock`; callers must respect lock expectations documented by comments, especially for register access and PTP cyclecounter reads.
- Fixed array sizing uses `DSA_MAX_PORTS`, `MV88E6XXX_N_FID`, `MV88E6XXX_N_SID`, and `MV88E6XXX_MAX_GPIO`. New hardware with larger limits would require careful auditing, not just table changes.
- The header intentionally stores hardware and Linux object mappings together, such as `msts`, `policies`, and `fid_bitmap`; bugs in lifecycle cleanup can leave stale pointers or inconsistent hardware/software allocation state.
- PTP and hwtstamp state includes sk_buff pointers and queues; teardown ordering must ensure no delayed work or packet references remain active.
- Invalid port masks and internal PHY offsets are model-specific. Incorrect values can make DSA expose unrouted ports or hide valid PHYs.

## Test Signals

Header-level changes should be validated by build coverage across all objects in `drivers/net/dsa/mv88e6xxx/`, because operation-table signatures and structure fields are consumed broadly. Runtime signals include correct feature gating in setup, matching phylink capabilities, valid devlink resources, successful PTP/hwtstamp registration only on supported models, successful TCAM setup only where `tcam_addr` and `tcam_ops` exist, and absence of lockdep or register-lock assertion failures under bridge/VLAN/FDB/LAG workloads.

For model-info or ops-table related header changes, test at least one representative from each affected family and verify probe detection, port count, invalid port handling, internal MDIO/PHY visibility, VLAN/STU/PVT behavior, stats strings/counts, EDSA tag selection, and optional feature registration.
