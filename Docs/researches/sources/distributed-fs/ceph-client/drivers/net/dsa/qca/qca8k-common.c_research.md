# sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k-common.c

## Purpose

This file contains shared QCA8K switch operations used by the QCA8K device driver: basic regmap wrappers, MIB descriptor data, FDB and VLAN table programming, ethtool stats, EEE configuration, bridge/STP membership handling, port enable/disable and MTU, ageing, MDB/mirror operations, VLAN callbacks, LAG offload, and switch ID validation.

## Important APIs, Types, and Functions

- `ar8327_mib[]` describes QCA832x/QCA833x MIB counter names, offsets, and 32/64-bit sizes.
- `qca8k_read()`, `qca8k_write()`, and `qca8k_rmw()` wrap `regmap_read/write/update_bits`.
- `qca8k_readable_table` constrains valid readable register ranges for the QCA8K regmap.
- FDB helpers include `qca8k_fdb_read()`, `qca8k_fdb_write()`, `qca8k_fdb_access()`, `qca8k_fdb_next()`, `qca8k_fdb_add()`, `qca8k_fdb_del()`, `qca8k_fdb_search_and_insert()`, `qca8k_fdb_search_and_del()`, and public DSA callbacks.
- VLAN helpers include `qca8k_vlan_access()`, `qca8k_vlan_add()`, `qca8k_vlan_del()`, and DSA VLAN callbacks.
- Bridge and port state APIs include `qca8k_port_stp_state_set()`, `qca8k_port_bridge_flags()`, `qca8k_port_bridge_join()`, `qca8k_port_bridge_leave()`, `qca8k_port_enable()`, and `qca8k_port_disable()`.
- LAG helpers include `qca8k_lag_can_offload()`, `qca8k_lag_setup_hash()`, `qca8k_lag_refresh_portmap()`, and the public join/leave callbacks.

## Control Flow

FDB operations serialize on `priv->reg_mutex`, write the ATU data registers, trigger an ATU function command, poll the busy bit, and optionally read back result status. Static FDB add/del use `QCA8K_FDB_LOAD` and `QCA8K_FDB_PURGE`; MDB add/del search for an existing entry, mutate the port mask, and reinsert or purge as needed. Dumps iterate with `QCA8K_FDB_NEXT` up to `QCA8K_NUM_FDB_RECORDS`.

VLAN operations similarly serialize on `reg_mutex`, issue VTU read/load/purge commands, update per-port egress mode bits in `QCA8K_REG_VTU_FUNC0`, and purge the VLAN when the last member is removed. PVID handling additionally updates egress VLAN and ingress CVID/SVID registers.

Bridge/STP logic maps Linux bridge states to hardware lookup states and toggles learning based on DSA port learning state. Membership updates connect a joining port to other ports in the same bridge unless both are isolated, update other ports' member masks, and finally update the joining/leaving port's mask to include the CPU port and eligible peers.

Mirroring first validates that the requested source is not already mirrored and that the single hardware monitor port is compatible. It sets the global mirror port and then either ingress mirror enable in lookup control or egress mirror enable in HOL control. Removal clears source bits and resets the monitor port to `0xF` when no mirror sources remain.

LAG join validates DSA LAG ID, max four members, hash TX type, and L2/L2+L3 hash mode. The hash selector is global, so different LAGs must share one hash mode unless only one LAG is configured. Portmap refresh updates trunk member and member-ID registers.

## State and Persistence

The file mutates `qca8k_priv` fields such as `port_enabled_map`, `port_isolated_map`, `mirror_rx`, `mirror_tx`, and `lag_hash_mode`. It also writes persistent hardware tables and registers: ATU/FDB, VTU/VLAN, port lookup membership, learning, STP state, EEE, MIB enablement, mirror selection, MTU, ageing, and LAG trunk tables. These settings persist until overwritten or switch reset. The common code relies on `reg_mutex` for table operations with command/busy registers.

## Dependencies and Integration Points

This code depends on DSA data structures, Linux bridge flags/states, switchdev VLAN/MDB objects, ethtool stat strings, regmap, and the definitions in `qca8k.h`. The DSA ops table in `qca8k-8xxx.c` exposes these functions to the kernel networking stack.

## Risks and Edge Cases

Several helpers return generic or unusual errors; for example ATU table-full in `qca8k_fdb_access()` returns `-1` rather than a specific errno. `qca8k_port_fdb_dump()` ignores the final `ret` and always returns 0, so callback errors may be hidden. `qca8k_port_mirror_del()` logs an error unconditionally through the `err:` label even when removal succeeds. MTU changes temporarily disable enabled CPU ports to avoid hardware panic; failures leave re-enable best-effort but should be tested. LAG member-ID update assumes an available slot and does not explicitly handle "no slot found" before programming index `i`.

## Test Signals

Signals include accurate ethtool stat names/counts for QCA832x and QCA833x, FDB add/delete/dump behavior with VID 0 defaulting to VID 1, MDB shared-port-mask behavior, VLAN add/delete/purge including last-member removal, PVID register updates, STP and learning transitions, isolated bridge ports not forwarding to each other, mirror add/delete enforcing one monitor port, MTU changes under traffic, ageing time quantization, and LAG offload rejection/acceptance for supported hash modes and member counts.
