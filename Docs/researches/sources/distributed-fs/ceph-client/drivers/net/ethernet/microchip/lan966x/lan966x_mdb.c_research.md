# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_mdb.c

Purpose: handles switchdev multicast database offload for LAN966x. It maintains multicast group membership, allocates shared PGIDs for L2 multicast destinations, encodes IPv4/IPv6 multicast entries for special MAC table entry types, and updates CPU-copy behavior as VLAN membership changes.

Important APIs and functions: lifecycle functions are `lan966x_mdb_init` and `lan966x_mdb_deinit`. Switchdev object handlers are `lan966x_handle_port_mdb_add` and `lan966x_handle_port_mdb_del`. VLAN interaction APIs are `lan966x_mdb_write_entries`, `lan966x_mdb_erase_entries`, `lan966x_mdb_clear_entries`, and `lan966x_mdb_restore_entries`.

Control flow: MDB add classifies the MAC as IPv4 multicast, IPv6 multicast, or generic L2. IPv4/IPv6 entries encode the destination port mask into bytes of the MAC value and use `lan966x_mac_ip_learn`, avoiding PGID allocation. L2 entries allocate or reuse a general PGID with the same port mask, program `ANA_PGID`, and learn a locked MAC entry pointing at that PGID. Delete paths remove CPU or front-port membership, forget the old MAC encoding, drop PGID references, delete empty entries, or re-learn updated entries. VLAN write/erase helpers add or remove CPU copy for entries whose bridge requested CPU membership.

State and persistence: `lan966x->mdb_entries` stores MAC, VID, front/CPU port mask, PGID pointer, and CPU-copy reference count. `lan966x->pgid_entries` stores PGID index, port mask, and refcount so L2 multicast groups sharing a port set reuse hardware PGIDs. Hardware state persists in ANA PGID entries and MAC table entries.

Dependencies and integration points: depends on switchdev MDB objects, bridge-master detection for CPU port membership, VLAN CPU membership helpers, MAC table learn/forget APIs, PGID constants from the main header, and multicast address classification conventions.

Risks: PGID resources are limited to `PGID_GP_START..PGID_GP_END`, so L2 multicast can fail with `-ENOSPC`. Error paths after PGID allocation or MAC forget/relearn can leave software and hardware out of sync. CPU-copy handling differs between IP multicast and L2 multicast and depends on VLAN membership callbacks. `lan966x_mdb_restore_entries` reuses a `cpu_copy` variable across loop iterations, which is risky if false is not reset for each IP entry.

Test signals: bridge MDB add/delete for IPv4, IPv6, and L2 multicast; multiple groups sharing a port mask; PGID exhaustion; bridge CPU port joins/leaves VLAN; VLAN clear/restore cycles; duplicate CPU-copy references; teardown purge; multicast traffic forwarding and CPU copy behavior.
