# subset-b-004325 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/port.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/port.c

## Purpose
Implements Marvell 88E6xxx per-port register programming helpers. It is the chip-variant aware layer used by the main DSA driver to configure link forcing, speed/duplex, RGMII delays, cmode/SERDES mode selection, bridge state, VLAN/FID/PVID behavior, egress tagging, flooding, mirroring, policy actions, jumbo mode, priority remapping, and special EtherType handling.

## Important APIs, Types, and Functions
The base helpers are `mv88e6xxx_port_read`, `mv88e6xxx_port_write`, and `mv88e6xxx_port_wait_bit`, which add `chip->info->port_base_addr` to the logical port and call the common register accessors. Public configuration entry points include `mv88e6xxx_port_set_link`, `mv88e6xxx_port_sync_link`, chip-specific `*_port_set_speed_duplex`, `*_port_set_cmode`, `mv88e6xxx_port_set_state`, `mv88e6xxx_port_set_vlan_map`, `mv88e6xxx_port_get_fid`, `mv88e6xxx_port_set_fid`, `mv88e6xxx_port_get_pvid`, `mv88e6xxx_port_set_pvid`, `mv88e6xxx_port_set_mirror`, `mv88e6xxx_port_set_policy`, `mv88e6393x_port_set_policy`, and TCAM-enabling helpers.

## Control Flow and State
Most functions follow read-modify-write control flow with early error returns. Capability restrictions are encoded by chip-specific wrappers, for example 2500/10000 Mbps only on selected ports and cmode changes only on SERDES-capable ports. Persistent state is split between hardware registers and `chip->ports[port]` fields such as `cmode`, `mirror_ingress`, and `mirror_egress`. FID state spans registers 0x06 and 0x05 on devices with more than 16 databases. `mv88e6393x` policy and EtherType operations use indirect pointer/EPC sequences and busy waits.

## Dependencies and Integration Points
Depends on `chip.h` for device metadata and ops, `global2.h` for monitor destination writes, `port.h` constants, `serdes.h` cmode values, phylink/PHY interface enums, bridge STP states, DSA port iteration, and common `mv88e6xxx_*` register access under the driver's outer locking discipline. The ops table in chip descriptors selects the appropriate functions.

## Risks and Test Signals
Main risks are wrong chip/port capability gates, incorrect bit preservation during read-modify-write, cmode cache drift after failed writes, and indirect register sequences racing if called outside the register lock. Regression signals include phylink mode tests, STP state transitions, VLAN/FID/PVID programming, bridge flooding/mirroring behavior, ethtool or debug register dumps, and hardware tests for 200/2500/5000/10000 Mbps edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/port.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/port.h

## Purpose
Defines the 88E6xxx per-port register map, bit fields, product IDs, and exported per-port programming prototypes used by `port.c`, other driver modules, and chip operation tables.

## Important APIs, Types, and Functions
The header enumerates register offsets such as `MV88E6XXX_PORT_STS`, `MV88E6XXX_PORT_MAC_CTL`, `MV88E6XXX_PORT_CTL0`, `MV88E6XXX_PORT_CTL1`, `MV88E6XXX_PORT_BASE_VLAN`, `MV88E6XXX_PORT_DEFAULT_VLAN`, policy/priority registers, LED control, hidden register access, and 6393X EPC/policy management fields. It declares all public port helpers, including speed/duplex, cmode, VLAN/FID/PVID, state, flooding, policy, trunking, jumbo, pause limit, mirror, hidden register, LED setup, and TCAM enable functions.

## Control Flow and State
This file has no runtime control flow. Its state model is declarative: macros encode how persistent port state is stored in hardware. Several logical properties span multiple bit fields or registers, such as FID upper/lower bits, priority remap tables, 6393X indirect policy pages, and hidden register command/data ports.

## Dependencies and Integration Points
Includes `chip.h` for `struct mv88e6xxx_chip` and enums used in prototypes. The constants are consumed by `port.c`, `port_hidden.c`, TCAM setup, LED support, PTP/trace-adjacent code, and chip descriptor code assigning function pointers.

