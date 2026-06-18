# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netpoll_basic.py

Purpose: Attempts to trigger and observe the netpoll TX-side polling path (`netpoll_poll_dev`) by congesting a NIC while sending netconsole messages.

Important APIs/functions: Uses `NetDrvEpEnv`, `GenerateTraffic`, ethtool queue/ring helpers, configfs netconsole target helpers, and `bpftrace` kprobe collection. Key functions are `configure_network`, `netcons_configure_target`, `do_netpoll_flush`, `do_netpoll_flush_monitored`, `bpftrace_any_hit`, and `test_netpoll`.

Control flow: Main loads netconsole, checks configfs, enters a local/remote endpoint environment, reduces queues/rings where possible, starts background traffic, creates a netconsole target, repeatedly writes batches to `/dev/kmsg` while recreating the target, and checks whether bpftrace saw `netpoll_poll_dev`.

State and persistence: Mutates ethtool channel/ring settings, configfs netconsole target directories, `/dev/kmsg`, global `MAPS`/`BPF_THREAD`, and traffic generator state. Deferred cleanup restores rings/queues and removes the target.

Dependencies and integration: Requires dynamic netconsole configfs, bpftrace/kprobe support, ethtool JSON support, root, and a driver/environment capable of hitting the rare netpoll path.

Risks: The expected path is environment-dependent; lack of hits becomes `XFAIL`, not necessarily a kernel failure. Ring/queue reduction may be unsupported on real NICs, and repeated configfs target recreation can leave stale targets if interrupted before deferred cleanup.

Test signals: Success is at least one bpftrace hit for `netpoll_poll_dev`; skip covers missing configfs/bpftrace setup, and xfail covers environments that do not trigger the path.
