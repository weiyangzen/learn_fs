# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmutil/utils.c

Purpose: Provides exported Broadcom utility functions for SKB allocation/free, multi-precedence packet queues, board/dot revision string formatting, and optional debug hex dumping.

Important APIs: `brcmu_pkt_buf_get_skb/free_skb()`, enqueue/dequeue variants (`penq`, `penq_head`, `pdeq`, `pdeq_match`, `pdeq_tail`), flush functions, `brcmu_pktq_init()`, `brcmu_pktq_peek_tail()`, `brcmu_pktq_mlen()`, `brcmu_pktq_mdeq()`, `brcmu_boardrev_str()`, `brcmu_dotrev_str()`, and DEBUG-only `brcmu_prpkt()`/`brcmu_dbg_hex_dump()`.

Control flow and state: Packet queues mutate `struct pktq` length, high-precedence hint, and per-precedence `sk_buff_head`s. Enqueue rejects full total/per-precedence queues. Dequeue/flush unlink SKBs and adjust lengths. `mdeq` refreshes `hi_prec` downward before selecting the highest non-empty requested precedence. String helpers format caller-provided buffers.

Dependencies and integration: Uses Linux netdevice/SKB/module APIs and `brcmu_utils.h`; exports symbols for Broadcom wireless modules. Risks include callers needing external locking, potential stale `hi_prec` edge cases in `peek_tail`, WARN on freeing chained SKBs, fixed caller buffer lengths, and callback semantics in flush/dequeue-match. Test signals include queue overflow, precedence ordering, selective flush, concurrent caller lock coverage, revision formatting, DEBUG builds, and module load metadata.