## Risks and Test Signals
Bit definitions are hardware ABI. A wrong mask or overlapping value can silently program forwarding, VLAN, LED, or link state incorrectly. Test signals are compile coverage across all chip variants, register dump comparison against datasheets, exercising each ops-table variant, and validating that optional LED/PTP/TCAM builds still compile with the declared prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/port_hidden.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/port_hidden.c

## Purpose
Implements access to undocumented/hidden per-port registers used by some mv88e6390/mv88e6341 errata and development paths.

## Important APIs, Types, and Functions
Exports `mv88e6xxx_port_hidden_write`, `mv88e6xxx_port_hidden_wait`, and `mv88e6xxx_port_hidden_read`. The functions use the reserved 0x1a register through the data port and control port constants from `port.h`.

## Control Flow and State
Writes first load the data port, then write a BUSY|WRITE command containing block, port, and register fields to the control port. Reads write a BUSY|READ command, wait until BUSY clears, and then read the data port. Persistent state is entirely in hidden hardware registers; no software cache is maintained here.

## Dependencies and Integration Points
Depends on `mv88e6xxx_port_write`, `mv88e6xxx_port_read`, and `mv88e6xxx_port_wait_bit`. `port.c` uses it for `mv88e6341_port_set_cmode_writable`, enabling forced cmode and SGMII autonegotiation bits before normal cmode programming.

## Risks and Test Signals
Risk centers on undocumented register semantics, missing waits after writes, and block/port/reg field overflow. Calls should be made under the normal register lock. Tests should cover the affected errata path on supported chips, timeout behavior if BUSY never clears, and ensuring unsupported chips never select hidden-register ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/port_hidden.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/ptp.c

## Purpose
Provides PTP hardware clock support for 88E6xxx devices, including cyclecounter/timecounter setup, frequency/time adjustment, external timestamp capture on supported GPIO pins, overflow maintenance, and per-family PTP ops descriptors.

## Important APIs, Types, and Functions
Key structures include `mv88e6xxx_cc_coeffs` and exported ops `mv88e6165_ptp_ops`, `mv88e6352_ptp_ops`, and `mv88e6390_ptp_ops`. Important functions are `mv88e6xxx_ptp_setup`, `mv88e6xxx_ptp_free`, `mv88e6xxx_ptp_adjfine`, `mv88e6xxx_ptp_adjtime`, `mv88e6xxx_ptp_gettime`, `mv88e6xxx_ptp_settime`, `mv88e6352_ptp_enable_extts`, and family-specific clock reads.

## Control Flow and State
Setup reads the TAI clock period, selects 4/8/10 ns coefficients, initializes `chip->tstamp_cc` and `chip->tstamp_tc`, configures `ptp_clock_info`, optionally programs the PTP CPU destination port, registers the PHC, and schedules overflow work. Time changes are protected by `mv88e6xxx_reg_lock`. External timestamp enable configures GPIO function, starts delayed polling, reads TAI event status, clears valid events, converts raw cycles to nanoseconds, and emits `ptp_clock_event`.

## Dependencies and Integration Points
Depends on AVB TAI read/write ops, GPIO ops, hwtstamp support, global1/global2 helpers, kernel PTP, workqueues, DSA upstream-port lookup, and the driver register lock. It integrates with ethtool/SIOCSHWTSTAMP paths through `hwtstamp.c` and with PHC consumers through `ptp_clock_register`.

## Risks and Test Signals
Risks include wrong clock-period coefficients, missed 32-bit counter overflow, deadlocks if free is called with the register lock held, event polling races, unsupported GPIO/pin functions, and firmware/hardware reporting unexpected periods. Test signals include `phc2sys`/`ptp4l` stability, adjfine bounds, external timestamp edge tests, suspend/remove cleanup, and forced error paths for TAI reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/ptp.h

