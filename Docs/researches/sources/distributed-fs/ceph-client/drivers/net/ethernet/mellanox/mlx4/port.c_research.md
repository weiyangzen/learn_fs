# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/port.c

## Purpose
`port.c` is the mlx4 port resource and configuration layer. It manages per-port MAC tables, VLAN tables, RoCE GID tables, multi-function bonding mirrors, SET_PORT command filtering and rewriting, InfiniBand port capability aggregation, Ethernet port attributes, multicast/VLAN/stat wrappers, transceiver EEPROM reads, and traffic-class reporting.

## Important APIs, types, and functions
- Table initialization: `mlx4_init_mac_table()`, `mlx4_init_vlan_table()`, and `mlx4_init_roce_gid_table()`.
- MAC lifecycle: `__mlx4_register_mac()`, `mlx4_register_mac()`, `__mlx4_unregister_mac()`, `mlx4_unregister_mac()`, `__mlx4_replace_mac()`, and `mlx4_get_base_qpn()`.
- VLAN lifecycle: `mlx4_find_cached_vlan()`, `__mlx4_register_vlan()`, `mlx4_register_vlan()`, `__mlx4_unregister_vlan()`, and `mlx4_unregister_vlan()`.
- Bonding helpers: `mlx4_bond_mac_table()`, `mlx4_unbond_mac_table()`, `mlx4_bond_vlan_table()`, and `mlx4_unbond_vlan_table()`.
- RoCE GID partitioning: `mlx4_get_slave_num_gids()`, `mlx4_get_base_gid_ix()`, `mlx4_reset_roce_gids()`, `mlx4_get_slave_from_roce_gid()`, and `mlx4_get_roce_gid_from_slave()`.
- SET_PORT paths: `mlx4_common_set_port()`, `mlx4_SET_PORT_wrapper()`, `mlx4_SET_PORT()`, `mlx4_SET_PORT_general()`, `mlx4_SET_PORT_qpn_calc()`, `mlx4_SET_PORT_user_mtu()`, `mlx4_SET_PORT_user_mac()`, `mlx4_SET_PORT_fcs_check()`, `mlx4_SET_PORT_VXLAN()`, and `mlx4_SET_PORT_BEACON()`.
- Module info: `mlx4_get_module_info()` plus `mlx4_get_module_id()`, SFP/QSFP offset helpers, `struct mlx4_cable_info`, and cable MAD error decoding.

## Control flow and integration
MAC and VLAN registration search the local per-port tables for an existing entry, increment references on reuse, otherwise choose a free slot, mark it valid, and push the whole table to firmware with `MLX4_CMD_SET_PORT`. In multi-function mode public register/unregister APIs call wrapped resource commands instead. In multi-function Ethernet bonding, registration and unregistration may mirror entries to the opposite port at the same index so virtual functions can fail over consistently.

The SET_PORT wrapper converts a slave-visible port to the physical port and sends requests through `mlx4_common_set_port()`. For Ethernet, non-master slaves are restricted to general MTU/user-MTU and GID-table changes. RQP calculation commands are rewritten with the master's base QPN. General commands aggregate maximum MTU/user-MTU across functions and preserve global pause settings unless the master requested the change. GID-table updates validate no duplicate GIDs within the request or against the rest of the port table, merge the slave's partition into the full table, then issue SET_PORT. For InfiniBand, capability masks are aggregated across slaves, with SM and device-management capabilities blocked for guests where required.

Transceiver reads use `MLX4_CMD_MAD_IFC` attribute `0xFF60`. The code first reads the module ID, derives SFP or QSFP I2C address/page/offset semantics, caps each request to `MODULE_INFO_MAX_READ`, avoids crossing the 256-byte page boundary, and returns either the read byte count or a negative command/MAD status.

## State and persistence behavior
Per-port software state lives in `mlx4_priv(dev)->port[port]`: MAC/VLAN entries, reference counters, duplicate flags, RoCE GID tables, base QPN, and mutexes. Multi-function master state records per-slave MTU, user MTU, pause, and InfiniBand capability masks, plus per-port maxima. Hardware-visible state is persistent until reprogrammed: MAC and VLAN tables, RoCE GID tables, port MTU/pause/user MAC/FCS/VXLAN/beacon settings, multicast filters, and IB port capabilities.

## Dependencies
The file depends on mlx4 command mailboxes, `MLX4_CMD_SET_PORT`, `MLX4_CMD_MAD_IFC`, resource reservation commands, mlx4 multi-function helpers, Ethernet and VLAN constants, RoCE GID constants, `mlx4_stats.h`, endian helpers, bitmap helpers for active-port/slave calculations, and device capability fields.

## Risks
- MAC/VLAN bonding requires identical indices on both ports. Partial firmware failure while adding or removing mirrored entries can leave software and hardware tables inconsistent.
- Some duplicate cleanup paths adjust totals on one table while touching another; table counters should be checked carefully after bonding transitions.
- SET_PORT policy is security-sensitive in SR-IOV: guest requests must not change global pause, beacon, SM capability, device management, or unrelated GID slots.
- GID partition math divides VF GID space by active-port membership; zero or stale VF counts can cause bad indexing.
- Module EEPROM reads have page-boundary and high-page quirks; callers must handle short reads and a silent zero-byte return for unsupported SFP high pages.

## Test signals
Test MAC/VLAN register, duplicate register, unregister, replace, exhaustion, and mirrored bond/unbond flows on one-port and two-port devices. Exercise slave SET_PORT denial/allow cases, MTU aggregation across VFs, pause preservation, RoCE GID duplicate rejection and reset, IB capability aggregation, VXLAN and FCS SET_PORT commands, module EEPROM reads for SFP/QSFP/QSFP+/QSFP28, unsupported module IDs, and command failure injection.
