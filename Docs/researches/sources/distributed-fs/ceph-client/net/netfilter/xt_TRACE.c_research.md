# sources/distributed-fs/ceph-client/net/netfilter/xt_TRACE.c

Purpose: `TRACE` target marks packets for netfilter tracing.

Important APIs/types/functions: `trace_tg()`, `trace_tg_check()`, `trace_tg_destroy()`, and nf_logger reference helpers.

Control flow: check obtains the family logger; runtime sets `skb->nf_trace = 1` and continues; destroy releases logger. Targets are raw-table IPv4/IPv6 entries.

State and persistence: trace bit persists on skb; logger reference persists for rule lifetime. Dependencies include x_tables, nf_log/syslog soft dependency, raw table, and netfilter trace consumers. Risks: missing logger rejects rule, high trace volume, and downstream hooks observe trace bit globally for that packet. Test signals: logger availability, raw hook enforcement, trace flag set, IPv4/IPv6 registration, destroy put, and continuation.
