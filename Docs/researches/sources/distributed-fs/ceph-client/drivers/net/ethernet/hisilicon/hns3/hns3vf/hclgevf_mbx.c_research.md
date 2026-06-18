# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_mbx.c

Implements HNS3 VF mailbox send, synchronous PF response waiting, command receive queue draining, and deferred async PF notification handling. Public functions are `hclgevf_send_mbx_msg()`, `hclgevf_mbx_handler()`, and `hclgevf_mbx_async_handler()`.

Synchronous sends lock `mbx_resp.mbx_mutex`, reset response state, assign a nonzero match ID, send `HCLGEVF_OPC_MBX_VF_TO_PF`, and poll for up to 500 iterations unless command queue disable is seen. CRQ handling validates descriptors, traces traffic, handles response messages immediately, and enqueues async link/reset/link-mode/VLAN/promisc messages into the ARQ ring for service-task processing.

State lives in `hdev->mbx_resp` and `hdev->arq`; async handling updates link speed/duplex/status, supported/advertising modes, reset pending bits, PF-push-link status, and port-base VLAN info. Dependencies are mailbox ABI structs/opcodes, command queues, tracepoints, and exported update/schedule helpers. Risks include stale or mismatched responses, ARQ overflow dropping events, memory-ordering bugs around `received_resp`, and command-queue-disabled deferrals. Test with matched/unmatched responses, timeouts, ARQ full, PF-pushed link/VLAN/reset events, and tracepoint output.