## Purpose
Declares PTP/TAI register constants and the build-time interface for enabling or stubbing mv88e6xxx PTP support.

## Important APIs, Types, and Functions
Defines TAI config, clock period, event status, event time, global time, and 6165 per-port timestamp status offsets. Under `CONFIG_NET_DSA_MV88E6XXX_PTP`, it declares `mv88e6xxx_ptp_setup`, `mv88e6xxx_ptp_free`, `ptp_to_chip`, and extern PTP ops descriptors. Without PTP config, setup/free become no-op inline functions and the ops descriptors are empty static constants.

## Control Flow and State
There is no runtime control flow except compile-time selection. The constants describe persistent hardware state used by `ptp.c` and hwtstamp logic: TAI event capture configuration, valid/error bits, raw timestamp words, and per-port arrival/departure status blocks.

## Dependencies and Integration Points
Includes `chip.h` and exposes symbols consumed by chip descriptors and the main driver setup/teardown path. It links PTP support to hwtstamp and AVB accessors while allowing the driver to compile with PTP disabled.

## Risks and Test Signals
Risks include config-stub divergence from the enabled implementation and incorrect register offsets affecting timestamp capture. Test signals are allmodconfig and no-PTP builds, PHC registration on enabled builds, and hwtstamp tests that validate arrival/departure status offsets for 6165/6352/6390 families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/serdes.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/serdes.c

## Purpose
Implements SERDES lane discovery, PCS state decoding, interrupt mapping, ethtool stats, and register dumps for 88E6xxx SERDES-capable chips.

## Important APIs, Types, and Functions
Public functions include `mv88e6xxx_pcs_decode_state`, lane mappers `mv88e6341_serdes_get_lane`, `mv88e6390_serdes_get_lane`, `mv88e6390x_serdes_get_lane`, `mv88e6393x_serdes_get_lane`, stats functions for 6352 and 6390 families, IRQ mapping helpers, and get-regs length/dump helpers. Internal read helpers use page-based 6352 access and Clause 45 6390 lane access.

## Control Flow and State
PCS decode first honors BMSR link status, then derives link, autoneg completion, speed, duplex, and pause from SGMII PHY status. Lane discovery maps current `chip->ports[port].cmode` to SERDES lane addresses and returns negative errno for non-SERDES ports. The 6352 stats path accumulates hardware counters into `chip->ports[port].serdes_stats`; 6390 stats return current 48-bit register values. Register dumps iterate static register lists or page ranges.

## Dependencies and Integration Points
Depends on `phy.h` page reads, Clause 45 PHY reads, `global2.h` scratch SERDES detection, `port.h` cmode values, irqdomain mapping, ethtool string/stats APIs, MII helpers, and phylink link-state semantics.

## Risks and Test Signals
Risks include stale cmode cache causing wrong lane selection, invalid speed decoding, counter read width/order mistakes, and register dump reads from inactive lanes. Test signals include phylink resolution for SGMII/1000BASE-X/2500BASE-X, ethtool stats/registers, SERDES IRQ delivery, and mode transitions on ports 0/5/9/10 depending on chip family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/serdes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/serdes.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/serdes.h

## Purpose
Defines SERDES register addresses, interrupt bits, lane IDs, PCS operational constants, and public SERDES/PCS helper prototypes.

## Important APIs, Types, and Functions
Important definitions include 6352 fiber page and interrupt registers, 6390 lane IDs, 10G/SGMII/USXGMII register offsets, SGMII PHY status bits, 6393X POC and power/reset bits, and errata register fields. It declares lane lookup, IRQ mapping, stats, get-regs, PCS decode, and external PCS ops descriptors. Inline wrappers `mv88e6xxx_serdes_get_lane` and `mv88e6xxx_serdes_irq_mapping` gate optional chip ops.

## Control Flow and State
The only executable logic is optional-ops dispatch in inline helpers. Persistent state is hardware-defined: lane identity and PCS mode are inferred from port cmode and SERDES registers, not stored in this header.

