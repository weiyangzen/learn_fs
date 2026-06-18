# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_port.h

## Purpose

`nfp_port.h` defines the common NFP port abstraction and MAC statistics offsets. It is the interface used by netdevs, representors, ethtool, devlink, app code, and PF port-refresh code to represent physical NIC ports, logical PF ports, and logical VF ports.

## Important APIs, Types, and Functions

Important definitions are `enum nfp_port_type`, `enum nfp_port_flags`, speed bitmap indexes, and `struct nfp_port`. The structure stores netdev/app links, devlink port, link callback, TC offload count, physical ETH-table data, MAC stats base, supported speeds, PF/VF IDs, split-port metadata, vNIC control memory, and list membership. The header declares port netdev ops helpers, ETH-table accessors, physical-port init, refresh functions, devlink port register/unregister, and `nfp_port_ethtool_ops`.

## Control Flow

The header supports lifecycle flows where app/PF code allocates a port, fills physical or vNIC-specific union fields, registers a devlink port, associates it with a netdev/representor, and later refreshes or frees it. The inline `nfp_port_is_vnic()` quickly distinguishes PF/VF logical ports from physical ports for stats and ethtool handling.

## State and Persistence Behavior

Port objects persist the driver's view of hardware topology and offload state. `NFP_PORT_CHANGED` tracks stale physical-port data between ETH-table refreshes. MAC stats offsets define persistent firmware accumulator locations used by representor and ethtool stats.

## Dependencies and Integration Points

It depends on Linux devlink, netdev physical item IDs, NFP app/PF forward declarations, NSP ETH-table types, and ethtool. MAC stats offsets must match firmware `_mac_stats` layout and are consumed in `nfp_net_ethtool.c` and `nfp_net_repr.c`.

## Risks and Edge Cases

The union requires callers to branch on `port->type` before accessing fields. Physical ports may transition to `NFP_PORT_INVALID` after firmware configuration changes. MAC stat offsets are ABI-like and any mismatch skews stats. `tc_offload_cnt` is documented as boolean-like, so consumers should not depend on exact count semantics unless app code defines them.

## Test Signals

Compile all port consumers, validate devlink port registration for each type, exercise ETH-table invalidation, compare MAC stats offsets against firmware dumps, and check feature/offload behavior for physical and vNIC ports.
