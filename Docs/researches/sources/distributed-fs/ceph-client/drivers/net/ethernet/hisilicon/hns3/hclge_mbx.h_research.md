# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hclge_mbx.h

## Purpose

`hclge_mbx.h` defines the HNS3 PF/VF and firmware mailbox protocol structures, opcodes, subcodes, message limits, async-response ring, and helper pointer-move macros. It is the shared protocol ABI for commands such as reset, MAC/VLAN filtering, queue/vector mapping, RSS, link status, base config, MTU, queue reset, keepalive, media type, VF table handling, and M7 firmware notifications.

## Important APIs, Types, And Functions

`enum HCLGE_MBX_OPCODE` enumerates VF-to-PF, PF-to-VF, and M7-to-PF message codes. Subcode enums define MAC/VLAN operations and table operations. Size constants include `HCLGE_MBX_MAX_MSG_SIZE`, `HCLGE_MBX_MAX_RESP_DATA_SIZE`, `HCLGE_MBX_MAX_RING_CHAIN_PARAM_NUM`, scheduler/reset timeouts, ARQ message size/count, opcode max, and push-link-status enable bit.

Important structs include `hclge_ring_chain_param`, `hclge_basic_info`, `hclgevf_mbx_resp_status`, `hclge_respond_to_vf_msg`, `hclge_vf_to_pf_msg`, `hclge_pf_to_vf_msg`, command descriptors for VF-to-PF and PF-to-VF mailbox commands, VF reset command, packed payloads for link status/mode, port base VLAN, queue info/depth, VLAN filter, MTU info, `hclgevf_mbx_arq_ring`, and `hclge_mbx_ops_param`. `hclge_mbx_ops_fn` is the PF operation callback signature.

## Control Flow

The header has no executable functions, but the protocol flow is explicit. A VF sends `hclge_mbx_vf_to_pf_cmd` with opcode/subcode/data and optional response request; PF handlers receive it through a `hclge_mbx_ops_fn`, fill `hclge_respond_to_vf_msg`, and send `hclge_mbx_pf_to_vf_cmd`. Asynchronous PF messages are queued in the VF ARQ ring, whose head/tail macros wrap modulo `HCLGE_MBX_MAX_ARQ_MSG_NUM`. Response matching uses mutex-protected `hclgevf_mbx_resp_status`, `origin_mbx_msg`, `match_id`, status, and additional data.

## State And Persistence

Mailbox state is transient command/response data plus VF-side response status and async ring indices/count. The ABI structures are packed where firmware byte layout matters. Persistent configuration affected by these messages lives elsewhere in PF/VF device state and hardware tables.

## Dependencies And Integration Points

The header includes Linux init, mutex, and types headers and forward-declares PF/VF device types. It is consumed by HNS3 PF mailbox, VF mailbox, reset, link, RSS, VLAN, MAC, queue-vector, and keepalive code. It also bridges firmware-originated M7 notifications to PF logic.

## Risks And Test Signals

Risks include ABI/layout drift, endian mistakes in `__le16/__le32/__le64` fields, opcode/subcode mismatch between PF and VF, async ring overflow, response match-id races, and insufficient validation of `msg_len`. Test signals include PF/VF mailbox negotiation, VF reset and FLR flows, MAC/VLAN/RSS/MTU operations from VF, async link status delivery, keepalive handling, ARQ wraparound, and sparse/endian checks.
