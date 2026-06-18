<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/xdp_diag.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/xdp_diag.h

Purpose: defines the sock_diag interface for querying AF_XDP/XDP socket information, rings, UMEM, memory info, and statistics.

Important APIs and types: `struct xdp_diag_req` and `xdp_diag_msg` carry family/protocol, inode, show mask, and cookies. Show flags request basic info, ring config, UMEM, meminfo, and stats. Attribute enum names diagnostic attributes. `struct xdp_diag_info`, `xdp_diag_ring`, `xdp_diag_umem`, and `xdp_diag_stats` report ifindex/queue, ring entries, UMEM geometry/flags/refs, and drop/invalid/empty counters.

Control flow, state, and persistence: userspace sends sock_diag requests and receives snapshots of XDP socket state. No persistent state is defined here.

Dependencies and integration points: integrates AF_XDP sockets, sock_diag netlink, XDP zero-copy UMEM, and observability tools.

Risks and test signals: risks include stale cookie matching, UMEM refcount visibility, stats races, and optional attribute gating. Test sockets with RX/TX rings, shared UMEM, zero-copy flag, invalid descriptors, and show-mask combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/xdp_diag.h -->
