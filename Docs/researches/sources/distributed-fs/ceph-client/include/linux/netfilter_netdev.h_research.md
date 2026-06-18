# sources/distributed-fs/ceph-client/include/linux/netfilter_netdev.h

Purpose: Defines ingress and egress netdev netfilter hook helpers that bridge net_device packet paths to `nf_hook()`.

Important APIs, types, and functions: Exports `nf_hook_ingress_active()`, `nf_hook_ingress()`, `nf_hook_egress_active()`, `nf_hook_egress()`, `nf_skip_egress()`, and `nf_hook_netdev_init()` with configuration-dependent stubs. Detected source surface: 151 lines; includes `linux/netdevice.h`, `linux/netfilter.h`; macros `_NETFILTER_NETDEV_H_`; structs `net_device`, `nf_hook_entries`, `nf_hook_state`; enums none; typedefs none; function-like declarations/helpers `nf_hook_egress_active`, `nf_hook_ingress`, `nf_hook_ingress_active`, `nf_hook_netdev_init`, `nf_skip_egress`, `rcu_access_pointer`.

Control flow: The network device receive/transmit paths check static keys and per-device hook lists, initialize hook state with netdev family and hook number, and pass skbs through ingress or egress hooks. Egress code may consume/drop/return a replacement skb and supports skip marking to avoid recursion.

State and persistence behavior: State lives in static keys, per-device hook lists, skb extension flags, and net namespace hook arrays. The header defines inline control decisions but not backing storage.

Dependencies and integration points: Depends on netfilter core and netdevice structures. Used by tc/nftables netdev family integration and driver-facing packet paths.

Risks and test signals: Risks are recursion on egress reinjection, wrong return convention for consumed skbs, and static-key/config stub mismatches. Test ingress drop/accept, egress redirect/drop, disabled CONFIG_NETFILTER_INGRESS/EGRESS, and device unregister.
