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
