# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/mhi_wwan_ctrl.c

Purpose: exposes MHI control channels such as DUN, MBIM control, QMI, DIAG, FIREHOSE, and NMEA as WWAN character ports.

Important APIs/functions: `mhi_wwan_ctrl_probe()` allocates `struct mhi_wwan_dev`, records UL/DL capabilities from MHI channels, and creates a WWAN port of the type stored in the MHI ID table. `mhi_wwan_ctrl_start()` prepares MHI transfers, initializes RX budget from free DL descriptors, and refills RX buffers. `mhi_wwan_ctrl_tx()` queues outgoing SKBs with `mhi_queue_skb()` and turns TX off when the MHI queue is full. `mhi_ul_xfer_cb()` frees completed TX SKBs and re-enables WWAN TX. `mhi_dl_xfer_cb()` sets received SKB length and forwards it to `wwan_port_rx()`. RX refill is budgeted by `mhi_wwan_rx_budget_dec/inc()` and an SKB destructor.

Control flow and state: `flags` track channel capability and refill state. `rx_budget` limits outstanding RX buffers to descriptor capacity and is replenished only when WWAN core releases an SKB. `tx_lock` serializes TX queue state with callbacks; `rx_lock` protects budget and refill scheduling.

Dependencies and integration points: depends on MHI bus APIs and WWAN port core. The MHI channel-name table maps firmware channels to WWAN port types.

Risks and test signals: RX buffer lifetime relies on the SKB destructor, so leaks or missing destructor calls stall refill. Test start/stop, full TX queue backpressure, DL overflow tolerance, all listed channel names, and remove while work is pending.
