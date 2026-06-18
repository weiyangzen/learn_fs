# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mbox.h

## Purpose
Defines the RVU mailbox ABI shared by AF, PF, VF, and device block drivers. It includes mailbox memory layout, direction IDs, message headers, helper prototypes, message ID registry, error-code ranges, and payloads for generic RVU, CGX/RPM, NPA, NIX, NPC, PTP, SDP, CPT, MCS, representor events, and CN20K-specific AQ/MCAM operations.

## Important APIs, Types, and Functions
Core layout declarations are `MBOX_SIZE`, down/up TX/RX offsets and sizes, `MBOX_RSP_TIMEOUT`, `MBOX_MSG_ALIGN`, direction constants, `struct otx2_mbox_dev`, `struct otx2_mbox`, `struct mbox_hdr`, and `struct mbox_msghdr`. `MBOX_MESSAGES` and the up-message lists define message IDs and generate `MBOX_MSG_*` enum values. Payload families cover resource attach/detach/free/MSI-X/capability, CGX/RPM link and MAC control, NPA LF/AQ/CN20K AQ, NIX LF/AQ/scheduler/vtag/RSS/RX/FRS/LSO/backpressure/multicast/IPsec/stats, NPC MCAM/counter/flow/KEX/hash/default-rule/CN20K MCAM, PTP, CPT, SDP, MCS MACsec, and representor events.

## Control Flow
The header has no runtime flow, but its macro registry controls handler dispatch and ID/name generation. Message handlers use the request/response structs selected by each `M(...)` row. `otx2_mbox_alloc_msg` wraps `otx2_mbox_alloc_msg_rsp` for messages without explicit response-size reservation.

## State and Persistence Behavior
Mailbox structs are serialized into shared memory and are ABI-persistent across driver components and peer functions. `pcifunc`, ID, signature, version, next offset, and return code define framing. Payloads carry hardware context snapshots, resource IDs, table indexes, stats, link state, and action encodings that persist in AF-managed hardware until later mailbox commands modify them. CN20K payloads embed CN20K context structs and eight-keyword MCAM entries with `action2`.

## Dependencies and Integration Points
Includes Linux Ethernet, size, and ethtool headers plus `rvu_struct.h`, `common.h`, and `cn20k/struct.h`. It is the protocol boundary between `mbox.c` transport and block-specific handlers for MAC, NIX/NPA, NPC flow steering, CPT/IPsec, SDP, MCS, PTP, eswitch/representors, and CN20K context programming.

## Risks
This file is highly ABI-sensitive. Changing IDs, struct sizes, field order, bit definitions, or error-code values can break AF/PF/VF/firmware communication while compiling. Reserved fields protect compatibility. The macro registry is central, and large fixed arrays affect mailbox space limits.

## Test Signals
Generated `MBOX_MSG_*` compile coverage, request/response size checks, AF/PF/VF resource attach/detach, NPA/NIX/CN20K AQ, CGX/RPM link and MAC operations, NPC flow install/delete and CN20K MCAM virtual allocations, PTP, CPT, SDP, MCS, representor up/down events, invalid IDs, signature/version validation, and cross-version compatibility tests.