## Dependencies and Integration Points
Includes `chip.h` and forward-declares `phylink_link_state`. Used by `serdes.c`, `port.c`, PCS implementation files, chip descriptors, and interrupt setup paths.

## Risks and Test Signals
Risks are ABI-style: wrong lane IDs or bit masks break link setup, interrupts, and stats. Test signals are compile coverage for all chip descriptors, SERDES link-up in each supported interface mode, interrupt status decode, and ethtool register dumps matching known hardware values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/serdes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/smi.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/smi.c

## Purpose
Implements System Management Interface bus access selection for 88E6xxx switches, covering direct single-chip, dual-direct, and indirect multi-chip addressing modes.

## Important APIs, Types, and Functions
The exported entry point is `mv88e6xxx_smi_init`. Internal ops implement direct `mdiobus_read_nested`/`mdiobus_write_nested`, dual-direct address offsetting by `chip->sw_addr`, indirect command/data register transactions, and busy polling through `mv88e6xxx_smi_direct_wait`.

## Control Flow and State
Initialization selects `chip->smi_ops` based on `chip->info->dual_chip`, strapped `sw_addr`, and `chip->info->multi_chip`, then stores `chip->bus` and `chip->sw_addr`. Indirect reads write a BUSY|mode22|read command, wait for busy clear, then read data. Indirect writes write data, issue BUSY|mode22|write, then wait. Persistent state is the selected bus ops pointer and switch address.

## Dependencies and Integration Points
Depends on MDIO bus APIs, jiffies timeout helpers, and `struct mv88e6xxx_bus_ops` consumed by common register accessors. It is one of the earliest setup pieces before higher-level register helpers work.

## Risks and Test Signals
Risks include wrong addressing mode selection, timeout tuning for slow MDIO, indirect command field errors, and nested MDIO locking assumptions. Test signals include probing strapped address variants, multi-chip indirect access, timeout injection, and basic register read/write sanity before chip ID detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/smi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/smi.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/smi.h

## Purpose
Declares SMI command/data register fields, the SMI init function, and inline read/write dispatchers for the selected bus ops.

## Important APIs, Types, and Functions
Defines `MV88E6XXX_SMI_CMD`, `MV88E6XXX_SMI_DATA`, BUSY, Clause 22/45 mode and operation masks, device address mask, and register address mask. Exposes `mv88e6xxx_smi_init`, `mv88e6xxx_smi_read`, and `mv88e6xxx_smi_write`.

## Control Flow and State
Inline read/write helpers check `chip->smi_ops` and the relevant callback before dispatching, otherwise returning `-EOPNOTSUPP`. Runtime state is held in `chip->smi_ops`, `chip->bus`, and `chip->sw_addr`, initialized by `smi.c`.

## Dependencies and Integration Points
Includes `chip.h` and feeds the common mv88e6xxx bus abstraction. It is consumed by core register read/write helpers and therefore sits below port, global, PHY, TCAM, and other functional modules.

## Risks and Test Signals
Risks are missing ops initialization and macro drift from firmware/hardware command layout. Test signals include direct and indirect MDIO access tests, all supported addressing modes, and compile checks for inline fallback behavior when ops are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/smi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/switchdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/switchdev.c

## Purpose
Bridges mv88e6xxx hardware miss violations into Linux switchdev notifications, allowing locked FDB learning events to be reported to the bridge.

## Important APIs, Types, and Functions
Exports `mv88e6xxx_handle_miss_violation`. Internal helpers `__mv88e6xxx_find_vid` and `mv88e6xxx_find_vid` walk the VTU to map a filtering database ID back to a VLAN ID.

## Control Flow and State
On a miss violation, the code finds the VID for the supplied FID under the register lock, builds `switchdev_notifier_fdb_info` with `locked = true`, resolves the DSA port and its bridge port under RTNL, then calls `call_switchdev_notifiers(SWITCHDEV_FDB_ADD_TO_BRIDGE, ...)`. It does not persist state itself; the bridge/FDB layer handles the resulting notification.

