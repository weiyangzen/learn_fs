<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rpl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rpl.h

Purpose: defines the IPv6 RPL source-routing header layout exported to userspace and tunnel code.

Important APIs, types, and functions: `struct ipv6_rpl_sr_hdr` contains IPv6 extension-header fields, RPL compression fields `cmpri`/`cmpre`, padding/reserved bits with endian-specific bitfields, and a flexible union of IPv6 segment addresses or raw data. `rpl_segaddr` and `rpl_segdata` are compatibility aliases.

Control flow: packet creation or parsing code reads the fixed header, uses `hdrlen` and compression fields to determine segment encoding, and then consumes the flexible segment area as either full addresses or compressed bytes.

State and persistence behavior: state is packet wire data only. The packed struct does not own storage and must be used with validated skb or userspace buffers.

Dependencies and integration points: includes byteorder definitions, `linux/types.h`, and IPv6 address definitions. It integrates with IPv6 RPL source-routing, lightweight tunnel encapsulation, and packet parsers.

Risks and edge cases: bitfield order differs by endian and the struct is packed. Callers must validate `hdrlen`, `segments_left`, compression nibble values, and flexible-array bounds before dereferencing segment data.

Test signals: parse and emit RPL SRH packets on big- and little-endian builds, test compressed and uncompressed segment lists, fuzz `hdrlen` and compression fields, and verify tunnel encapsulation size calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rpl.h -->
