# sources/distributed-fs/ceph-client/include/uapi/linux/batadv_packet.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/batadv_packet.h` is the public wire-format contract for the B.A.T.M.A.N. advanced mesh protocol. The complete 669-line header was read. It defines packet type numbers, protocol flags, ICMP/throughput-meter values, TVLV container types, and the packed packet structures consumed by kernel batman-adv code and userspace tools such as `batctl`.

## Important APIs, Types, and Functions

There are no functions, but the macro `batadv_tp_is_error(n)` classifies throughput-meter status values over 127 as errors. Important enums include `batadv_packettype`, `batadv_subtype`, `batadv_iv_flags`, `batadv_icmp_packettype`, `batadv_mcast_flags`, `batadv_tt_data_flags`, `batadv_vlan_flags`, `batadv_bla_claimframe`, `batadv_tvlv_type`, and `batadv_icmp_tp_subtype`. Important structs include `batadv_bla_claim_dst`, OGM/OGM2/ELP headers, ICMP variants, unicast, unicast-4addr, fragment, broadcast, multicast, coded, unicast TVLV, `batadv_tvlv_hdr`, gateway, translation-table VLAN/data/change, roam advertisement, multicast data, and multicast tracker payloads.

## Control Flow

The file itself has no executable flow. Protocol flow is encoded in header layout and type fields: receivers classify packets by `packet_type`, then route to OGM, ELP, unicast, multicast, ICMP, network-coding, or TVLV parsers. TVLV-bearing packets use `tvlv_len` followed by one or more `batadv_tvlv_hdr` containers. Fragment flow depends on the endian-specific bitfield in `batadv_frag_packet`; ICMP route-record flow uses a bounded `BATADV_RR_LEN` array; throughput-meter flow sends `BATADV_TP_MSG` and expects `BATADV_TP_ACK`.

## State and Persistence Behavior

No persistent state is owned by the header. It describes transient mesh control and payload packets whose fields drive kernel tables for originators, neighbors, translation tables, multicast capabilities, bridge loop avoidance, distributed ARP table, roaming, and throughput-meter sessions. Packet sequence numbers, TTLs, TTVNs, checksums, and write-once timestamps are state carriers across the mesh, not local storage.

## Dependencies and Integration Points

Direct dependencies are `<asm/byteorder.h>`, `<linux/if_ether.h>`, `<linux/stddef.h>`, and `<linux/types.h>`. Integration points include the batman-adv kernel module, Ethernet frame handling, `batctl`, generic netlink status reporting in `batman_adv.h`, and mesh peers that must agree on `BATADV_COMPAT_VERSION`, packet type numbers, byte order, and structure packing.

## Risks and Edge Cases

This is a wire ABI. The `#pragma pack(2)` requirement is central because headers before Ethernet payloads must satisfy alignment constraints; accidental padding can break interoperability or leak uninitialized bytes. The fragment packet bitfield depends on `__BIG_ENDIAN_BITFIELD` or `__LITTLE_ENDIAN_BITFIELD`; unsupported byteorder intentionally fails compilation. Flexible arrays and counted TVLV data require length validation before parsing. Multicast, TT, and network-coding fields mix host-local and network-byte-order values, so tools must respect the declared `__be16`/`__be32` types.

## Test Signals

Strong signals include compile coverage on big- and little-endian targets, structure size/offset assertions for packet headers, packet parser fuzzing with malformed `tvlv_len` and fragment fields, interop tests between kernel batman-adv and `batctl`, mesh integration tests for OGM/ELP/unicast/multicast paths, and throughput-meter tests that validate success/error classification around value 127/128.
