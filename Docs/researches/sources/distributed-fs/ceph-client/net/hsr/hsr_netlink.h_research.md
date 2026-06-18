## sources/distributed-fs/ceph-client/net/hsr/hsr_netlink.h

Purpose: public-in-driver declarations for the HSR/PRP netlink integration. It keeps module init/exit and asynchronous node notification APIs visible to the rest of the HSR code without exposing netlink implementation details.

Important APIs/types/functions: declares `hsr_netlink_init()` and `hsr_netlink_exit()` for module registration/unregistration of rtnl and generic-netlink families. Declares `hsr_nl_ringerror(struct hsr_priv *hsr, unsigned char addr[ETH_ALEN], struct hsr_port *port)` for notifying userspace when traffic for a node is seen only through one slave, and `hsr_nl_nodedown(struct hsr_priv *hsr, unsigned char addr[ETH_ALEN])` for notifying when a node ages out. Forward declarations of `struct hsr_priv` and `struct hsr_port` avoid heavy include coupling.

Control flow and state: this header carries no state and has no runtime control flow. Its functions operate on live `hsr_priv`/`hsr_port` objects owned by the HSR master and node database. Callers are expected to respect the locking context of the notification emitters; the implementation allocates atomic skbs and performs RCU lookup of the master for warning paths.

Dependencies and integration points: includes `linux/if_ether.h` for `ETH_ALEN`, `linux/module.h`, and UAPI `linux/hsr_netlink.h` for command/attribute constants. It is included by `hsr_netlink.c` and by HSR code that emits topology notifications.

Risks: the notification APIs take raw MAC buffers and object pointers, so stale object lifetime or wrong locking in callers can produce invalid reports. No compile-time constraint says the passed `port` belongs to `hsr`, so callers must maintain that invariant.

Test signals: build coverage checks prototypes and UAPI availability. Runtime signals are userspace reception of ring error and node-down multicast events during HSR topology failure/aging tests.
