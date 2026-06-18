# sources/distributed-fs/ceph-client/drivers/net/ovpn/bind.h

Purpose: defines ovpn binding data structures and inline packet-source matching for peer remote endpoints.

Important APIs/types/functions: `union ovpn_sockaddr` wraps IPv4/IPv6 sockaddr forms. `struct ovpn_bind` stores remote sockaddr, local IPv4/IPv6 endpoint, and RCU cleanup head. `ovpn_bind_skb_src_match()` compares an skb's source IP and UDP source port against the binding remote address. It also declares bind allocation/reset functions.

Control flow: the inline matcher rejects null bindings, branches on `skb->protocol`, verifies the stored family, compares IPv4 or IPv6 source address, then compares UDP source port. Non-IP protocols fail.

State and persistence: the header defines per-peer volatile binding state. RCU cleanup is part of the structure contract.

Dependencies and integration: uses IP, IPv6, UDP, skb, spinlock, and RCU headers. It is used by peer receive and endpoint lookup logic to validate packet source addresses.

Risks: matcher assumes UDP header access is valid for the skb shape provided by callers. It matches only remote endpoint, not local endpoint. Any protocol other than IPv4/IPv6 UDP fails.

Test signals: feed IPv4/IPv6 UDP skbs with matching and mismatching source address/port, null bind, wrong family, and non-IP protocol cases.
