# sources/distributed-fs/ceph-client/net/mctp/af_mctp.c

Purpose: implements the AF_MCTP datagram socket family, including bind/connect, sendmsg/recvmsg, tag allocation ioctls, socket option for extended addressing, socket hash/unhash, key expiry, and module init/exit.

Important APIs and functions: `mctp_bind()`, `mctp_connect()`, `mctp_sendmsg()`, `mctp_recvmsg()`, `mctp_setsockopt()/getsockopt()`, `mctp_ioctl_alloctag()/droptag()`, `mctp_sk_hash()/unhash()`, `mctp_sk_expire_keys()`, and `mctp_pf_create()`. Module init registers socket family, proto, routes, neighbours, and devices.

Control flow and state: bind records local EID/net/type and optional connected peer, then hashes into per-net bind buckets. Send validates sockaddr/tag bits and capabilities, resolves a route or direct extended address, builds an skb with type byte payload prefix, stores network in `mctp_cb`, and calls `mctp_local_output()`. Recv pulls the type byte and returns base or extended sockaddr metadata. Tag ioctls allocate/drop manual `mctp_sk_key` entries; timers expire automatic keys. Unhash removes binds and all socket keys under net key lock.

Dependencies and integration: depends on route/device/neighbour subsystems, net namespace MCTP state, Linux socket/proto APIs, trace events, capabilities, and KUnit socket tests included when enabled.

Risks and test signals: tag lifetimes involve socket refs, key refs, timers, and device flow refs; cleanup must avoid use-after-free. `sendmsg()` mutates `addr->smctp_network` in the user-provided kernel sockaddr copy. Test signals include bind conflict matrix, connect/bind mismatch, direct extended addressing send/recv, ioctl error paths, key expiry, and module init unwind.
