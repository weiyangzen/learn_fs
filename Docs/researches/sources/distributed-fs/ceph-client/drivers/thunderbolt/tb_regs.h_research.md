# sources/distributed-fs/ceph-client/drivers/thunderbolt/tb_regs.h

## Purpose
`tb_regs.h` defines Thunderbolt and USB4 config-space register layouts, capability IDs, port/router type constants, register offsets, bit masks, and packed hop-entry structures. It is the low-level register contract used by switch, port, path, link-controller, TMU, USB4, DP, PCIe, USB3, wake, and sideband code. The file does not perform register I/O itself; it names the offsets and fields that other files read and write through the config-channel wrappers declared in `tb.h`.

## Important APIs, Types, and Functions
- `TB_ROUTE_SHIFT` defines the 8-bit-per-port route encoding used by topology helpers.
- `TB_MAX_CONFIG_RW_LENGTH` defines the practical maximum dword count for config read/write transactions.
- Capability enums `tb_switch_cap`, `tb_switch_vse_cap`, and `tb_port_cap` identify switch and port capability chains.
- `enum tb_port_state` names PHY states such as disabled, connecting, up, CL0s, CL1, CL2, and unplugged.
- Packed capability structures include `tb_cap_basic`, `tb_cap_extended_short`, `tb_cap_extended_long`, `tb_cap_any`, `tb_cap_link_controller`, `tb_cap_phy`, `tb_eeprom_ctl`, and `tb_cap_plug_events`.
- `struct tb_regs_switch_header` and `struct tb_regs_port_header` are cached in `struct tb_switch` and `struct tb_port` respectively.
- Router register constants cover common router status/control registers, sleep/wake bits, USB4 router operation registers, and `enum usb4_switch_op`.
- TMU router and adapter constants define frequency windows, timestamp intervals, uni/enhanced modes, disable bits, and timing averages.
- `enum tb_port_type` names inactive, lane/null, NHI, DP IN/OUT, PCIe UP/DOWN, and USB3 UP/DOWN adapters.
- Adapter register constants cover basic adapter buffer/lock registers, lane link width/speed/CLx/asymmetric fields, USB4 port sideband and wake registers, DP adapter HPD/bandwidth/group/capability fields, PCIe enable/encapsulation fields, and USB3 bandwidth fields.
- `struct tb_regs_hop` defines the two-dword hop table entry used to route packets through a switch.
- Link-controller and low-power constants define plug events, PCIe command registers, CP low power fields, link controller descriptors, sink allocation, power, port mode, wake/sleep controls, link attributes, and xHCI connection requests.

## Control Flow
Register access flows through helper APIs in other files. For example, switch allocation reads `tb_regs_switch_header` from port 0 switch config space, port initialization reads `tb_regs_port_header` from each adapter, capability walkers use the capability structs and IDs, path activation writes `struct tb_regs_hop` entries in the hops config space, TMU helpers program `TMU_RTR_*` and `TMU_ADP_*` registers, USB4 router operations use `ROUTER_CS_26` fields with `enum usb4_switch_op`, and DP/USB3 bandwidth code uses the adapter-specific masks to query, estimate, request, allocate, and release bandwidth.

`tb.c` depends on these definitions indirectly through helpers. For instance, DP resource and bandwidth handling uses DP adapter group, estimated bandwidth, requested bandwidth, and allocated bandwidth fields; Gen 4 asymmetric transitions use lane adapter width masks and USB4 port asymmetric control; redrive and wake handling use DP resource and low-power/link-controller state; and tunnel path programming ultimately materializes as hop register writes.

## State and Persistence Behavior
The file defines hardware state layout, not software storage. Some values are cached into `struct tb_switch::config` and `struct tb_port::config` in memory, while most other fields are read or written directly by helper functions when needed. Hardware persists these registers until reset, unplug, firmware action, or driver reconfiguration. During suspend/resume, `tb.c` restores router/link/TMU state by calling helpers that use these register definitions.

Fields such as route, upstream port number, max port number, adapter type, max HopIDs, link width, CLx enable bits, DP group IDs, DP estimated/allocated/requested bandwidth, USB3 allocated bandwidth, and hop enable bits are the hardware-backed state that higher layers reason about.

## Dependencies and Integration Points
The header includes `linux/types.h` and relies on kernel bit helpers such as `BIT()` and `GENMASK()`. It is included by `tb.h` and used across the Thunderbolt driver. It integrates tightly with control-channel config spaces from `tb_msgs.h`: config packets choose switch, port, hops, or counters space and these constants define the offsets and bit meanings inside those spaces.

Router operation opcodes here are used by USB4 router operation helpers and by ICM USB4 switch-op proxy messages. DP register definitions feed the DP tunneling and bandwidth allocation code. Lane, TMU, low-power, and link-controller constants feed CLx/TMU/link configuration code. Hop entries feed path and tunnel activation.

## Risks
- Packed bitfield layouts must match hardware config-space definitions exactly. Any mismatch corrupts low-level router or adapter programming.
- Several fields are marked unknown or TODO. Code should avoid making assumptions beyond the named masks.
- `TB_MAX_CONFIG_RW_LENGTH` is lower than the theoretical packet data array in `tb_msgs.h`; callers must obey this practical limit.
- Duplicate-looking DP `ADP_DP_CS_8` definitions appear for bandwidth mode bits and requested bandwidth. Maintainers must avoid inconsistent edits.
- Link width and direction constants are easy to invert because upstream-port perspective differs from downstream-port and host-router perspective.
- Router and adapter registers have generation-specific semantics, especially USB4 v1/v2, Titan Ridge TMU bits, and asymmetric Gen 4 controls.

## Test Signals
Low-level tests should validate config-space reads of switch and port headers, capability-chain parsing, PHY state reads, lane speed/width reads and writes, lane bonding, CLx enable/disable, TMU configuration, USB4 router operations, hop entry programming, DP HPD/resource/bandwidth registers, USB3 bandwidth allocation/release, PCIe adapter enable and xHCI link-controller requests, wake/sleep bits, and sideband transactions.

Regression signals include correct route depth decoding, no config read/write longer than `TB_MAX_CONFIG_RW_LENGTH`, correct DP bandwidth granularity/group/estimated allocation behavior, successful asymmetric link transitions on Gen 4 hardware, and successful resume restoration of link/TMU/CLx state.
