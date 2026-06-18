# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_trace.h

## Purpose
`hclge_trace.h` defines Linux tracepoints for HNS3 PF mailbox and command-queue activity. It provides structured observability for PF receiving VF mailbox requests, PF sending mailbox responses/notifications, and PF command descriptors sent to or received from firmware.

## Important Trace Events
- `hclge_pf_mbx_get` captures source VF id, mailbox code/subcode, PCI name, netdev name, and the raw VF-to-PF mailbox command as a u32 array.
- `hclge_pf_mbx_send` captures destination VF id, PF-to-VF mailbox code, PCI name, netdev name, and the raw PF-to-VF mailbox command.
- `hclge_pf_cmd_template` is a reusable event class for normal command descriptors, recording opcode, flag, retval, reserved field, descriptor index, descriptor count, PCI name, and descriptor data words.
- `hclge_pf_cmd_send` and `hclge_pf_cmd_get` instantiate the normal descriptor template.
- `hclge_pf_special_cmd_template` traces special command data as a descriptor-sized u32 array.
- `hclge_pf_special_cmd_send` and `hclge_pf_special_cmd_get` instantiate the special descriptor template.

## Control Flow And Integration
`hclge_mbx.c` defines `CREATE_TRACE_POINTS` before including this header, making it the tracepoint definition unit. Command code elsewhere can include the header and call the generated trace functions. The trace header sets `TRACE_SYSTEM hns3`, uses the standard include-guard plus `TRACE_HEADER_MULTI_READ` pattern, then sets `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE hclge_trace` before including `<trace/define_trace.h>`.

## State And Dependencies
The tracepoints read live `hclge_dev`, `hclge_comm_hw`, mailbox command, and command descriptor fields but do not mutate state. They depend on kernel tracepoint infrastructure, command/mailbox struct definitions being visible before use, PCI and netdev names being valid, and descriptor data lengths from common HNS3 headers.

## Risks And Edge Cases
- Raw mailbox and descriptor data may include sensitive or high-volume information; tracing should be enabled deliberately.
- `hdev->vport[0].nic.kinfo.netdev->name` is accessed in trace assignment; trace calls before netdev setup or after teardown would risk invalid pointers.
- Struct-size-derived array lengths couple trace ABI to command layout. Layout changes alter trace payload shape.

## Test Signals
Enable ftrace/perf trace events for `hns3:*` while exercising VF mailbox requests and firmware commands. Confirm event registration, field decoding, PCI/netdev names, raw arrays, and no crashes during probe/reset/remove with tracing enabled.
