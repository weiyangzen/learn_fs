# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_msg_abi.h

## Purpose

This packed ABI header defines a broader IPU firmware graph/task messaging protocol, mainly for processing-system style graph execution: device open/close, graph open/close, task request/done, terminals, links, compression options, profiles, and error codes.

## Important APIs, Types, and Functions

Key enums define message types, node/profile/link/term types, device/graph/task states, and error groups. Key structs include `ipu7_msg_node_profile`, `ipu7_msg_cb_profile`, `ipu7_msg_node`, `ipu7_msg_link_cmprs_option`, `ipu7_msg_link`, `ipu7_msg_task`, `ipu7_msg_task_done`, `ipu7_msg_term`, `ipu7_msg_term_event`, `ipu7_msg_dev_open`, `ipu7_msg_dev_close`, `ipu7_msg_graph_open`, and graph ack/close structs. Queue constants define FWPS input/output queue counts and message size caps.

## Control Flow

The header itself has no control flow. Consumers construct TLV-backed device/graph/task messages, enqueue them to firmware, then parse ack/done/event responses with embedded common ack headers.

## State and Persistence Behavior

State is message-payload memory shared with firmware. Device, graph, and task states are protocol-visible state machines rather than host-owned globals.

## Dependencies and Integration Points

It includes common GOFO ABI types and reuses common message header/error structures. It is part of the IPU7 firmware ABI family and aligns with syscom queue IDs.

## Risks and Edge Cases

TLV lists, compression option sizing, bitmap dimensions, max terminal count, and queue ID ranges are ABI-sensitive. Graph open errors have many memory/resource failure modes, so host diagnostics must retain error group/code/detail.

## Test Signals

ABI compile checks, struct size/offset verification, graph open/close with compression options, invalid graph/task IDs, and firmware ack error propagation are key signals.
