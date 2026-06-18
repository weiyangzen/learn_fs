# sources/distributed-fs/ceph-client/drivers/infiniband/core/ud_header.c

## Purpose

`ud_header.c` builds and serializes Unreliable Datagram packet headers for InfiniBand/RDMA transports. It provides exported helpers for initializing `struct ib_ud_header`, computing IPv4 checksums, and packing the header into wire format. The code is a compact marshalling layer used by drivers or core RDMA paths that need UD packets with combinations of LRH, Ethernet, VLAN, GRH/IPv6, IPv4, UDP, BTH, DETH, and optional immediate data.

## Important APIs, Types, and Functions

- The `STRUCT_FIELD` macro describes how fields in unpacked header structs map into network-order bit fields consumed by `ib_pack`.
- Static `ib_field` tables define the bit layout for LRH, Ethernet, VLAN, IPv4, UDP, GRH, BTH, and DETH headers.
- `ib_ud_ip4_csum` constructs a Linux `iphdr` from the unpacked UD IPv4 fields and returns `ip_fast_csum`.
- `ib_ud_header_init` initializes a caller-provided `struct ib_ud_header` according to requested header presence flags, payload length, IP version, UDP presence, and immediate data flag.
- `ib_ud_header_pack` serializes the active pieces of `struct ib_ud_header` into a caller-provided buffer and returns the number of bytes written.

## Control Flow

Initialization starts by rejecting UDP without an IPv4 or IPv6 header, because a standalone UDP header is nonsensical. `grh_present` is suppressed when an IP header is requested; IPv6 uses the GRH layout in this ABI. The function zeroes the header and then fills length and protocol fields based on the requested header stack. If LRH is present it computes the packet length in 4-byte words including LRH, optional GRH, BTH, DETH, payload, ICRC, and rounding. For IPv6 or GRH it sets `ip_version`, `payload_length`, and `next_header`. For IPv4 it sets version, header length, total length, and UDP protocol. If UDP is present it fills the UDP length. BTH opcode is selected based on immediate data, and BTH pad count is derived from payload length.

Packing is linear and controlled by the boolean presence flags stored in `struct ib_ud_header`. It calls `ib_pack` for each active layout table in wire order, advances a byte count, always packs BTH and DETH, and optionally copies immediate data after DETH.

## State and Persistence

The file has no persistent or global mutable state. Static layout tables are read-only. All mutable state is in caller-provided `struct ib_ud_header` and output buffers. The exported helpers are pure with respect to kernel global state except for using common checksum and marshalling helpers.

## Dependencies and Integration Points

The file depends on `rdma/ib_pack.h` field packing machinery, Linux Ethernet/IP protocol constants, and RDMA header-size constants such as `IB_LRH_BYTES`, `IB_GRH_BYTES`, `IB_BTH_BYTES`, and `IB_DETH_BYTES`. It exports symbols for use by RDMA drivers and core code that construct UD packets, including RoCE-style Ethernet/IP/UDP encapsulated packets and classic IB LRH/GRH packets.

## Risks

The main risk is ABI or wire-format drift: a wrong offset, bit width, byte count, or length formula creates malformed packets that are hard to debug at the RDMA protocol level. Buffer sizing is the caller's responsibility in `ib_ud_header_pack`; the function returns the written length but does not validate output capacity. `ib_ud_header_init` accepts `payload_bytes` as an `int`; callers should avoid negative or overflow-prone values. IPv6/GRH sharing is intentional but subtle, so tests need to verify combinations of `grh_present`, `ip_version`, and `udp_present`.

## Test Signals

Tests should compare packed bytes against known-good LRH/GRH/BTH/DETH and RoCEv2 Ethernet/IP/UDP/IB UD headers, including immediate-data and padding cases. IPv4 checksum validation, VLAN type selection, packet length rounding, GRH payload length rounding, and rejection of UDP without IP are important signals. Cross-driver packet captures or hardware loopback tests can validate that generated headers are accepted by real devices.