## Dependencies and Integration Points
Depends on `global1.h` VTU walking, DSA port lookup, switchdev notifier APIs, RTNL locking, and ATU violation handling code that supplies the entry and FID.

## Risks and Test Signals
Risks include failing to find VID for valid FIDs, notifying after a port leaves a bridge, lock ordering between register lock and RTNL, and duplicate locked FDB events. Test signals include locked-port miss violation tests, bridge FDB notification observation, VLAN/FID mapping coverage, and port-unbridged error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/switchdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/switchdev.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/switchdev.h

## Purpose
Provides the switchdev integration declaration for mv88e6xxx ATU miss handling.

## Important APIs, Types, and Functions
Declares `mv88e6xxx_handle_miss_violation(struct mv88e6xxx_chip *chip, int port, struct mv88e6xxx_atu_entry *entry, u16 fid)`.

## Control Flow and State
No runtime logic. It exposes a single integration point that converts hardware ATU miss context into a switchdev FDB notification in `switchdev.c`.

## Dependencies and Integration Points
Includes `chip.h` for chip and ATU entry definitions. It is consumed by ATU/global interrupt or violation handling code.

## Risks and Test Signals
Risks are compile-time interface drift with the caller and `switchdev.c`. Test signals are successful builds with switchdev support and locked-FDB miss handling tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/switchdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/tcam.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/tcam.c

## Purpose
Implements TCAM hardware programming and ordered rule management for mv88e6xxx chips with TCAM support, backing tc flower offload.

## Important APIs, Types, and Functions
Exports `mv88e6xxx_tcam_entry_find`, `mv88e6xxx_tcam_entry_add`, `mv88e6xxx_tcam_entry_del`, and ops descriptors `mv88e6390_tcam_ops` and `mv88e6393_tcam_ops`. Static helpers write TCAM registers, wait for BUSY clear, read/load pages, flush entries, flush all entries, and program 6390/6393 entry pages.

## Control Flow and State
Software state is `chip->tcam.entries`, an ordered list keyed by priority and cookie with hardware index tracking. Insertions walk from the tail, move lower-priority entries down by flushing/re-adding them, assign the new index, and program the entry. Deletes flush the removed index, shift following entries up, flush the final stale slot, remove the list node, and free it. Hardware state is page-based TCAM key/action content plus DPV action registers.

## Dependencies and Integration Points
Depends on `chip->info->tcam_addr`, `chip->info->num_tcam_entries`, `chip->info->ops->tcam_ops`, list management, `mv88e6xxx_write`, `mv88e6xxx_wait_bit`, and port masks. `tcflower.c` constructs entries and calls these APIs under the register lock.

## Risks and Test Signals
Risks include list/hardware divergence on partial insert failure, not rolling back moved entries, off-by-one capacity/index errors, masked frame byte programming mistakes, and 6393 extension selection assumptions. Test signals include priority ordering tests, add/delete churn, ENOSPC behavior, hardware packet matches, trap DPV validation, and teardown after partial failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/tcam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/tcam.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/tcam.h

## Purpose
Declares TCAM match layout constants, destination port vector action modes, public TCAM entry APIs, and helper macros for filling byte-oriented match data.

## Important APIs, Types, and Functions
Defines `PAGE0_MATCH_SIZE`, `PAGE1_MATCH_SIZE`, `DPV_MODE_*`, `mv88e6xxx_tcam_entry_add`, `mv88e6xxx_tcam_entry_del`, `mv88e6xxx_tcam_entry_find`, and the `mv88e6xxx_tcam_match_set` macro. The inline `__mv88e6xxx_tcam_match_set` copies data and mask bytes into `struct mv88e6xxx_tcam_key`.

## Control Flow and State
Runtime logic is limited to copying match bytes. `BUILD_BUG_ON` in the macro enforces compile-time bounds when offsets and data sizes are constant. Persistent rule state lives in `struct mv88e6xxx_tcam_entry` and `chip->tcam.entries`, defined elsewhere.

