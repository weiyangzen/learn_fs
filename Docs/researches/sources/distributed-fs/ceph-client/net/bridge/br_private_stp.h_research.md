# sources/distributed-fs/ceph-client/net/bridge/br_private_stp.h

## Purpose
`br_private_stp.h` declares the internal Spanning Tree Protocol contract: BPDU constants, timer/path-cost limits, the in-kernel config BPDU representation, and STP state-machine/transmit APIs shared across STP implementation files.

## Important APIs, types, and functions
- `BPDU_TYPE_CONFIG` and `BPDU_TYPE_TCN` define supported BPDU kinds.
- Timer bounds encode IEEE 802.1D ranges for hello time, forward delay, and max age; path-cost bounds protect port configuration.
- `struct br_config_bpdu` carries topology flags, root/bridge IDs, root path cost, port ID, and STP timers in jiffies.
- `br_is_designated_port()` tests whether a port's designated bridge/port match the local bridge.
- Prototypes cover root transition, BPDU generation/reception, configuration update, port state selection, topology-change handling, and BPDU send helpers.

## Control flow
The header links `br_stp.c` state-machine logic, `br_stp_bpdu.c` packet encoding/decoding, and `br_stp_timer.c` timer callbacks. Callers hold `br->lock` for most STP state-machine functions, as documented in comments and enforced by implementation patterns.

## State and persistence
No state is stored in the header itself. It defines constants and structs used to mutate `struct net_bridge` and `struct net_bridge_port` STP fields declared in `br_private.h`.

## Dependencies and integration points
It depends on bridge ID and port types from `br_private.h` and is included by STP implementation, netlink/sysfs setters, and bridge initialization paths.

## Risks and edge cases
Timer limits are user-visible through netlink/sysfs and must match validation in setters. The designated-port test assumes bridge IDs are 8-byte comparable. Callers must respect bridge-lock requirements to avoid inconsistent root/port selection.

## Test signals
Compile and runtime STP tests should cover timer validation boundaries, designated-port detection, config and TCN BPDU handling, and state changes with STP disabled, kernel STP, and user STP modes.
