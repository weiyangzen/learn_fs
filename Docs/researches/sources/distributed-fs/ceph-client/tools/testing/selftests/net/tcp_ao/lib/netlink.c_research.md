# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/netlink.c

Purpose: this file provides low-level rtnetlink helpers for TCP-AO selftests. It creates veth pairs, assigns addresses, adds routes, brings links up, and creates VRF devices without shelling out to `ip`.

Important APIs and functions: public functions are `add_veth`, `ip_addr_add`, `ip_route_add`, `ip_route_add_vrf`, `link_set_up`, and `add_vrf`. Internal helpers include `netlink_sock`, `netlink_check_answer`, `rtattr_pack`, `rtattr_begin`, `rtattr_end`, `veth_pack_peerb`, `__add_veth`, `__ip_addr_add`, `__ip_route_add`, `__link_set_up`, and `__add_vrf`.

Control flow: each public function opens a `NETLINK_ROUTE` socket, builds an RTM request with nested attributes, sends it, waits for an `NLMSG_ERROR` ACK, closes the socket, and returns the kernel error code. Veth creation nests `IFLA_LINKINFO`, `IFLA_INFO_DATA`, and `VETH_INFO_PEER` with peer namespace fd. VRF creation nests `IFLA_VRF_TABLE`.

State and persistence: the helpers change kernel network namespace state by creating links, routes, addresses, and VRF devices. Sequence numbers are randomized per socket. There is no userspace persistent state beyond the created kernel objects.

Dependencies and integration points: used by `setup.c`, `kconfig.c`, `bench-lookups.c`, and key-management VRF setup through declarations in `aolib.h`. It depends on Linux rtnetlink UAPI, `randomize_buffer`, and interface names being visible in the current namespace.

Risks: `netlink_sock` uses `seq_nr++` instead of `(*seq_nr)++` when reusing an existing socket, so intended sequence advancement would not occur on reuse; current public wrappers open fresh sockets, limiting impact. Route additions hard-code host prefix lengths and route table fields, so they are not generic route helpers. Some functions return negative kernel error codes and callers must handle `-EEXIST` explicitly.

Test signals: successful helpers return zero. Failures print netlink diagnostics and return negative errno, causing callers to skip, fail, or call `test_error`.
