## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nf_queue.c

Purpose: user-space nfnetlink_queue consumer for nft queue tests. It binds a queue, receives packets, optionally prints/counts per-hook packet stats, and sends accept or queue-forwarding verdicts, including stress modes for out-of-order and bogus verdicts.

Important APIs and types: uses libmnl with NETLINK_NETFILTER, `NFNL_SUBSYS_QUEUE`, `NFQNL_MSG_CONFIG`, `NFQNL_MSG_VERDICT`, `NFQA_CFG_CMD`, `NFQA_CFG_PARAMS`, `NFQA_CFG_FLAGS`, `NFQA_VERDICT_HDR`, `NFQA_PACKET_HDR`, `NFQA_SKB_INFO`, and verdict constants `NF_ACCEPT`/`NF_QUEUE`.

Control flow: `parse_opts()` sets count, verbosity, queue number, timeout, fail-open, GSO flag, verdict destination queue, delay, out-of-order mode, and bogus verdict mode. `open_queue()` binds netlink, binds the nfqueue, configures copy-packet mode, flags, and receive timeout. `mainloop()` receives netlink batches, parses attributes in `queue_cb()`, computes packet id from callback return, optionally delays, sends bogus verdicts for nonexistent ids, batches 16 ids for reverse-order verdicts, or immediately sends a verdict for the packet id. On timeout it exits cleanly; with `-c` it prints hook counters.

State and persistence: process-local options and `queue_stats`; queue binding exists while process runs. Dependencies include nfnetlink_queue kernel support and libmnl. Risks include callback return encoding `MNL_CB_OK + id`, fixed hook count array of 5, and leaving queued packets to bypass/fail-open depending on nft rule if process exits. Test signals are exit status, optional stats, and kernel queue behavior observed by scripts.
