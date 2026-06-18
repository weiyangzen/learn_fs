# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/mhi_wwan_mbim.c

Purpose: implements raw-IP network links carrying MBIM/NCM-framed traffic over an MHI data channel, primarily `IP_HW0_MBIM`.

Important APIs/functions: `mhi_mbim_probe()` prepares MHI transfer, records RX queue size, initializes delayed RX refill, and registers WWAN netdev ops. `mhi_mbim_newlink()` creates per-session links in an RCU hlist; some Foxconn controllers offset sessions using mux ID 112. `mhi_mbim_ndo_xmit()` wraps an IP packet with `mbim_tx_fixup()` into an NTH16/NDP16 header and queues it to MHI. `mhi_mbim_dl_callback()` handles MHI RX completion, including `-EOVERFLOW` aggregation through `frag_list`, then calls `mhi_mbim_rx()`. `mhi_mbim_rx()` validates NTH16/NDP16 headers, iterates NDPs and datagram entries, finds the session link, classifies IPv4/IPv6, accounts stats, and calls `netif_rx()`.

Control flow and state: `struct mhi_mbim_context` owns MHI device, RX aggregation head/tail, MRU, RX queue size, sequence counters, delayed refill work, TX lock, and link hash table. Per-link `u64_stats` provide lockless netdev stats. Netdev open schedules refill and starts queue; stop disables carrier/queue.

Dependencies and integration points: depends on MHI, WWAN core, USB CDC NCM/MBIM header definitions, raw-IP netdev semantics, RCU, and `u64_stats_sync`.

Risks and test signals: validate MBIM offsets/lengths, sequence wrap, multi-fragment MHI aggregation, RCU link deletion, TX queue wake, and controller-specific mux IDs. Test with malformed NTBs, multiple sessions, queue-full TX, and remove with partial aggregation.
