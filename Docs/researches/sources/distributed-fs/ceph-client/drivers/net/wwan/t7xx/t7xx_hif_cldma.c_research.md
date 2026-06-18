# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_cldma.c

Purpose: implements the high-level CLDMA host interface for t7xx control channels, managing GPD rings, TX/RX workqueues, runtime PM, PCIe sleep locks, CLDMA interrupts, and modem PM callbacks.

Important APIs/functions: `t7xx_cldma_init()` registers PM entity, creates ordered workqueues, and hooks the PCIe interrupt. `t7xx_cldma_switch_cfg()` configures shared or dedicated queue sizing and performs late ring allocation. `t7xx_cldma_start()` programs TX/RX ring start addresses, starts RX queues, and enables interrupts. `t7xx_cldma_send_skb()` maps an outgoing SKB to a TX GPD, waits for budget if needed, disables PCIe sleep, and starts/resumes hardware. RX is drained by `t7xx_cldma_gpd_rx_collect()` and delivered through `t7xx_port_proxy_recv_skb()` callbacks. TX completions are reclaimed by `t7xx_cldma_gpd_tx_collect()`. PM callbacks split suspend/resume into TX and RX phases.

Control flow and state: `struct cldma_ctrl` owns eight TX/RX queues, queue active bitmaps, DMA pool, rings, hardware info, PM entity, and init state. Each queue has ring pointers (`tr_done`, `tx_next`, `rx_refill`), budget, waitqueue, lock, and ordered worker. GPD HWO bits synchronize ownership with hardware.

Dependencies and integration points: depends on low-level CLDMA ops, t7xx PCIe MAC interrupts, MHCCIF masking, port proxy receive callbacks, runtime PM, DMA pools, and PCIe sleep-lock helpers.

Risks and test signals: GPD ownership races, runtime PM failures, TX budget waits, RX refill allocation, PCIe disconnect handling, and suspend/resume ordering are high risk. Test heavy control traffic, queue-full TX, dedicated dump queue config, modem reset, PCIe link loss, and PM cycles.
