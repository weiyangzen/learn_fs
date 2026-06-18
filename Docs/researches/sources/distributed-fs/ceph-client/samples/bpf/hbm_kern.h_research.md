# sources/distributed-fs/ceph-client/samples/bpf/hbm_kern.h

Purpose: shared kernel-side helpers, constants, maps, and packet parsing for HBM BPF programs.

Important APIs/types/functions: defines return flags `DROP_PKT`, `ALLOW_PKT`, `CWR`, thresholds for credit and EDT modes, rate conversion macros, maps `queue_state` and `queue_stats`, `struct hbm_pkt_info`, `get_tcp_info`, `hbm_get_pkt_info`, `hbm_init_vqueue`, `hbm_init_edt_vqueue`, and `hbm_update_stats`.

Control flow: helper routines extract TCP socket info and IP ECN state, initialize per-cgroup queues, and update shared stats counters based on congestion/drop/CWR/ECN decisions made by the main programs.

State and persistence: declares BPF maps that persist while programs are loaded. `queue_state` is cgroup-local storage with spin lock; `queue_stats` is an array shared with userspace.

Dependencies and integration: included by `hbm_out_kern.c` and `hbm_edt_kern.c`; depends on BPF helpers, kernel network headers, endian helpers, and `hbm.h` layout.

Risks: packet parsing reads only initial bytes and handles IPv4/IPv6 simplistically. Rate macros use fixed scaling and require userspace to supply matching units. Stats update has many optional counters and uses atomic operations that can be expensive under load.

Test signals: verifier acceptance, HBM stats consistency, TCP ECN marking observations, and tests that flip `loopback`, `no_cn`, and `stats` flags from userspace.
