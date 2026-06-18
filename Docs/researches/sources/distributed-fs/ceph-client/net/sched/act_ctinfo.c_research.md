# sources/distributed-fs/ceph-client/net/sched/act_ctinfo.c

Purpose: implements the `ctinfo` TC action, copying selected information from conntrack marks into packet DSCP and/or `skb->mark` for qdisc classification.

Important APIs/functions: `tcf_ctinfo_act()` performs lookup and mutation; `tcf_ctinfo_dscp_set()` writes IPv4/IPv6 DSCP while preserving ECN; `tcf_ctinfo_cpmark_set()` copies masked connmark to skb mark; `tcf_ctinfo_init()` validates masks and installs params; `tcf_ctinfo_dump()` reports config plus counters; `tcf_ctinfo_cleanup()` frees params.

Control flow: init requires `TCA_CTINFO_ACT`, validates that DSCP mask is exactly six contiguous bits and does not overlap the optional state mask, parses zone and copy-mask options, then RCU-swaps params. Runtime pulls IPv4/IPv6 headers, gets attached conntrack or performs tuple lookup in the configured zone, conditionally applies DSCP when no state mask is configured or the state bit is present, optionally copies mark, releases lookup refs, and returns the configured action.

State and persistence: per-action params are RCU-managed. Atomic counters track DSCP set, DSCP errors, and cpmark set. Packet state changes are DS field writes and `skb->mark`; conntrack mark is read only.

Dependencies and integration: depends on conntrack and connmark support, TC action API, IPv4/IPv6 DS field helpers, `skb_try_make_writable()`, and netfilter tuple lookup.

Risks: DSCP writes can fail if the skb cannot be made writable; this increments an error counter but still returns the configured action. Misconfigured masks are rejected, but runtime conntrack absence leaves packets unchanged. IPv6/IPv4 header pull length must be correct before DS field mutation.

Test signals: DSCP restore from mark with and without state mask, cpmark copy, invalid mask validation, IPv4/IPv6 writability failure counters, zone lookups, dump counter accuracy, and replacement cleanup under traffic.
