# sources/distributed-fs/ceph-client/net/mptcp/pm_userspace.c

## Purpose

`pm_userspace.c` implements the userspace path-manager backend. It lets a netlink controller, identified by an MPTCP token, announce/remove local addresses, create/destroy subflows, set backup flags, and query per-socket userspace-managed local endpoint state.

## Important APIs, types, and functions

- `mptcp_pm_userspace`: PM backend registered under the name `userspace`.
- `mptcp_userspace_pm_free_local_addr_list()`: frees per-socket userspace PM endpoint entries.
- `mptcp_userspace_pm_get_local_id()` and `mptcp_userspace_pm_is_backup()`: lookup helpers used by common PM/subflow code.
- `mptcp_pm_nl_announce_doit()`: validates and queues an ADD_ADDR announcement for a token-selected MPTCP socket.
- `mptcp_pm_nl_remove_doit()` and `mptcp_pm_remove_addr_entry()`: remove announced or subflow-backed local addresses and generate RM_ADDR signaling.
- `mptcp_pm_nl_subflow_create_doit()` and `mptcp_pm_nl_subflow_destroy_doit()`: userspace-requested subflow lifecycle operations.
- `mptcp_userspace_pm_set_flags()`: updates local entry backup flags and sends MP_PRIO.
- `mptcp_userspace_pm_dump_addr()` and `mptcp_userspace_pm_get_addr()`: token-scoped endpoint reporting.

## Control flow

Most netlink operations start with `mptcp_userspace_pm_get_sock()`, which validates `MPTCP_PM_ATTR_TOKEN`, resolves it via `mptcp_token_get_sock()`, verifies `mptcp_pm_is_userspace()`, and returns a referenced MPTCP socket. Address operations parse attributes with the shared parser from `pm_netlink.c`.

Announce flow appends a local entry, allocates an announce-list item, increments `add_addr_signaled`, calls `mptcp_pm_announce_addr()`, and schedules an ACK. Remove flow handles ID 0 specially because it can correspond to the initial subflow, otherwise deletes the local entry by ID, removes matching announcement/subflow state, sends RM_ADDR, then frees the entry with RCU-aware cleanup and socket memory accounting adjustment. Subflow create validates local/remote family compatibility, records a local entry with SUBFLOW flag, calls `__mptcp_subflow_connect()`, and rolls back the entry on failure. Destroy maps local/remote tuples to an existing subflow and closes it through `mptcp_subflow_shutdown()` and `mptcp_close_ssk()`.

## State and persistence

Userspace PM state is per `mptcp_sock` in `msk->pm.userspace_pm_local_addr_list`, protected by `msk->pm.lock`. Entries are socket-accounted allocations from `sock_kmemdup()` and carry address, flags, ifindex, and ID. Counters such as `local_addr_used`, `extra_subflows`, and `add_addr_signaled` mirror list and signaling state. The file deliberately keeps removed entries in some remote-close cases so IDs are not immediately reused incorrectly.

## Dependencies and integration points

It relies on `protocol.h` PM structures, common netlink parsing from `pm_netlink.c`, token lookup, common PM helpers such as `mptcp_pm_alloc_anno_list()`, `mptcp_pm_remove_addr()`, `mptcp_pm_mp_prio_send_ack()`, and subflow helpers from the MPTCP core. It increments MPTCP MIB counters for subflow removal and registers with the PM registry via `mptcp_pm_register()`.

## Risks and edge cases

ID management is subtle: ID 0 needs special handling, duplicate address/ID combinations are rejected unless both match, and ID reuse is intentionally conservative. Locking crosses socket locks, PM spinlocks, RCU list deletion, and subflow locks; ABBA regressions are a main risk. IPv4-mapped IPv6 normalization in destroy must match actual subflow tuples. A TODO notes missing refcounting for address entries that could be used multiple times, such as fullmesh-style cases.

## Test signals

Coverage should include token validation, userspace-PM-only rejection, announce/remove of signaled addresses, ID 0 removal, create/destroy subflow by tuple, MP_PRIO backup flag updates, dump/get address APIs, duplicate address/ID rejection, and IPv4/IPv6 tuple matching. MPTCP PM selftests and packet traces for ADD_ADDR, RM_ADDR, MP_JOIN, and MP_PRIO are the strongest behavioral signals.
