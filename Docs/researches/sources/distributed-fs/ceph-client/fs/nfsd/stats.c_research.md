# sources/distributed-fs/ceph-client/fs/nfsd/stats.c

Purpose: `stats.c` exposes NFSD runtime statistics through `/proc/net/rpc/nfsd` using seq_file/proc helpers. It reports duplicate reply cache, filehandle, I/O, thread, generic RPC, and optional NFSv4 operation counters. The source was read as a complete 86-line file.

Important APIs/types/functions: main show function is `nfsd_show`. `DEFINE_PROC_SHOW_ATTRIBUTE(nfsd)` creates proc operations. Exported setup/teardown APIs are `nfsd_proc_stat_init` and `nfsd_proc_stat_shutdown`.

Control flow: `nfsd_proc_stat_init` registers the proc stats file for a net namespace using `svc_proc_register`; opening/reading the file invokes `nfsd_show`. The show function obtains the net namespace from proc inode data, retrieves `struct nfsd_net`, sums per-cpu counters, prints legacy-compatible lines, calls `svc_seq_show` for generic RPC stats, and conditionally appends NFSv4 operation and write-delegation getattr counters. Shutdown unregisters the proc entry by name.

State and persistence: no persistent state is stored here. The file reads live per-net `percpu_counter` arrays and the global `nfsd_th_cnt` atomic. Deprecated fields are printed as zeros to preserve proc output shape for existing tools.

Dependencies and integration points: seq_file, procfs, SunRPC stats, net namespaces, `nfsd.h`, and UAPI counter indexes via `stats.h`. `nfsctl.c` calls initialization/shutdown during per-net lifecycle, and many NFSD paths increment counters exposed here.

Risks: proc output is user-visible and compatibility-sensitive. Counter sums are snapshots and may not be perfectly atomic across all fields. Adding or reordering fields can break parsers. NFSv4 operation output depends on `LAST_NFS4_OP` and counter index layout staying aligned.

Test signals: proc registration per net namespace, output format comparison with legacy expectations, counter increments for reply cache hits/misses/nocache, stale filehandles, I/O bytes, thread count changes, NFSv4 operation counters, and clean unregister during namespace teardown.
