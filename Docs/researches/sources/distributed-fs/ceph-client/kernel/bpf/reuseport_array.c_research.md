# sources/distributed-fs/ceph-client/kernel/bpf/reuseport_array.c

Purpose: implements the `BPF_MAP_TYPE_REUSEPORT_SOCKARRAY` storage for sockets participating in SO_REUSEPORT groups. It lets userspace update slots with socket FDs, allows BPF reuseport selection to look up sockets, and coordinates socket detach/free through socket callback user data. The source was read as a complete 353-line file.

Important APIs/functions: `bpf_sk_reuseport_detach`, `reuseport_array_alloc_check`, `reuseport_array_lookup_elem`, `reuseport_array_delete_elem`, `reuseport_array_free`, `reuseport_array_alloc`, `bpf_fd_reuseport_array_lookup_elem`, `bpf_fd_reuseport_array_update_elem`, `reuseport_array_get_next_key`, `reuseport_array_mem_usage`, and `reuseport_array_ops`. Important type: `struct reuseport_array` with RCU socket pointer slots.

Control flow: allocation delegates most validation to array map checks but requires value size to be `u32` or `u64`. Update converts the supplied value to an FD, resolves the socket, performs quick validation, then under `reuseport_lock` and the new socket callback lock revalidates socket family/protocol/type, hashed/reuseport/RCU-free state, user-data availability, and flag semantics. It stores a flagged pointer to the target slot in `sk_user_data`, RCU-publishes the socket in the array slot, and clears old socket user data if replacing. Delete locks `reuseport_lock`, clears the socket's user data, and clears the RCU slot. Free walks slots under RCU and socket callback locks to clear user data before freeing the array.

State and persistence: map slots hold RCU `struct sock *` pointers. Each attached socket stores a flagged pointer back to its array slot in `sk_user_data`, allowing `bpf_sk_reuseport_detach` to null the slot on socket close/disconnect. Map memory persists until map free; socket references come from the FD during update and reuseport/socket lifetime rules thereafter.

Dependencies/integration: uses socket reuseport core, `reuseport_lock`, `sk_callback_lock`, `sockfd_lookup`, socket cookies, array map allocation checks, BPF map ops, BTF map IDs, RCU, and socket user-data flags `SK_USER_DATA_BPF`/`SK_USER_DATA_NOCOPY`.

Risks and edge cases: socket eligibility checks are race-sensitive and repeated under locks. `sk_user_data` must not already be used. Free intentionally does not take `reuseport_lock` and relies on callback locks plus RCU to race safely with detach. Value size controls whether lookup returns a cookie through the syscall FD path. The map ops do not expose update in `reuseport_array_ops`; specialized FD update helper is used.

Test signals: reuseport sockarray selftests for UDP/TCP IPv4/IPv6 sockets, FD update and cookie lookup, delete/free while sockets close, `BPF_NOEXIST`/`BPF_EXIST` behavior, unsupported sockets, busy `sk_user_data`, and RCU/KASAN stress.
