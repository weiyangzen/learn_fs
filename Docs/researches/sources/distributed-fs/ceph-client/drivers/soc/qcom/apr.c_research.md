# sources/distributed-fs/ceph-client/drivers/soc/qcom/apr.c

## Purpose
Implements the Qualcomm APR/GPR packet-router bus over RPMSG for QDSP6 services. It creates APR/GPR child devices from device tree, routes inbound packets to registered service drivers or dynamic GPR ports, and integrates with PDR service availability notifications.

## Important APIs, Types, And Functions
Exports `apr_send_pkt()`, `gpr_alloc_port()`, `gpr_free_port()`, `gpr_send_pkt()`, `gpr_send_port_pkt()`, `aprbus`, `__apr_driver_register()`, and `apr_driver_unregister()`. Main private state is `struct packet_router` with RPMSG endpoint, service IDR, PDR handle, RX workqueue, and RX list. RX buffers use flexible `struct apr_rx_buf`. Service state is represented by `struct pkt_router_svc` embedded in APR devices and GPR ports.

## Control Flow
`apr_init()` registers `aprbus` then the RPMSG driver. `apr_probe()` reads `qcom,domain` or legacy `qcom,apr-domain`, determines APR versus GPR from compatible, initializes locks/IDR/workqueue/PDR, adds PDR lookups from child nodes, and immediately registers child devices without protection-domain dependencies.

Inbound RPMSG messages enter `apr_callback()`, which validates minimum length, copies the packet into an allocated RX buffer, appends it under `rx_lock`, and queues `apr_rxwq()`. The worker dispatches to `apr_do_rx_callback()` or `gpr_do_rx_callback()`. APR validates header fields, finds the destination service ID in the IDR, builds `apr_resp_pkt`, and calls the bound APR driver callback. GPR validates its header, finds destination port, and invokes the registered port callback.

Child registration is controlled by `of_register_apr_devices()`. It creates APR/GPR devices for children with matching protection-domain state, and `apr_pd_status()` adds or unregisters devices as remote services go up or down. Device removal unregisters child devices and drops IDR entries.

## State And Persistence
Runtime state is in the `packet_router` per RPMSG endpoint: service IDR, RX workqueue/list, PDR handle, and child devices on `aprbus`. Dynamic GPR ports allocate IDs in `0x10000000..0x20000000`. There is no persistent storage.

## Dependencies And Integration Points
Depends on RPMSG, OF child nodes, Qualcomm APR/GPR packet ABI headers, PDR helpers, IDR, workqueues, and Linux driver core bus registration. Audio and DSP service drivers bind to `aprbus`.

## Risks
RX processing copies packets in atomic context and can drop packets on allocation failure. Header validation rejects malformed remote data, but optional header size handling must remain correct. The worker iterates `rx_list` while briefly locking only for deletion, so list mutation ordering relies on single worker plus producer append discipline. Service removal while packets are queued can lead to callback lookup failures. `apr_add_device()` error paths after successful IDR allocation do not visibly remove the IDR entry before returning.

## Test Signals
Probe should create APR/GPR child devices for DT services, PDR up/down should register/unregister protection-domain services, inbound packets should reach the correct callbacks, malformed packets should log and be rejected, and dynamic GPR port allocation should avoid static service ID collisions.
