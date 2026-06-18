<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/proc_net.c -->
## sources/distributed-fs/ceph-client/fs/proc/proc_net.c

Purpose: implements network-namespace-aware proc entries and `/proc/<pid>/net`, including helper APIs used by networking code to create per-net seq and single proc files.

Important APIs and functions: exports `proc_create_net_data`, `proc_create_net_data_write`, `proc_create_net_single`, `proc_create_net_single_write`, `proc_net_inode_operations`, `proc_net_operations`, `bpf_iter_init_seq_net`, `bpf_iter_fini_seq_net`, and `proc_net_init`. Internals include `PDE_NET`, `get_proc_net`, `seq_open_net`, `seq_release_net`, `single_open_net`, `single_release_net`, `get_proc_task_net`, `proc_tgid_net_lookup`, `proc_tgid_net_readdir`, and pernet init/exit handlers.

Control flow: networking subsystems register entries under a net namespace's proc tree with seq or single callbacks. Opening a seq entry resolves the net namespace from the PDE parent, gets a net reference, allocates seq private state of caller-specified size, and stores/tracks the net reference. `/proc/<pid>/net` lookup and readdir resolve the target task's `nsproxy->net_ns` under task lock and then delegate to that namespace's `proc_net` tree. `proc_net_init` creates `/proc/net -> self/net` and registers pernet setup.

State and persistence behavior: each `struct net` owns `proc_net` and `proc_net_stat` PDE anchors. Per-open seq files hold a net reference in `seq_net_private`, with optional namespace tracker under `CONFIG_NET_NS`. Proc net dentries use forced lookup because `setns(CLONE_NEWNET)` can change visible content beneath the same path.

Dependencies and integration points: integrates network namespace lifetime, pernet subsystem registration, proc generic registration, seq_file, BPF iterator net initialization, task namespace lookup, and proc pid dentry/inode behavior.

Risks: net namespace references must be acquired before callbacks and released exactly once. `/proc/<pid>/net` must reflect the target task's current net namespace and not cache stale dentries. Writable helpers allow network subsystems to mutate state via proc; mode/write callback validation matters.

Test signals: create/read per-net proc entries from multiple netns; `setns` while resolving `/proc/self/net`; task exit during `/proc/<pid>/net` lookup; BPF iterator net ref lifecycle; writable proc_net entries with and without write callbacks; pernet cleanup removing `stat` and net anchors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/proc_net.c -->
