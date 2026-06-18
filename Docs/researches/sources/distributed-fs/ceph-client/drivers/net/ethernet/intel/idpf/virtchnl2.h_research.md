# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/virtchnl2.h

## Purpose
Defines the virtchnl2 wire ABI used between the IDPF data-plane driver and the device control plane. It assigns stable opcode, capability, queue, protocol, PTP, RSS, flow steering, and event constants, and declares the little-endian message structures exchanged over mailbox control queues.

## Important APIs, Types, And Structures
`enum virtchnl2_op` lists control-plane operations from version negotiation and capability exchange through vport lifecycle, queue configuration, vectors, RSS, SR-IOV, events, stats, PTP, LAN memory regions, and flow rules. Capability enums define checksum, segmentation, RSS/flow types, header split, RSC, other device features, PTP features, and sideband action types. Queue model/type enums describe single versus split queues and TX/RX/completion/buffer queue types.

Core message structs include `virtchnl2_version_info`, `virtchnl2_get_capabilities`, `virtchnl2_create_vport`, `virtchnl2_vport`, `virtchnl2_txq_info`, `virtchnl2_config_tx_queues`, `virtchnl2_rxq_info`, `virtchnl2_config_rx_queues`, `virtchnl2_add_queues`, `virtchnl2_vector_chunk(s)`, `virtchnl2_alloc_vectors`, RSS key/LUT/hash messages, `virtchnl2_get_ptype_info`, `virtchnl2_vport_stats`, `virtchnl2_event`, queue chunk and queue-vector map messages, loopback, MAC address list, promiscuous mode, PTP capability and timestamp messages, LAN memory region messages, and flow steering rule/action structures. `VIRTCHNL2_CHECK_STRUCT_LEN()` static assertions pin fixed struct sizes.

## Control Flow
This header has no executable control flow. It defines the protocol sequence consumed by `idpf_virtchnl.c`: negotiate version, request capabilities, create vports, configure and enable queues/vectors, and then perform feature operations such as RSS, stats, MAC filters, PTP, and flow steering. Flexible-array structures are sized by count fields and are typically sent in chunks when the payload can exceed a mailbox buffer.

## State And Persistence
The ABI describes serialized state owned by the control plane and cached by the driver: capabilities, vport IDs and flags, queue IDs and tail register chunks, vector IDs and register offsets, RSS tables and keys, packet type tables, PTP offsets/latches, LAN memory regions, and flow rule IDs/status. All multibyte fields use little-endian types because driver and control plane may run on platforms with different endianness. Existing enum values and struct layouts are persistent compatibility contracts and should not be renumbered or resized casually.

## Dependencies And Integration Points
The header includes Ethernet address definitions and uses Linux endian, bit, and flexible-array annotations. It is included by `idpf_virtchnl.h` and indirectly by the main IDPF control-plane implementation. It is paired with `virtchnl2_lan_desc.h` for descriptor ID values and with PTP, RSS, queue, and flow steering code that serializes these structs.

## Risks
ABI drift is the largest risk. Opcode values, enum values, struct sizes, padding, endian annotations, and flexible-array count semantics must remain compatible with firmware/control-plane implementations. Several comments note reserved values and mandatory protocol IDs; changing them can break negotiation or packet parsing. Flexible message structs need caller-side bounds checks against mailbox buffer size and reply size. Flow steering structures are large and bounded by maximum protocol headers, raw packet size, actions, and rule count; callers must ensure control-plane limits are respected.

## Test Signals
Compile-time `static_assert` checks catch fixed-size layout changes. Runtime signals include successful virtchnl version/capability negotiation, queue/vport/RSS/PTP/flow rule operations against real or emulated control planes, endian correctness tests on serialized buffers, short/oversized flexible-array reply rejection, and compatibility testing across firmware versions that implement virtchnl2 version 2.0.
