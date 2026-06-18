# sources/distributed-fs/ceph-client/include/net/flow.h

Purpose: defines the generic routing-flow descriptors used by IPv4 and IPv6 output lookups. `struct flowi_common` carries shared selector state: output/input ifindex, L3 master device, mark, DSCP, scope, protocol, flags, security id, UID, multipath hash, and tunnel id. `struct flowi4` and `struct flowi6` add address-family fields and the `union flowi_uli` L4 selector union for ports, ICMP, mobility header, and GRE key. `struct flowi` overlays common, IPv4, and IPv6 views for APIs that route either family.

Important APIs: `flowi4_init_output()` fully initializes an IPv4 lookup key, including loopback input index, DSCP conversion from TOS, UID, ports, and zeroed tunnel/multipath fields. `flowi4_update_output()` retargets address/output-interface fields after a previous lookup. `flowi4_to_flowi()`, `flowi6_to_flowi()`, and common accessors rely on the union layout. `__get_hash_from_flowi6()` exports IPv6 hash derivation into flow keys.

Control flow and state: this header is mostly value construction. Callers allocate these descriptors on stack or in cork/socket state, initialize them, then pass them into route, xmit, and reply paths. There is no persistent storage here; persistence comes from copied socket fields such as marks, UIDs, ports, and tunnel identifiers.

Dependencies and integration: depends on `inet_dscp.h`, `in6.h`, atomic/container helpers, and Linux UID types. It integrates with `ip.h`, `inet_sock.h`, IPv6 routing, tunnel output, policy routing, and flow hashing.

Risks: partial initialization is dangerous because route lookups consume many flags and selectors. The IPv4 address grouping and alignment comments are ABI-like assumptions used by fast copy/hash paths. Tests should cover route lookup behavior with marks, DSCP/TOS, bound devices, transparent/HDRINCL flags, tunnel ids, and IPv6 flow hashing.
