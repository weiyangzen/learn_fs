# sources/distributed-fs/ceph-client/include/net/nsh.h

Purpose: defines Network Service Header structures, masks, constants, and skb helpers used to push/pop and parse service function chaining metadata.

Important APIs and types: `struct nshhdr` represents the base/service-path header plus MD type 1 fixed context or MD type 2 TLV metadata. `struct nsh_md1_ctx` and `struct nsh_md2_tlv` model metadata formats. Masks/shifts decode version, flags, TTL, length, MD type, SPI, and SI. Helpers return the skb NSH header, header length, version, flags, TTL, and update flags/TTL/length fields. `nsh_push()` and `nsh_pop()` manipulate encapsulation.

Control flow: datapath code positions the network header on NSH, validates length/type, decrements or sets TTL/SI elsewhere, and uses push/pop around encapsulation and decapsulation.

State and persistence: no persistent state; all data is per-packet header state in skb linear data.

Dependencies and integration points: depends on skbuff accessors and byte-order helpers; integrates with tunnel/classifier actions and service function chaining encapsulation.

Risks and test signals: risks include malformed length causing out-of-bounds access, MD type 2 TLV padding mistakes, incorrect endian masking, TTL loop-detection errors, and skb headroom/tailroom failures. Test push/pop round trips, MD1 and MD2 lengths, max header length, OAM/unknown protocol handling, TTL edge cases, and malformed packets.
