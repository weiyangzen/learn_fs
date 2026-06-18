# sources/distributed-fs/ceph-client/include/net/firewire.h

Read `sources/distributed-fs/ceph-client/include/net/firewire.h` completely for this pass (27 lines, 599 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/firewire.h_research.md`.

Purpose: defines pseudo link-layer address and header formats for IP over IEEE 1394 FireWire networking.

Important APIs/types/functions: `FWNET_ALEN` is 16 bytes. `union fwnet_hwaddr` exposes raw bytes and an RFC2734/RFC3146 hardware-address layout containing EUI-64 `uniq_id`, max receive size `max_rec`, speed `sspd`, and six-byte FIFO address. `FWNET_HLEN` is 18 bytes. `struct fwnet_header` contains a 16-byte destination pseudo address and 16-bit protocol field.

Control flow: FireWire network code uses the pseudo hardware address for neighbor/ARP-like addressing and emits/parses `fwnet_header` before the network-layer payload.

State and persistence: no state is stored. The address values are per-node/interface runtime identifiers derived from FireWire bus properties.

Dependencies and integration points: depends only on Linux integer types. It integrates with the FireWire net driver, RFC2734 IPv4-over-1394, RFC3146 IPv6-over-1394, and generic netdevice header/address handling.

Risks: packed layout and big-endian fields are wire ABI. The pseudo address is not an Ethernet MAC and must not be treated as 6 bytes. FIFO/speed/max_rec values must match FireWire node capabilities.

Test signals: FireWire net header encode/decode, address length reporting, IPv4/IPv6 over 1394 interop, endian checks for EUI-64/protocol field, MTU/max_rec handling, and neighbor resolution with 16-byte addresses.