## Dependencies and Integration Points
Requires chip/tcam structures from `chip.h` through includers. Used by `tcflower.c` to map flow dissector fields into TCAM frame offsets, and by `tcam.c` for entry management.

## Risks and Test Signals
Risks include incorrect offsets or endian treatment by callers, non-constant offsets weakening `BUILD_BUG_ON`, and match-size assumptions drifting from hardware. Test signals include compile checks for match bounds, tc flower add tests for each supported key, and packet-level validation of exact/masked matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/tcam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/tcflower.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/tcflower.c

## Purpose
Implements a minimal tc flower offload frontend that parses supported flow keys and installs/removes TCAM entries.

## Important APIs, Types, and Functions
Exports `mv88e6xxx_cls_flower_add`, `mv88e6xxx_cls_flower_del`, and `mv88e6xxx_flower_teardown`. Internal `mv88e6xxx_flower_parse_key` supports basic keys, control address type, and IPv4 source/destination addresses. Supported action is `FLOW_ACTION_TRAP`.

## Control Flow and State
Add validates TCAM support, parses keys into `mv88e6xxx_tcam_key`, locks registers, rejects duplicate cookies, allocates an entry, copies priority/cookie/key, translates trap to a DPV replace action targeting the CPU port, restricts source port vector to the ingress port, and calls `mv88e6xxx_tcam_entry_add`. Delete finds by cookie and delegates to TCAM delete. Teardown frees all software entries without hardware reprogramming, intended for driver cleanup.

## Dependencies and Integration Points
Depends on DSA switch private data, flow dissector APIs, netlink extack, TCAM helpers, port masks, and DSA upstream port lookup. It integrates with the DSA cls_flower callback surface.

## Risks and Test Signals
Risks include unsupported keys/actions returning clear extack messages, endian/offset mistakes for EtherType/IP fields, duplicate cookie handling, memory leaks on add failure, and teardown leaving stale hardware unless paired with hardware flush. Test signals include tc flower add/delete tests, trap-to-CPU packet delivery, unsupported key/action negative tests, and repeated add/delete ordering with priorities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/tcflower.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/tcflower.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/tcflower.h

## Purpose
Declares the mv88e6xxx tc flower offload entry points.

## Important APIs, Types, and Functions
Provides prototypes for `mv88e6xxx_cls_flower_add`, `mv88e6xxx_cls_flower_del`, and `mv88e6xxx_flower_teardown`.

## Control Flow and State
No runtime logic. State is managed by `tcflower.c` through allocated TCAM entries and `chip->tcam.entries`.

## Dependencies and Integration Points
Relies on DSA and flow offload types being visible through includers. Used by the main driver ops table and cleanup paths.

## Risks and Test Signals
Risks are prototype drift and missing declarations when TCAM/flower support changes. Test signals are builds with tc flower callbacks enabled and add/delete offload smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/tcflower.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/trace.c

## Purpose
Instantiates mv88e6xxx tracepoints by defining `CREATE_TRACE_POINTS` and including `trace.h`.

## Important APIs, Types, and Functions
No functions are defined directly. The file causes the tracepoint definitions in `trace.h` to emit storage and registration code in exactly one translation unit.

## Control Flow and State
No explicit control flow. Kernel tracepoint state is generated by the tracepoint macros during compilation.

## Dependencies and Integration Points
Depends on `trace.h` and the kernel tracepoint build system. Other mv88e6xxx files include `trace.h` without `CREATE_TRACE_POINTS` to use the generated trace events.

## Risks and Test Signals
Risks are duplicate tracepoint instantiation if another file defines `CREATE_TRACE_POINTS`, or missing events if this file is removed from the build. Test signals include successful module linking and events appearing under tracing for ATU/VTU violations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/trace.h

## Purpose
Defines trace events for mv88e6xxx ATU and VTU violation reporting.

