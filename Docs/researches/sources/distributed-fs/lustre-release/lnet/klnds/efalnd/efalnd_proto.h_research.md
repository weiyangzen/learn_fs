# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_proto.h

## Purpose
This private header defines the EFALND wire protocol: completion status codes, metadata entries, QP descriptors, RDMA descriptors, connection handshake messages, data-transfer messages, common headers, protocol versions, and message type IDs.

## Important APIs, Types, And Functions
`enum kefa_comp_status` maps remote completion/error outcomes. Packed structs include `kefa_nid_md_entry`, `kefa_qp_proto`, `kefa_rdma_desc`, v2 immediate/PUTR/GETR request bodies, `kefa_getr_ack_msg`, `kefa_completion_msg`, connection probe/response/request/ack payloads, `kefa_msg_v1`, `kefa_msg_v2`, `kefa_hdr`, and top-level `kefa_msg`. Constants define magic (`EFALND_MSG_MAGIC`), protocol versions 1 and 2, min/max protocol versions, and message type IDs from connection probe through GETR done.

## Control Flow
Every EFALND packet starts with `kefa_hdr`; the receiver validates magic, protocol version, type, and total byte count before interpreting the version-specific body. V1 supports only probe/probe response with legacy `lnet_nid_t` fields. V2 carries large NIDs and all data-transfer messages. RDMA flows exchange descriptors and opaque TX-index cookies, then complete with status messages.

## State, Persistence, And Dependencies
The structs are packed wire ABI and must remain stable for inter-node compatibility. There is no live state in the header. It depends on LNet header structures such as `lnet_hdr_nid16`, `lnet_nid_t`, and `struct lnet_nid`.

## Integration Points
`efalnd.c` builds/parses data messages and maps status codes to errno. `efalnd_connection.c` builds/parses handshake messages and negotiates protocol versions. `efalnd_peerni.c` uses `kefa_nid_md_entry` for metadata exchange in LNet ping replies.

## Risks
Adding fields after flexible arrays or unions would break layout; comments explicitly prohibit adding fields after several unions. Mismatched `hdr.nob` calculations can cause short-packet rejection or overread. Version negotiation must preserve V1 probe compatibility while using V2 for data traffic. Status-code mapping must stay synchronized with sender behavior.

## Test Signals
Tests should assert packed sizes/offsets, message-size calculations for every type/version, protocol min/max negotiation, malformed magic/version/length rejection, RDMA cookie round trips, and errno/status conversion coverage.
