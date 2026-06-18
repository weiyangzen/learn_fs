# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif_rx.c

Purpose: implements the DPMAIF receive path for t7xx, including BAT/PIT allocation, RX buffer provisioning, PIT parsing, fragmented packet assembly, NAPI polling, BAT/PIT release back to hardware, and RX shutdown cleanup.

Important APIs/functions: `t7xx_dpmaif_bat_alloc()` allocates coherent BAT rings plus software SKB/page tables and bitmaps. `t7xx_dpmaif_rx_buf_alloc()` fills normal BAT entries with DMA-mapped SKBs and optionally notifies hardware. `t7xx_dpmaif_rx_frag_alloc()` fills fragment BAT entries with page fragments. `t7xx_dpmaif_napi_rx_poll()` acquires PCIe sleep lock, drains PIT entries within budget, completes/unmasks RX interrupts, and releases PM references. `t7xx_dpmaif_rx_start()` walks PIT descriptors, parses MSG PIT metadata, consumes PD PIT payload/fragment descriptors, assembles SKBs, and delivers them through `callbacks->recv_skb()`. `t7xx_dpmaif_bat_release_work()` releases consumed BAT entries and allocates replacements.

Control flow and state: RX queues track PIT read/write/release indexes and expected PIT sequence. Normal BAT SKBs and fragment BAT pages are marked consumed in bitmaps, then batch-released when thresholds are reached. Current packet assembly lives in `rx_data_info` until a non-continuation PIT completes the packet.

Dependencies and integration points: depends on DPMAIF hardware index APIs, t7xx PCI sleep-lock/runtime PM, NAPI/GRO, DMA mapping, page fragments, and netdev callbacks in `t7xx_netdev`.

Risks and test signals: PIT sequence polling, fragment bounds, SKB tailroom, BAT bitmap/index mismatch, sleep-lock retry, and shutdown while NAPI runs are high risk. Test fragmented and non-fragmented RX, checksum flags, multi-queue interrupts, malformed PITs, BAT refill thresholds, PM suspend, and modem stop/exception.
