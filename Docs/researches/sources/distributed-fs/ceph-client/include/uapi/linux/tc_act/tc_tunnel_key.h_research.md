# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_tunnel_key.h

## Purpose
Defines the TC tunnel key action ABI for setting or releasing tunnel metadata used by encapsulation offloads and tunnel devices.

## Important APIs, Types, and Constants
Actions are `TCA_TUNNEL_KEY_ACT_SET` and `TCA_TUNNEL_KEY_ACT_RELEASE`. `struct tc_tunnel_key` embeds `tc_gen` and `t_action`. Attributes carry IPv4/IPv6 source and destination, key id, destination port, checksum/no-frag flags, TOS, TTL, and nested tunnel options. Nested option families cover Geneve, VXLAN GBP, and ERSPAN fields.

## Control Flow, State, and Persistence
Userspace configures tunnel metadata. Runtime action writes or clears tunnel key state on the skb for later encapsulation or offload. Action state persists in TC.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>`. Integrates with TC, tunnel devices, switchdev/hardware offload, Geneve, VXLAN, and ERSPAN.

## Risks and Test Signals
Risks include invalid nested option lengths, IPv4/IPv6 attribute mismatch, key-id endian issues, and offload feature gaps. Test set/release, each tunnel family, option parsing boundaries, packet encapsulation, and dump/offload behavior.
