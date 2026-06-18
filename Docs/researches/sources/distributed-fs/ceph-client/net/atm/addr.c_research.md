# sources/distributed-fs/ceph-client/net/atm/addr.c

Purpose: manages local ATM service addresses associated with an `atm_dev`, including normal local addresses and LECS addresses.

Important APIs, types, and functions: public functions are `atm_reset_addr`, `atm_add_addr`, `atm_del_addr`, and `atm_get_addr`, declared in `addr.h`. Helpers `check_addr`, `identical`, and `notify_sigd` validate addresses, compare private/public address fields, and notify the ATM signaling daemon of interface address changes.

Control flow: add/delete validate `sockaddr_atmsvc`, select either `dev->lecs` or `dev->local`, take `dev->lock`, check for duplicates or matching entries, mutate the list, release the lock, and notify signaling for local address changes. Reset removes all entries from the selected list. Get counts entries under lock, copies them to a temporary buffer, then copies as many as fit to userspace.

State and persistence: state is the `atm_dev_addr` list entries stored on each `atm_dev`. It is runtime-only and protected by the device spinlock. Local address changes trigger `sigd_enq(... as_itf_notify ...)`.

Dependencies and integration points: depends on ATM core structures, signaling (`sigd_enq`), `copy_to_user`, and list operations. Used by ATM ioctl/resource paths to maintain addresses visible through sysfs and signaling.

Risks: `atm_get_addr` allocates `total` bytes while holding a spinlock with `GFP_ATOMIC`; very large address lists can fail. It copies `min(total, size)` but returns `-E2BIG` when user buffer is too small. Address validation relies on public address NUL termination and private-address first byte semantics.

Test signals: add duplicate addresses, delete missing addresses, reset local versus LECS lists, query with exact/small/large user buffers, signaling notification on local changes only, invalid family/public-string termination, and concurrent sysfs/ioctl reads under lockdep.
