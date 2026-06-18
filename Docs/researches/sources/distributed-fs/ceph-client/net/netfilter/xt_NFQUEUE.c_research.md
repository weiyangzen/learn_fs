# sources/distributed-fs/ceph-client/net/netfilter/xt_NFQUEUE.c

Purpose: `NFQUEUE` target queues packets to userspace netfilter queues, supporting ranges, hash fanout, bypass, and CPU fanout.

Important APIs/types/functions: `nfqueue_tg()`, `nfqueue_tg_v1()`, `nfqueue_tg_v2()`, `nfqueue_tg_v3()`, `nfqueue_tg_check()`, and `nfqueue_hash()`.

Control flow: check initializes hash seed, rejects zero queue count and queue ranges above 65535, and validates revision flags. Runtime returns queue verdict for configured queue, packet-hash-selected queue, or CPU-selected queue, adding bypass flag when configured.

State and persistence: global hash seed only; queue state is in nf_queue/userspace. Dependencies include x_tables, nf_queue verdict encoding, jhash, SMP CPU id, and ARP/IP aliases. Risks: queue overflow, CPU fanout distribution changes, bypass accepting packets without listeners, and shared check struct assumptions. Test signals: revisions 0-3, range validation, hash fanout, CPU fanout, bypass, ARP/IPv4/IPv6 use, and userspace queue absence.
