# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_netiface.c

## Purpose

`ip_set_hash_netiface.c` implements `hash:net,iface`, an ipset type matching an IP network plus network interface name. It supports physical bridge device matching, wildcard interface prefixes, `nomatch`, `/0` support, and generic ipset extensions.

## Important APIs, types, and functions

The hashed key structs omit the variable interface string from the key length used by the generated hash, while full element structs store `ip`, `physdev`, `cidr`, `nomatch`, `elem`, `wildcard`, and `iface[IFNAMSIZ]`. `hash_netiface{4,6}_data_equal()` first compares IP/CIDR, increments the `multi` counter for same-network multi-element checks, then compares physical-device bit and either exact interface name or wildcard prefix. `data_list()` emits IP, CIDR, interface name, and flags for physdev, wildcard, and nomatch. `get_physindev_name()` and `get_physoutdev_name()` integrate with bridge netfilter when configured. `kadt` functions read packet IP and either logical in/out interface or bridge physical interface. `uadt` functions parse IP, interface name, flags, CIDR, ranges, and extensions.

## Control flow

The file configures `IP_SET_HASH_WITH_NETS`, `IP_SET_HASH_WITH_MULTI`, and `IP_SET_HASH_WITH_NET0`; the last allows `/0` entries. Packet operations mask the packet IP by default CIDR and copy the selected interface name. Userspace IPv4 can add/delete/test exact entries or expand `IP_TO` into CIDR blocks. IPv6 rejects IP ranges. `IPSET_FLAG_PHYSDEV` switches packet-path interface selection to bridge physical devices if `CONFIG_BRIDGE_NETFILTER` is enabled; otherwise physdev requests cannot populate an interface and fail. `IPSET_FLAG_IFACE_WILDCARD` changes equality to prefix matching.

## State and persistence behavior

The set stores interface names in each element plus generic extensions and timeout state. The `multi` mechanism lets multiple interface entries share the same network hash key. Timed entries are handled by generic hash cleanup. Retry state for IPv4 stores the next IP block. The registered type carries no independent global state.

## Dependencies and integration points

Dependencies include bridge netfilter APIs, ipset net/hash infrastructure, IFNAMSIZ string handling, netlink parsers, and packet path `xt_action_param` interface state. The type exposes `IPSET_TYPE_IP | IPSET_TYPE_IFACE | IPSET_TYPE_NOMATCH`.

## Risks

Interface wildcard matching uses prefix comparison with the stored name length, so malformed or unintended prefixes can match broad device sets. Physdev behavior depends on `CONFIG_BRIDGE_NETFILTER`; without it, physdev packet matching can fail. Empty interface names are rejected on packet path. `/0` support is deliberate here and must be tested because many other hash net types reject CIDR zero.

## Test signals

Tests should cover exact interface matches, wildcard prefix matches, logical input/output dimension flags, bridge physdev matching when enabled, `/0` entries, IPv4 range expansion, IPv6 range rejection, `nomatch`, timeout cleanup, and list serialization of physdev/wildcard flags.
