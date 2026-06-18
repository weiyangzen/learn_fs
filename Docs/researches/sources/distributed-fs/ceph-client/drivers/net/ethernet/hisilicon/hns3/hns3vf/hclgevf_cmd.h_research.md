# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_cmd.h

## Purpose
`hclgevf_cmd.h` defines VF-side command queue constants, command descriptor aliases, hardware register offsets, VF resource/query payloads, queue/vector mapping payloads, and exported command helpers for the HNS3 virtual-function driver.

## Important Types And Constants
- Command queue bits include RX invalid/out-valid bits, RX ring head sync enable, NIC reset-ready bit, default CMQ descriptor count, descriptor-count shift, and query-device-specs BD count.
- TQP register constants define VF TQP register offset/size, v2 maximum size, and extended register offset.
- `struct hclgevf_tqp_map` describes PF/VF task queue pair mapping with absolute TQP id, VF id, map type/enabled flag, and virtual id.
- `enum hclgevf_int_type` and `struct hclgevf_ctrl_vector_chain` encode vector-to-TX/RX/event cause mappings with up to ten TQP elements per command.
- `struct hclgevf_query_res_cmd` reports VF queue count, MSI-X bases, and VF interrupt vector count.
- GRO, link status, common TQP queue enable, TX queue pointer, and device specs command structs define firmware descriptor payloads.
- `hclgevf_cmd_setup_basic_desc()` aliases the common command descriptor setup helper.
- Exported functions are `hclgevf_cmd_send()` and `hclgevf_arq_init()`.

## Control Flow And Integration
The VF main implementation includes this header to send firmware/PF commands, initialize async receive queues, query resources and device specs, map interrupt vectors, enable queues, configure GRO, query link, and participate in reset readiness. VF mailbox code also relies on `hclgevf_cmd_send()` when exchanging descriptors with PF/firmware.

## State And Persistence Behavior
The header defines wire-format command state rather than owning runtime state. Values returned through these payloads populate VF device state in `hclgevf_main.c`, such as queue counts, interrupt vector counts, device limits, and link status. Reset readiness bits and queue enable commands affect hardware-visible VF state that must be restored after reset.

## Dependencies And Risks
The header depends on Linux IO/types, `hnae3.h`, and `hclge_comm_cmd.h`. Firmware layout compatibility is the dominant risk: bit positions, little-endian fields, descriptor counts, and structure padding must match hardware. The TQP id masks and vector element limit must be checked by callers before filling command payloads.

## Test Signals
Validate VF probe resource query, interrupt vector mapping, queue enable/disable, GRO configuration, link status query, reset readiness, device specs query over four BDs, and command timeout/error handling in `hclgevf_cmd_send()`.
