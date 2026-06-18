# sources/distributed-fs/ceph-client/Documentation/netlink/specs/wireguard.yaml

Purpose: this generic-netlink legacy schema documents the WireGuard device control ABI for retrieving and setting interface, peer, and allowed-IP configuration.

Important APIs, types, and functions: constants include `wg-key-len` of 32 bytes. Struct `--kernel-timespec` models handshake time. Flags include device `replace-peers`, peer `remove-me`, `replace-allowedips`, `update-only`, and allowed-IP `remove-me`. Attribute sets are hierarchical: `wgdevice` has ifindex/ifname, private/public keys, flags, listen port, fwmark, and indexed-array `peers`; `wgpeer` has public/preshared keys, flags, endpoint, keepalive interval, last handshake, byte counters, indexed-array allowed IPs, and protocol version; `wgallowedip` has family, IP address, CIDR mask, and flags.

Control flow: `get-device` value 0 is a dump operation requiring exactly one of ifindex or ifname. It may emit multiple `NLM_F_MULTI` messages; peers or allowed IP lists can be fragmented and must be coalesced by userspace. The final `NLMSG_DONE` carries a zero or negative errno. `set-device` value 1 accepts the device tree and may be sent in fragments when configuration exceeds max message size; replace flags should only appear in the first relevant fragment.

State and persistence: WireGuard device keys, listen port, fwmark, peer list, endpoints, counters, keepalive timers, and allowed IPs live in kernel WireGuard device state. Private/preshared keys can be cleared with all-zero payloads.

Dependencies and integration: depends on the WireGuard generic netlink family name/version, kernel netdevice instances, AF_INET/AF_INET6 endpoint and allowed-IP formats, and userspace tools such as `wg`.

Risks: key material is sensitive binary payload. Fragmented dump/set semantics require correct coalescing and careful use of replace flags. Interface selector exclusivity is semantic rather than represented as a YAML check. Test signals include get/set round trips, invalid key length rejection, peer/allowed-IP fragmentation tests, selector exclusivity tests, and counter/handshake decoding.
