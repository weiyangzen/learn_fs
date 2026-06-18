# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_protocol_type.h

## Purpose
`ice_protocol_type.h` defines ICE protocol identifiers, tunnel types, hardware protocol IDs, packet header layouts, metadata IDs/offsets, packet flag masks, and extraction structures used by switch/flow recipe logic. It is a shared vocabulary for matching packet fields and metadata in the ICE pipeline.

## Important APIs, Types, and Functions
- Recipe limits: `ICE_NUM_WORDS_RECIPE`, `ICE_MAX_CHAIN_RECIPE`, `ICE_MAX_CHAIN_RECIPE_RES`, `ICE_MAX_CHAIN_WORDS`, and `ICE_CHAIN_FV_INDEX_START`.
- Protocol enums: `enum ice_protocol_type`, `enum ice_sw_tunnel_type`, and `enum ice_prot_id`.
- Hardware protocol constants such as `ICE_MAC_OFOS_HW`, `ICE_IPV4_OFOS_HW`, `ICE_UDP_OF_HW`, and related tunnel/header IDs.
- Header structures: Ethernet, ethertype, VLAN, IPv4, IPv6, SCTP, L4, UDP tunnel, GTP, PFCP, PPPoE, L2TPv3, NVGRE, and `struct ice_hw_metadata`.
- Metadata definitions: MDID IDs, offsets, packet flag masks, and `enum ice_pkt_flags`.
- Extraction structures: `union ice_prot_hdr`, `struct ice_prot_ext_tbl_entry`, and `struct ice_prot_lkup_ext`.

## Control Flow
This is a declarative header with no functions. Flow/recipe code uses these constants and structures to map software protocol types to hardware protocol IDs, compute field offsets, interpret metadata words, and build lookup extraction lists. The comments document MDID bit layouts that downstream code uses when matching VLAN, tunnel, TCP, and error flags.

## State and Persistence
No mutable state is defined. The structures describe packet and metadata layouts, and caller-owned instances may be used to build persistent hardware recipes elsewhere.

## Dependencies and Integration Points
The file depends on Ethernet constants, bit macros, endian types, and `struct ice_fv_word` from surrounding ICE/common headers. It integrates with switch recipe construction, flow director, ACL/RSS matching, parser profile generation, and any logic that maps parsed protocol offsets into field vectors.

## Risks
Layout definitions must match hardware parser and firmware expectations. Several structures intentionally model wire format with big-endian fields; consumers must avoid host-endian comparisons. Metadata comments encode bit meanings that can vary by package/version, and the file notes that not all MDIDs are available to the switch block. Recipe chain limits and field-vector indexes are hard bounds; overflow or misuse can lead to invalid hardware recipes.

## Test Signals
Compile-time checks for structure sizes/offsets and enum/constant consistency are valuable. Runtime flow tests should cover recipes for outer/inner MAC/IP/L4, VLAN flags, tunnel flags, metadata source VSI/PTYPE/length, and chained recipes near `ICE_MAX_CHAIN_WORDS`. Packet classification tests should verify big-endian header fields and protocol offsets are interpreted correctly.
