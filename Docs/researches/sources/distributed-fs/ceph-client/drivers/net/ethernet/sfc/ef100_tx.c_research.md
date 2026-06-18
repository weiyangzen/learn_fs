# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_tx.c

Purpose: Implements EF100 transmit queue allocation/init, descriptor construction, TX completions, skb enqueue, TSOv3, checksum and VLAN offload descriptors, doorbells, and representor egress override descriptors.

Important APIs and functions: `ef100_tx_probe()` allocates descriptor storage with an extra QMDA completion entry. `ef100_tx_init()` binds the core netdev TX queue and initializes hardware TXQ via MCDI. `ef100_tx_write()` pushes raw queued buffers. `ef100_ev_tx()` handles TX completion events. `ef100_enqueue_skb()` and `__ef100_enqueue_skb()` are the main transmit entry points. Static helpers validate TSO (`ef100_tx_can_tso()`), compose SEND/SEG/TSO/PREFIX descriptors, set partial checksum and VLAN insertion, and ring doorbells.

Control flow: Enqueue validates queue availability, computes GSO segment count, reserves a TSO metadata buffer when EF100 TSOv3 can handle the skb, or falls back to software TSO. Representor sends reserve an option buffer for an egress mport override and reject traffic that would stop the parent PF queue. Data is DMA mapped through common TX helpers, descriptors are written in ring order, `write_count` is published with barriers, BQL and fill-level thresholds decide queue stop/start, and a doorbell is pushed unless `xmit_more` can batch safely. Completion events map descriptor counts to a TX index and call common completion cleanup.

State and persistence: Mutates `insert_count`, `write_count`, `notify_count`, `packet_write_count`, `xmit_pending`, per-buffer flags, TX statistics (`tx_packets`, `tso_bursts`, `tso_packets`, fallback counters), BQL completions, and representor error counters. No durable persistence exists, but descriptor ring state and memory ordering are critical.

Dependencies and integration points: Uses common TX mapping/unwind/completion helpers, EF100 register fields from `ef100_regs.h`, MCDI TX initialization, netdev BQL APIs, checksum helpers, VLAN tag APIs, XDP/raw TX path conventions, and `ef100_rep.h` for VF representor traffic.

Risks: Descriptor count accounting is complex for TSO, raw writes, and representor prefix descriptors. The code modifies the TCP checksum field for TSO metadata, so skb ownership expectations matter. Queue stop thresholds must leave a descriptor unused. Memory barriers before doorbells and after `write_count` publication protect against hardware and completion races. Representor traffic intentionally drops rather than backpressuring, which can surprise callers.

Test signals: Cover normal skb TX, `xmit_more` batching, doorbell after >255 descriptors, TSOv3 accepted and fallback paths, GSO partial/encapsulated variants, VLAN and checksum offloads, queue stop/wake behavior, TX completion indexing, XDP/raw TX, representor mport override sends, and enqueue error unwind freeing skbs.
