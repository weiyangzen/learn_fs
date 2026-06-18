# sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvlan_l3s.c

Purpose: Adds IPvlan L3S support, which makes an IPvlan port act as an L3 master device and rewrites local-input packets to the matched IPvlan slave late in netfilter input processing. This mode lets routed traffic arrive on the lower device but be accounted and delivered as the correct IPvlan device.

Important APIs and functions: Public lifecycle hooks are `ipvlan_l3s_init()`, `ipvlan_l3s_cleanup()`, `ipvlan_l3s_register()`, `ipvlan_l3s_unregister()`, and `ipvlan_migrate_l3s_hook()`. Internal helpers are `ipvlan_skb_to_addr()`, `ipvlan_l3_rcv()`, `ipvlan_nf_input()`, `ipvlan_register_nf_hook()`, `ipvlan_unregister_nf_hook()`, and `ipvlan_ns_exit()`. `ipvl_l3mdev_ops` supplies `.l3mdev_l3_rcv`.

Control flow: `ipvlan_l3s_register()` increments a per-netns netfilter hook reference count, installs `l3mdev_ops` on the lower device, and marks `IFF_L3MDEV_RX_HANDLER`. The l3mdev receive callback performs IPv4 or IPv6 input route lookup using the matched IPvlan device. The netfilter hooks run at `NF_INET_LOCAL_IN` with `INT_MAX` priority; when an skb maps to a configured IPvlan address, `ipvlan_nf_input()` changes `skb->dev`, `skb_iif`, and IPv6 control-block input interface, then records successful RX accounting.

State and persistence: State is per network namespace in `struct ipvlan_netns`, storing only `ipvl_nf_hook_refcnt`. The hook is registered once per namespace no matter how many L3S ports exist, and unregistered when the refcount reaches zero. `ipvlan_ns_exit()` defensively warns and unregisters if namespace teardown finds leaked references.

Dependencies and integration: Depends on `ipvlan_core.c` address parsing/lookup and RX accounting, l3mdev operations, IPv4/IPv6 route input helpers, netfilter hook registration, and pernet subsystem registration. `ipvlan_main.c` calls this when mode changes to or from `IPVLAN_MODE_L3S` and when the lower device moves network namespaces.

Risks and test signals: Risks include hook refcount imbalance across mode changes and namespace moves, stale `l3mdev_ops`, incorrect skb input-interface rewrites, and IPv6 conditional build behavior. Test L3S registration/unregistration cycles, multiple ports in one netns, netns migration, local IPv4/IPv6 delivery, IPv6 disabled builds, and namespace exit with active devices.
