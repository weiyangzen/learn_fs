# sources/distributed-fs/ceph-client/include/net/tun_proto.h

## Purpose

`tun_proto.h` defines one-byte tunnel protocol identifiers shared by VXLAN-GPE and NSH-style encapsulations and converts them to and from Ethernet protocol values.

## Important APIs, types, and functions

Constants are `TUN_P_IPV4`, `TUN_P_IPV6`, `TUN_P_ETHERNET`, `TUN_P_NSH`, and `TUN_P_MPLS_UC`. Helpers are `tun_p_to_eth_p()` and `tun_p_from_eth_p()`.

## Control flow

Encapsulation code maps an inner protocol byte to an Ethernet protocol before passing packets into normal networking paths. Decapsulation or metadata construction maps an Ethernet protocol back to the compact tunnel value. Unknown protocols return zero.

## State and persistence behavior

The header owns no state. The mappings are static wire-protocol constants.

## Dependencies and integration points

It depends on Ethernet protocol definitions and kernel integer types. It integrates with VXLAN-GPE, NSH, MPLS tunnel metadata, and tunnel drivers that expose compact next-protocol fields.

## Risks and test signals

Risks include treating zero as a valid protocol, forgetting to update both mapping directions when adding a protocol, and mismatches with external tunnel registries. Tests should round-trip each supported protocol and verify unknown values fail closed.
