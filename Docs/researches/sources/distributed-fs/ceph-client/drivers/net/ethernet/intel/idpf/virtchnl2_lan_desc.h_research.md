# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/virtchnl2_lan_desc.h

## Purpose
Defines virtchnl2 LAN transmit and receive descriptor identifiers, bit masks, and descriptor writeback formats used by the IDPF datapath. It is an ABI-style hardware descriptor contract for single queue and split queue receive paths and for selected transmit descriptor capabilities.

## Important APIs, Types, And Structures
`enum virtchnl2_tx_desc_ids` advertises supported TX descriptor profiles such as data, context, flex TSO context, flex L2 tag descriptors, flow scheduling, and descriptor-done. `enum virtchnl2_rx_desc_ids` and `enum virtchnl2_rx_desc_id_bitmasks` define base and flex RX descriptor IDs, including the shared profile ID for split queue and single queue flex NIC descriptors.

The header defines bit masks for splitq advanced flex descriptor fields, status/error sections, ptype, packet length, generation bit, buffer queue ID, header length, RSC, split header, timestamp valid bit, and base descriptor status/error fields. Descriptor structures include `virtchnl2_splitq_rx_buf_desc`, `virtchnl2_singleq_rx_buf_desc`, `virtchnl2_singleq_base_rx_desc`, `virtchnl2_rx_flex_desc_nic`, `virtchnl2_rx_flex_desc_adv_nic_3`, and the common `union virtchnl2_rx_desc`.

## Control Flow
This header has no executable control flow. Runtime code fills buffer descriptors before handing them to hardware and decodes writeback descriptors after hardware completion. XDP metadata and RX processing code read fields such as ptype, length, RSS hash, timestamp low/high bits, buffer ID, generation bit, and completion status using these layouts and masks.

## State And Persistence
Descriptor rings are DMA-visible state shared between driver and hardware. The structures describe on-ring memory layout and must match device writeback behavior exactly. Enum values and bit positions are persistent hardware/firmware ABI and cannot be renumbered without breaking descriptor negotiation and parsing.

## Dependencies And Integration Points
The header depends on Linux bit helpers. It is consumed by IDPF TX/RX code, XDP descriptor helpers in `xdp.h`, queue configuration in `idpf_virtchnl.c` through descriptor ID masks, checksum/RSS/timestamp extraction, and any datapath path that distinguishes single queue base/flex and split queue advanced descriptors.

## Risks
Bitfield interpretation bugs can corrupt packet length, completion status, RSS hash, buffer selection, timestamp validity, or checksum error handling. The split queue and single queue flex descriptors share RX descriptor ID 2, so callers must also use the negotiated queue model to choose the correct layout. Direct word access under `__LIBETH_WORD_ACCESS` assumes the descriptor struct layout and alignment match the optimized loads used elsewhere. Descriptor ABI changes require careful coordination with control-plane capability negotiation and hardware documentation.

## Test Signals
Signals include RX/TX traffic across single queue and split queue modes, checksum and RSS validation, timestamp metadata extraction, XDP receive metadata tests, ring wrap and generation-bit handling, base versus flex descriptor selection, compile-time structure size checks where present in consumers, and hardware/firmware interoperability tests for descriptor IDs advertised in vport creation.
