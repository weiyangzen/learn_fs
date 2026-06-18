# sources/distributed-fs/ceph-client/net/ipv6/xfrm6_protocol.c

## Purpose
Registers IPv6 protocol handlers for ESP, AH, and IPCOMP and provides chained handler registration for protocol-specific XFRM modules. It also supplies the IPv6 `xfrm_input_afinfo` callback used by generic XFRM receive.

## Important APIs, types, and functions
Exports `xfrm6_rcv_encap`, `xfrm6_protocol_register`, and `xfrm6_protocol_deregister`. Init/exit functions are `xfrm6_protocol_init` and `xfrm6_protocol_fini`. Static protocol descriptors are `esp6_protocol`, `ah6_protocol`, `ipcomp6_protocol`, and `xfrm6_input_afinfo`; handler lists are RCU pointers `esp6_handlers`, `ah6_handlers`, and `ipcomp6_handlers`.

## Control flow
Inbound ESP/AH/IPCOMP packets enter small protocol wrappers that pass the skb, protocol number, SPI, and encapsulation type into `xfrm6_rcv_encap`. That function walks the RCU handler chain for the protocol and calls each handler's callback until one consumes the packet. On failure it frees the skb and returns an error. Error handlers walk the same chain via `xfrm6_rcv_cb`, allowing modules to react to ICMPv6 errors.

Registration is serialized by `xfrm6_protocol_mutex`. A new handler is prepended only if the same callback is not already present, then the corresponding `inet6_protocol` is installed if needed. Deregistration unlinks the exact handler, unregisters the inet6 protocol when the list becomes empty, and waits for an RCU grace period.

## State and persistence behavior
Persistent runtime state is limited to the three RCU handler chains and installed inet6 protocol registrations. No disk state exists. Handler lifetime relies on module-level deregistration plus `synchronize_net`.

## Dependencies and integration points
Depends on IPv6 protocol registration, generic XFRM input AF registration, ESP/AH/IPCOMP modules registering `struct xfrm6_protocol`, RCU, and mutex serialization. It is initialized from `xfrm6_policy.c` and receives UDP-encapsulated ESP from `xfrm6_input.c`.

## Risks and test signals
Risks include duplicate handler registration, unregistering while readers are active, missing protocol deletion when the last handler leaves, and incorrect ICMP error propagation. Test module load/unload for ESP/AH/IPCOMP, inbound plain and UDP-encapsulated ESP, AH/IPCOMP receive, ICMPv6 errors to active SAs, concurrent traffic during deregistration, and error unwind from partial init.
