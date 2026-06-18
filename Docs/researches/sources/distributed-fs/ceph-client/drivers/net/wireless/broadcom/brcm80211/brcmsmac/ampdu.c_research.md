# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/ampdu.c

Purpose: implements brcmsmac transmit A-MPDU aggregation policy, per-session header rewriting, block-ack status handling, retry decisions, and adaptive FIFO preloading to avoid TX underflows.

Important APIs and functions: `brcms_c_ampdu_attach()`/`detach()` create module state. `brcms_c_ampdu_reset_session()`, `brcms_c_ampdu_add_frame()`, and `brcms_c_ampdu_finalize()` build one aggregate from queued skbs. `brcms_c_ampdu_dotxstatus()` parses hardware status and completes/retries MPDUs. `brcms_c_ampdu_tx_operational()`, `brcms_c_ampdu_macaddr_upd()`, `brcms_c_ampdu_shm_upd()`, `brcms_c_aggregatable()`, and `brcms_c_ampdu_flush()` integrate with station, template RAM, SHM, and DMA.

Control flow: attach initializes per-TID enable masks, BA window sizes, retry limits, max RX factor, max TX length table by MCS/bandwidth/SGI, and FIFO preload tables. Adding frames enforces max frames/bytes, same priority, retry count selection, MCS-dependent aggregate length limits, and marks every MPDU as middle. Finalize fixes first/last MPDU flags, trims last delimiter/padding, updates PLCP lengths, AMPDU bits, mixed-mode lengths, RTS/CTS durations, fallback markers, and preload size. TX status builds BA bitmaps from multi-word hardware status, reports ACKed frames to mac80211, retransmits eligible misses, or completes failures.

State and persistence: `struct ampdu_info` holds policy and adaptive underflow state; `struct scb_ampdu` tracks station/TID retry and release limits. Hardware SHM/template RAM stores BA template address and watchdog/MIMO settings. No disk persistence.

Dependencies and integration: depends on mac80211 skb control blocks, D11 TX headers/status, DMA queues, rate helpers, antenna selection, PHY chanspec, shared memory offsets, and tracepoints.

Risks and test signals: high-risk areas are queue walking across aggregated DMA descriptors, BA bitmap indexing, retry accounting, endian updates in D11 headers, rate fallback PLCP handling, and underflow feedback. Test HT throughput, mixed priorities, fallback rates, RTS/CTS aggregates, tx underflow counters, BA timeout behavior, station teardown flush, and mac80211 tx status correctness.
