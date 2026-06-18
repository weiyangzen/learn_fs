# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_mbx.c

## Purpose
`hclge_mbx.c` implements PF-side mailbox handling for VF and firmware-originated requests. It drains the command receive queue, validates messages, dispatches by mailbox opcode, mutates PF/VF shadow state, invokes hardware configuration helpers, sends synchronous responses when requested, and pushes asynchronous notifications such as link, reset, and port-base VLAN state to VFs.

## Important APIs And Functions
- `hclge_mbx_handler()` is the entry point scheduled by the PF service path. It loops until the CRQ is empty, checks command disable state, validates descriptor ownership and source VF id, traces received messages, dispatches, clears descriptors, advances the CRQ pointer, and writes back the head register.
- `hclge_gen_resp_to_vf()` builds a `HCLGEVF_OPC_MBX_PF_TO_VF` response descriptor, mirrors original code/subcode/match id, bounds response length, maps negative errno to a u16 response status, traces, and sends through the command queue.
- `hclge_send_mbx_msg()` is the common async PF-to-VF sender used by reset, link, and VLAN notifications.
- `hclge_get_ring_chain_from_mbx()`, `hclge_map_unmap_ring_to_vf_vector()`, and `hclge_get_vf_ring_vector_map()` convert VF mailbox ring parameters into `hnae3_ring_chain_node` chains and bind/query interrupt vector mappings.
- VF configuration handlers cover promisc requests, UC/MC MAC updates, VLAN filter and RX strip changes, VF alive/start/stop, MTU, queue id translation, RSS key paging, queue reset, VF reset request, link mode/status, media type, MAC address query, VF FLR cleanup, VF uninit cleanup, NCSI error reset escalation, and VF table clear.
- `hclge_mbx_ops_list[]` maps `HCLGE_MBX_*` opcodes to small handler wrappers that translate results into synchronous responses.

## Control Flow
The receive path is descriptor-driven. `hclge_mbx_handler()` reads CRQ descriptors, verifies `HCLGE_CMDQ_RX_OUTVLD_B`, rejects out-of-range VF ids, and populates `hclge_mbx_ops_param` with the addressed `hdev->vport[mbx_src_vfid]`. `hclge_mbx_request_handling()` looks up the opcode in `hclge_mbx_ops_list`, calls the handler, and sends a response only when `mbx_need_resp` is set and the opcode is below the FLR-status boundary, because PF must not reply to IMP-owned messages.

Configuration requests usually do not program hardware immediately in this file. Promisc and MAC modify paths update vport request/shadow state and schedule the PF service task. VLAN filter, MTU, TQP reset, ring-vector bind, and queue-id translation call direct helpers. Keepalive marks `last_active_jiffies` and transitions initialized VFs to alive, then pushes pending link/reset/VLAN notifications. Link-change messages schedule the PF service task and optionally decode link-failure codes.

## State And Persistence Behavior
The file updates in-memory VF state under `struct hclge_vport`: requested promisc flags, `HNAE3_PFLAG_LIMIT_PROMISC`, MAC/VLAN pending lists, port-base VLAN notification bits, liveness bits, `last_active_jiffies`, `mps`, and queue/vector mapping. It also reads shared PF state such as MAC link/speed/duplex, RSS key, supported/advertising link modes, and reset type. On VF FLR or uninit it removes MAC and VLAN table state, either preserving or deleting list entries depending on the path. NCSI errors set a global reset request through the AE device operations.

## Dependencies And Integration Points
This file depends on `hclge_main.h`, mailbox command layouts from `hclge_mbx.h`, HNAE3 helpers, common RSS state, tracepoints in `hclge_trace.h`, command queue send/read/write helpers, PF vport MAC/VLAN management, reset helpers, and service scheduling. It integrates directly with the VF driver protocol: response payload sizes, opcodes, match ids, and multi-message RSS key/link-mode queries must remain compatible with hns3 VF code and firmware expectations.

## Risks And Edge Cases
- Mailbox payload parsing is offset- and struct-layout-sensitive. Incorrect `msg_len`, ring counts, or untrusted VF indexes could lead to invalid queue/vector operations if validation is incomplete.
- `hclge_errno_to_resp()` stores `abs(errno)` into a u16 and clamps out-of-range values to `EIO`; unusual positive statuses may not map as VF expects.
- Some handlers update shadow state and schedule service work instead of synchronously applying hardware changes, so response success may precede actual hardware programming.
- Link-mode responses only send one `unsigned long` chunk selected by VF query index; compatibility depends on both sides agreeing on bitmap paging.
- `hclge_get_basic_info()` reads `basic_info->pf_caps` from zeroed response storage before setting bits, which is safe only because the response buffer is cleared before dispatch.

## Test Signals
Exercise SR-IOV VF probe, mailbox handshake, VF MAC/VLAN add/delete, spoofed MAC rejection, promisc and limited-promisc requests, RSS key paging with invalid indexes, vector map/unmap/query, VF queue reset, VF initiated reset, PF reset notifications, link changes, NCSI error escalation, and tracepoint output for `hclge_pf_mbx_get/send`. Kernel fault injection around command send and allocation failures should validate response/error paths.
