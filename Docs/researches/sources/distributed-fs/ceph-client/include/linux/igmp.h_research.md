# `sources/distributed-fs/ceph-client/include/linux/igmp.h`

Purpose: internal IPv4 IGMP/multicast membership structures and APIs for socket membership lists, device multicast records, source filters, report/query parsing, and IGMP lifecycle operations.

Important APIs/types/functions: `igmp_hdr`, `igmpv3_report_hdr`, `igmpv3_query_hdr`, `struct ip_sf_socklist`, `struct ip_mc_socklist`, `struct ip_sf_list`, `struct ip_mc_list`, IGMPv3 exponential decode macros, `ip_mc_may_pull`, multicast join/leave/source/filter APIs, device init/up/down/remap APIs, group refcount helpers, and `ip_mc_check_igmp`.

Control flow and state: socket multicast lists are RCU-linked; per-interface multicast records hold source lists, timers, user/ref counts, spinlock, reporter state, retransmission counts, timestamps, and RCU teardown. `ip_mc_may_pull` validates transport length before pulling data into linear SKB memory.

Dependencies/integration: depends on SKB, timers, IP, socket pointer abstraction, refcounting, and UAPI IGMP. Integrated with IPv4 multicast routing, socket options, and netdevice address lifecycle.

Risks: RCU lifetime of socket/source lists, timer teardown during device/socket close, source-filter include/exclude accounting, short packet parsing, and exponential max-response decoding edge cases.

Test signals: IGMPv2/v3 receive, join/leave/SSM, source filter add/drop/query, device up/down/unmap/remap, short/truncated query/report packets, timer cancellation, and RCU/refcount stress.
