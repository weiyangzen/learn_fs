# sources/distributed-fs/ceph-client/include/linux/netfilter_bridge.h

Purpose: Defines bridge netfilter helpers for sk_buff bridge metadata, fake route cleanup, physical in/out device queries, and prerouting state checks.

Important APIs, types, and functions: Key exports are `struct nf_bridge_frag_data`, `br_handle_frame_finish()`, `br_drop_fake_rtable()`, `nf_bridge_info_get()`, `nf_bridge_info_exists()`, physical interface accessors, and `nf_bridge_in_prerouting()`. Detected source surface: 88 lines; includes `linux/skbuff.h`, `uapi/linux/netfilter_bridge.h`; macros `__LINUX_BRIDGE_NETFILTER_H`, `br_drop_fake_rtable`; structs `dst_entry`, `nf_bridge_frag_data`; enums none; typedefs none; function-like declarations/helpers `br_drop_fake_rtable`, `br_handle_frame_finish`, `nf_bridge_get_physindev`, `nf_bridge_get_physinif`, `nf_bridge_get_physoutdev`, `nf_bridge_get_physoutif`, `nf_bridge_in_prerouting`, `nf_bridge_info_exists`, `nf_bridge_info_get`, `skb_ext_exist`, `skb_ext_find`.

Control flow: Bridge netfilter attaches metadata to bridged skbs, carries fragmentation state when IPv4/IPv6 bridge hooks fragment packets, and later resumes bridge frame handling or drops fake route entries.

State and persistence behavior: State is per-skb bridge info plus optional frag data; no persistent global state is owned by the header.

Dependencies and integration points: Depends on bridge netfilter UAPI and sk_buff. Integrated by bridge, IPv4/IPv6 netfilter, ebtables, and nf_bridge forwarding paths.

Risks and test signals: Risks are stale physical device pointers, fake dst leaks, and wrong prerouting detection after skb clones. Test bridged IPv4/IPv6 traffic through netfilter hooks, fragmentation, and bridge device teardown.
