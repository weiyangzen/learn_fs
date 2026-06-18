# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/npc.h

## Purpose

`npc.h` defines the parser, key extraction, action, profile, and MCAM rule data structures for the OcteonTX2 NPC block. NPC is the packet parser and match/action engine used by RVU/NIX flows; this header provides layer/ltype enumerations, key-field identifiers, packed firmware/profile formats, action bitfield layouts, vtag action masks, reserved MCAM entry indexes, and the in-memory rule representation used by AF flow steering.

## Important APIs, Types, And Constants

`SET_KEX_LD()` and `SET_KEX_LDFLAGS()` are helper macros for programming NPC key extraction registers. `enum NPC_LID_E` defines parser layers LA through LH. The `npc_kpu_*_ltype` enums define recognized ltypes at each layer: Ethernet/custom/CPT at LA, VLAN/DSA/PPPoE at LB, IPv4/IPv6/ARP/MPLS at LC, TCP/UDP/SCTP/ICMP/AH/GRE at LD, tunnel protocols at LE/LF/LG/LH, and inner transport ltypes.

`enum key_fields` defines logical fields used in MCAM keys: DMAC, SMAC, ethertype, VLAN tags, IPv4/IPv6 addresses, protocol selectors, ports, IPsec SPI, MPLS fields, ICMP fields, TCP flags, channel, PF_FUNC, error fields, layer ltypes, exact match result, extracted tag views, and unknown fields.

Packed profile structures include `npc_kpu_profile_cam`, `npc_kpu_profile_action`, `npc_kpu_profile`, `npc_kpu_fwdata`, `npc_kpu_profile_fwdata`, `npc_coalesced_kpu_prfl`, and `npc_mcam_kex`. These encode firmware-loadable KPU CAM/action entries, default MKEX data, layer-type definitions, and custom profile metadata.

Hardware register bitfield structs include `npc_kpu_cam`, `npc_kpu_action0`, `npc_kpu_action1`, `npc_kpu_pkind_cpi_def`, `nix_rx_action`, and `nix_tx_action`. `rvu_npc_mcam_rule` is the software rule object with packet/mask keys, interface, RX/TX action union, vtag action, owner, entry, counter, channel, priority, and flags.

## Control Flow

The header does not implement functions, but it drives NPC initialization and flow programming elsewhere in the AF driver. KPU profile loaders consume the packed profile structures, write CAM/action registers using the bitfield layouts, install key extraction profiles through `npc_mcam_kex`, and derive field offsets from `key_fields` and ltype defaults.

Flow installation code builds `rvu_npc_mcam_rule`, fills packet and mask data, chooses RX or TX action layout, optionally attaches counters and vtag actions, and writes MCAM entries. Default unicast, broadcast, all-multicast, and promiscuous entries use the reserved NIXLF entry indexes declared here.

## State And Persistence Behavior

Profile structures describe persistent NPC hardware programming loaded into KPU and key extraction registers. `rvu_npc_mcam_rule` instances are software state for installed flows; the corresponding MCAM entries, counters, and actions persist in hardware until removed, disabled, or reset. The firmware profile data is packed and endian-sensitive, with signatures such as `NPC_SIGN` and `KPU_SIGN` guarding profile identity.

## Dependencies And Integration Points

`npc.h` depends on constants and types from surrounding RVU/NPC headers, including `NPC_MAX_INTF`, `NPC_MAX_LID`, `NPC_MAX_LT`, `NPC_MAX_LD`, `NPC_MAX_LFL`, `MKEX_NAME_LEN`, `struct flow_msg`, and NIX interface/action definitions. It is included by `rvu.h` and used by NPC initialization, profile loading, MCAM resource management, flow steering, exact match support, VLAN tag actions, and NIX RX/TX delivery setup.

MCS files in this work item do not include `npc.h` directly, but both MCS and NPC live under the RVU Admin Function and participate in hardware packet processing: NPC classifies and steers packets, while MCS applies MACsec policies at the MACsec block.

## Risks

Several enum comments warn that ltype values must not be modified because RSS flow-tag calculation, IPv4/IPv6 checksum/length handling, and protocol detection depend on stable encodings. Packed firmware structures are ABI-sensitive; changing field order, packing, or endian annotations can break external KPU/MKEX profiles. The bitfield structs are endian-conditional and must match hardware register definitions exactly.

`rvu_npc_mcam_rule` mixes hardware entry ownership, action data, counters, vtag state, and list linkage. Incorrect lifetime or owner handling can leak MCAM entries, expose another function's traffic, or leave counters/actions attached to stale rules.

## Test Signals

Useful signals include KPU/MKEX profile signature validation, successful parser initialization, correct key extraction for RX and TX interfaces, default NIXLF entries installed at reserved indexes, flow steering tests for each supported key field class, VLAN tag action tests, exact match result decoding, RSS stability after ltype changes, endian build coverage, and MCAM rule allocation/free tests that confirm owner, counter, and enable state remain consistent.
