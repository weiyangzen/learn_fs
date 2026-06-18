# sources/distributed-fs/ceph-client/include/net/xfrm.h

## Purpose

`xfrm.h` is the central internal header for Linux XFRM/IPsec. It defines security association state, policy database entries, mode/type registration, key-manager callbacks, replay protection, secpath metadata, route bundles, tunnel/interface hooks, hardware offload contracts, netlink/PF_KEY compatibility, NAT keepalive hooks, and policy/state lookup APIs.

## Important APIs, types, and functions

Core state types include `struct xfrm_state`, `struct xfrm_policy`, `struct xfrm_tmpl`, `struct xfrm_dst`, `struct sec_path`, `struct xfrm_offload`, `struct xfrm_dev_offload`, `struct xfrm_mgr`, `struct xfrm_type`, `struct xfrm_type_offload`, `struct xfrm_mode_cbs`, `struct xfrm_policy_afinfo`, `struct xfrm_state_afinfo`, protocol/tunnel handler structures, algorithm descriptors, `struct xfrm_translator`, and XFRM interface structs. Important helpers cover reference management (`xfrm_state_hold()`/`put()`, `xfrm_pol_hold()`/`put()`), address/selector matching, flow port extraction, policy checks, route forwarding checks, socket policy clone/free, state/policy lookup/add/update/delete/flush, replay check/advance, mode/type registration, offload validation, mark and if_id netlink attributes, and NAT keepalive lifecycle.

## Control flow

Outbound packets decode a flow, check socket and global policies, resolve templates to states, build an `xfrm_dst` bundle, and pass through mode/type output callbacks or offload validation. Inbound packets parse SPI/sequence, find a state, perform replay/auth/decrypt/type input, populate secpath, and then run policy verification. Missing states trigger key-manager acquire/report callbacks. State and policy netlink/PF_KEY changes allocate, initialize, insert, update, delete, or flush objects and send notifications. Device offload paths add state/policy to netdevices, validate transmit offload, resume async processing, and free offload resources on teardown.

## State and persistence behavior

Persistent state is per-net namespace XFRM SPD/SAD state plus per-object timers, lifetimes, replay windows, generation IDs, refcounts, locks, security contexts, algorithm/key material, encapsulation data, NAT keepalive state, and offload device references. `struct sec_path` is per-SKB metadata recording applied transforms and offload status. `xfrm_dst` route bundles cache route, path, child, policy and state references plus generation/cookie values. Timers drive replay notifications, hard/soft expiry, hold queues, and NAT keepalives.

## Dependencies and integration points

It depends on UAPI XFRM, PF_KEY, IPsec, IPv4/IPv6 routing, flow keys, dst entries, GRO cells, audit, netlink attributes, socket policy, SNMP statistics, netdevice offload ops, optional security labels, optional migration, optional user compat translation, and optional BTF/BPF registration. It integrates with ESP/AH/IPComp, IPIP/IPv6 tunnel modes, XFRM interfaces, UDP encapsulation, key managers, iproute2/netlink policy management, audit, hardware crypto/packet offload, and network namespaces.

## Risks and test signals

Risks are high because this header defines security-critical lifetime and policy contracts. Key issues include refcount/RCU mistakes in state/policy/dst/secpath objects, replay-window or ESN errors, selector/address matching bugs, policy bypass through `DST_NOPOLICY`/`IPSKB_NOPOLICY`, offload device reference leaks, netlink attribute length mistakes, algorithm clone allocation leaks, mode callback misuse, and disabled-config stubs accepting traffic when XFRM is absent. Tests should cover inbound/outbound IPsec for IPv4/IPv6, transport and tunnel modes, policy block/allow/acquire, socket policies, replay and ESN windows, lifetime expiry, NAT-T and keepalive, state/policy migration, hardware offload add/delete/resume, audit events, netlink/PF_KEY compatibility, XFRM interfaces, and config matrices with XFRM/offload/security/IPv6 disabled.