## Important APIs, Types, and Functions
Declares event classes `mv88e6xxx_atu_violation` and `mv88e6xxx_vtu_violation`, then defines ATU member/miss/full events and VTU member/miss events. Payloads capture device name, source port ID, port vector or VID, MAC address for ATU, and FID.

## Control Flow and State
Trace macros generate static tracepoint metadata and fast assignment/print logic. No driver state is mutated. Event output formats show device, SPID, port vector/MAC/FID, or VID.

## Dependencies and Integration Points
Uses Linux tracepoint headers, device names, Ethernet address length, and local `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` so generated trace definitions resolve in the driver directory. Called from violation handling code elsewhere in the driver.

## Risks and Test Signals
Risks include ABI changes to trace event field names, format mismatch, and include-path breakage. Test signals include `trace-cmd`/ftrace visibility, formatted ATU/VTU violation records, and clean builds with `TRACE_HEADER_MULTI_READ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/Kconfig

## Purpose
Adds the kernel configuration option for the MaxLinear MxL862xx DSA switch driver.

## Important APIs, Types, and Functions
Defines `config NET_DSA_MXL862` as a tristate named "MaxLinear MxL862xx". It depends on `NET_DSA` and selects `CRC16` and `NET_DSA_TAG_MXL_862XX`.

## Control Flow and State
No runtime logic. Build-time state determines whether the driver is omitted, built-in, or modular, and ensures required CRC and tag-protocol support are selected.

## Dependencies and Integration Points
Integrates with the kernel Kconfig tree under DSA drivers. The selected tag protocol is required for packets between CPU and switch ports, while CRC16 is used by the host command transport.

## Risks and Test Signals
Risks include missing dependencies for MDIO/PHY features in other files or selecting a tagger that is not present. Test signals include `oldconfig`, built-in and module builds, and runtime DSA probe with MxL86252/MxL86282 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/Makefile

## Purpose
Defines build objects for the MxL862xx DSA driver.

## Important APIs, Types, and Functions
Builds `mxl862xx_dsa.o` when `CONFIG_NET_DSA_MXL862` is enabled. The composite object contains `mxl862xx.o` and `mxl862xx-host.o`.

## Control Flow and State
No runtime flow. Build composition decides that the host command transport is linked with the main DSA driver implementation.

## Dependencies and Integration Points
Integrates with Kbuild and the Kconfig symbol from `Kconfig`. The source list must remain synchronized with driver files and any future feature split.

## Risks and Test Signals
Risks include omitting new objects or leaving stale object names after refactors. Test signals are clean module/built-in builds and modpost symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx-api.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx-api.h

## Purpose
Defines the packed firmware API data structures and enums used by the MxL862xx host command layer and main DSA driver.

## Important APIs, Types, and Functions
Major ABI groups include `mdio_relay_data`, direct register modification, MAC table add/remove/read/query/clear, bridge allocation/config, bridge-port allocation/config, QoS meter config, extended VLAN filter/treatment/allocation/config, VLAN filter allocation/config, special tag settings, CTP/logical port assignment, STP port config, firmware version, port type enums, and RMON counters. Fields use `__le16`, `__le32`, `__le64`, and `__packed`.

## Control Flow and State
No executable control flow. The header describes command payloads exchanged with firmware. Persistent switch state represented here includes learned/static MAC entries, allocated bridge and bridge-port IDs, VLAN block IDs, meter IDs, port maps, special tag modes, STP states, and hardware counters.

## Dependencies and Integration Points
Depends on kernel bit macros and Ethernet address length. It pairs with command IDs in `mxl862xx-cmd.h` and transport in `mxl862xx-host.c`; higher-level `mxl862xx.o` fills these structures before calling `mxl862xx_api_wrap`.

## Risks and Test Signals
Risks are ABI packing/alignment mistakes, endian conversion omissions, firmware-version drift, invalid block/handle lifecycle, and large structures exceeding transport limits. Test signals include `pahole`/sizeof checks against firmware ABI, command round trips for each structure family, VLAN/bridge/FDB behavior, and RMON counter sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx-api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx-cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx-cmd.h

## Purpose
Defines MxL862xx firmware command IDs and MMD register window constants for host-to-firmware API calls.

## Important APIs, Types, and Functions
Constants describe MMD device/register layout (`CTRL`, `LEN_RET`, data register range), API command namespace "magic" bases, common config/register-mod commands, bridge/bridge-port/CTP/QoS/RMON/MAC/extended-VLAN/VLAN-filter/special-tag/STP commands, internal GPY read/write commands, firmware version command, and `MMD_API_MAXIMUM_ID`.

## Control Flow and State
No runtime logic. The constants are the command ABI consumed by `mxl862xx_api_wrap` callers and interpreted by firmware. The data window size constrains payload batching in `mxl862xx-host.c`.

## Dependencies and Integration Points
Used with payload structures from `mxl862xx-api.h` and the MDIO transport in `mxl862xx-host.c`. Main driver code maps DSA operations to these command IDs.

## Risks and Test Signals
Risks include duplicated register constants drifting from `mxl862xx-host.c`, wrong command IDs invoking unintended firmware operations, and namespace collisions. Test signals are command-specific integration tests, firmware version reads, FDB/VLAN/bridge setup, and static checks that transport constants remain consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx-cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx-host.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx-host.c

## Purpose
Implements the MxL862xx MDIO/MMD host transport, including CRC-6 protected command registers, CRC-16 protected payload data, command batching, reset, and CRC-error shutdown handling.

## Important APIs, Types, and Functions
Exports `mxl862xx_api_wrap`, `mxl862xx_reset`, `mxl862xx_host_init`, and `mxl862xx_host_shutdown`. Internal functions include CRC error work, `mxl862xx_crc6`, encode/verify helpers, raw register read/write, busy wait, `mxl862xx_issue_cmd`, data pagination helpers, reset-data optimization, and firmware error translation.

## Control Flow and State
`mxl862xx_api_wrap` takes the MDIO lock, waits for idle, optionally resets the firmware data buffer when many zero words are present, writes payload words plus CRC16 through the data window, pages data with SET_DATA commands, issues the API command, optionally reads response words with GET_DATA commands, verifies CRC16, and returns the firmware result. `mxl862xx_issue_cmd` encodes CRC6 into control/length registers, waits for BUSY clear, verifies response CRC6, and extracts signed firmware return values. CRC failures set `MXL862XX_FLAG_CRC_ERR` and schedule work that closes CPU-port conduits.

## Dependencies and Integration Points
Depends on MDIO Clause 45 access, bus `mdio_lock`, CRC16, workqueues, RTNL, DSA CPU ports, `mxl862xx_priv`, firmware command IDs, and the main driver API wrapper calls.

## Risks and Test Signals
Risks include CRC bit packing mistakes, odd-size payload boundary bugs, paging off-by-one errors, lock nesting issues, over-broad port shutdown on transient CRC errors, and duplicated MMD constants drifting from `mxl862xx-cmd.h`. Test signals include CRC6 known vectors, odd/even payload round trips, multi-page payloads, firmware CRC error injection, reset command verification, and concurrent API callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx-host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx-host.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx-host.h

## Purpose
Declares the public host transport interface for the MxL862xx driver.

## Important APIs, Types, and Functions
Prototypes are `mxl862xx_host_init`, `mxl862xx_host_shutdown`, `mxl862xx_api_wrap`, and `mxl862xx_reset`.

## Control Flow and State
No runtime logic. The declared functions initialize/cancel CRC error work, issue firmware API commands with optional readback and quiet error behavior, and perform software reset.

## Dependencies and Integration Points
Includes `mxl862xx.h` for `struct mxl862xx_priv` and flag/work definitions. Used by the main driver to initialize transport state and send all firmware-backed operations.

## Risks and Test Signals
Risks are signature drift with callers and missing shutdown during remove paths. Test signals include build coverage, probe/remove cycles, reset path tests, and API wrapper calls from FDB/VLAN/bridge/stat operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx-host.h -->
