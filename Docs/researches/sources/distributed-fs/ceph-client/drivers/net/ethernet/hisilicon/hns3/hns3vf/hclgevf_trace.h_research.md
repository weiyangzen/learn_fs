# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_trace.h

Defines HNS3 VF tracepoints for mailbox receive/send and command queue descriptor send/get under trace system `hns3`. Events are `hclge_vf_mbx_get`, `hclge_vf_mbx_send`, `hclge_vf_cmd_send`, and `hclge_vf_cmd_get`.

Tracepoint assignment captures PCI name, netdev name, VF ID, opcode/subcode, descriptor flags/retval, and raw mailbox/descriptor words. It does not mutate driver state; data persists only in kernel tracing buffers. `CREATE_TRACE_POINTS` is set from `hclgevf_mbx.c`, while command tracing is wired through common CMQ ops in `hclgevf_main.c`.

Dependencies are Linux tracepoint infrastructure and HNS3 mailbox/descriptor structs. Risks include dereferencing netdev fields before NIC registration and user-space trace consumer ABI sensitivity. Test by enabling `hns3` ftrace/perf events while exercising mailbox and command queue paths.
