# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_handlers.h

Purpose: Declares the two RMNET packet-handler entry points shared between virtual device and configuration code.

Important APIs: `void rmnet_egress_handler(struct sk_buff *skb)` accepts an skb transmitted on an RMNET virtual net_device and rewrites it for the real lower device. `rx_handler_result_t rmnet_rx_handler(struct sk_buff **pskb)` is registered as an RX handler on the real device and consumes or passes ingress frames.

Control flow and integration: This header is included by `rmnet_vnd.c` so VND TX can call the egress path, and by configuration or lower-device setup code that installs the RX handler. It includes `rmnet_config.h` for shared type visibility.

State and persistence: No state is defined here. It exposes functions that operate on SKBs, per-device private state, and RMNET ports maintained elsewhere.

Risks and test signals: API stability matters because these functions are boundary points between RMNET net_device operations and lower-device RX handling. Build coverage should ensure prototypes remain synchronized with implementation, and runtime tests should verify RX handler registration and VND TX call paths.
