# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_txrx.h

Purpose: Declares the Ionic TX/RX fast-path entry points used by queue setup, netdev operations, NAPI registration, XDP ndo hooks, and reset/teardown code.

Important APIs: Declares RX management (`ionic_rx_fill`, `ionic_rx_empty`, `ionic_rx_service`), TX management (`ionic_tx_flush`, `ionic_tx_empty`, `ionic_start_xmit`), NAPI pollers (`ionic_rx_napi`, `ionic_tx_napi`, `ionic_txrx_napi`), and XDP transmit (`ionic_xdp_xmit`). It forward-declares `struct bpf_prog` so RX fill can account for XDP headroom without forcing BPF includes into all users.

Control flow: Callers wire these functions into netdev and NAPI operations: TX packets enter through `ionic_start_xmit`, external XDP frames through `ionic_xdp_xmit`, interrupts schedule one of the NAPI pollers, and teardown invokes empty/flush helpers.

State and persistence behavior: No state is stored in the header. It defines module boundaries over `struct ionic_queue`, `struct ionic_cq`, `struct napi_struct`, and netdev objects.

Dependencies and integration points: Integrates the Ionic implementation with Linux netdev, NAPI, and XDP APIs. Include order must provide Ionic queue/CQ structures to callers.

Risks: Signature changes affect netdev/NAPI hook registration across the driver. The presence of both split and combined NAPI pollers means setup code must bind the correct one for the interrupt mode.

Test signals: Build coverage and runtime smoke tests for queue bring-up/teardown, NAPI mode selection, and XDP ndo registration.
