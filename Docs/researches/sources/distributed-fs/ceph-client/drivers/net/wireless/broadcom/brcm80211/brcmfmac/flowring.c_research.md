# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/flowring.c

Purpose: Manages msgbuf TX flowrings by mapping destination/prio/interface tuples to firmware flow IDs, queuing SKBs, and applying flow control when per-ring queues exceed thresholds.

Important APIs/types/functions: Lookup/create/delete/open, TID/ifidx access, enqueue/dequeue/reinsert/qlen, attach/detach, address mode configuration, peer deletion, and TDLS peer addition. Uses 512-slot linear-probed hash and priority-to-FIFO table.

Control flow: TX/protocol lookup or create a flowring, queue SKBs until firmware opens it, block netif above high watermark, unblock below low watermark, and delete affected rings on peer/address-mode changes.

State and persistence behavior: Runtime state includes hash table, ring array, per-if address mode, TDLS peer list, block lock, and SKB queues. Firmware flowring state is synchronized through msgbuf delete calls.

Dependencies and integration points: Depends on core flowblock/finalize/interface lookup, bus drvdata, msgbuf deletion, protocol address mode, and SKB queues.

Risks: Many APIs assume valid flow IDs. `brcmf_flowring_create()` returns `-ENOMEM` in a `u32` return type. Locking around ring lifetime and TDLS list is limited. Address mode changes delete only open rings.

Test signals: AP/STA hashing, multicast normalization, TDLS override, ring exhaustion, high/low blocking, delete draining, peer deletion, and detach cleanup.
