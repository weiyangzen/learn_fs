# sources/distributed-fs/ceph-client/net/netfilter/xt_CLASSIFY.c

Purpose: `CLASSIFY` target writes `skb->priority` for qdisc classification.

Important APIs/types/functions: `classify_tg()` and `xt_classify_target_info`; target registrations cover IPv4, IPv6, and ARP with output/forward/postrouting-like hooks.

Control flow: runtime copies configured priority to the skb and returns `XT_CONTINUE`. x_tables core enforces family and hook masks.

State and persistence: no module state; priority persists on skb for downstream traffic control. Dependencies include x_tables, ARP/IP hook spaces, and qdisc classifiers. Risks: overwrites earlier priority decisions, hook mask correctness, and ARP hook namespace differences. Test signals: priority assignment, hook validation, IPv4/IPv6/ARP families, and continued traversal.
