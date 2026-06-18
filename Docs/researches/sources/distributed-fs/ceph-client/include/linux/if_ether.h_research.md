# `sources/distributed-fs/ceph-client/include/linux/if_ether.h`

Purpose: kernel Ethernet header access helpers and MAC formatting declarations layered over UAPI Ethernet constants.

Important APIs/types/functions: `MAC_ADDR_STR_LEN`, `eth_hdr`, `skb_eth_hdr`, `inner_eth_hdr`, `eth_header_parse`, and `sysfs_format_mac`.

Control flow and state: inline pointer casts over the caller-managed `sk_buff` header pointers; no persistent state.

Dependencies/integration: depends on `sk_buff`, UAPI `if_ether.h`, and netdevice parsing/formatting users throughout Ethernet, VLAN, tunneling, sysfs, and drivers.

Risks: helpers assume header pointers have been set and data is pulled enough; `skb_eth_hdr` is TX-path oriented and uses `skb->data`; MAC string length excludes trailing NUL.

Test signals: short skb header tests, TX path callers using `skb_eth_hdr`, inner MAC header tunnel parsing, sysfs MAC formatting buffer sizing, and compile checks for Ethernet UAPI constants.
