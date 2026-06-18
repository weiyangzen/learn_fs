
# sources/distributed-fs/ceph-client/include/linux/ntb_transport.h

Purpose: declares the higher-level NTB transport client API that builds queue pairs over NTB memory windows and doorbells.

Important APIs/types/functions: `struct ntb_transport_client` supplies probe/remove callbacks for transport devices. `ntb_transport_register_client()`, `ntb_transport_unregister_client()`, `ntb_transport_register_client_dev()`, and `ntb_transport_unregister_client_dev()` manage clients and named devices. `struct ntb_queue_handlers` supplies receive, transmit, event, and error callbacks. Queue APIs create/free queue pairs, enqueue RX/TX buffers, remove RX buffers, bring links up/down, and query link state.

Control flow: a transport client registers, receives a queue-pair device in probe, allocates a queue with handlers, posts receive buffers, enqueues transmit buffers, and reacts to link/event/error callbacks. Link helpers expose per-queue state independently of raw NTB link state.

State and persistence: queue-pair state lives in the transport implementation: posted buffers, callbacks, link state, and NTB resources. This header stores only opaque handles and callback contracts.

Dependencies and integration points: depends on NTB core, `struct device`, and transport implementation. It integrates raw NTB resources with client protocols that want message queues rather than direct doorbell/window management.

Risks and test signals: risks include buffer ownership ambiguity after enqueue/remove, callbacks racing with queue free, link state mismatch between NTB and transport, and missing RX buffers causing dropped traffic. Test signals include ntb_netdev/ntb_pingpong style traffic, queue teardown during link down, callback ordering tests, and buffer leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ntb_transport.h -->
