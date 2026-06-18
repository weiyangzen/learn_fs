# sources/distributed-fs/ceph-client/net/kcm/kcmproc.c

## Purpose
Provides `/proc/net/kcm` and `/proc/net/kcm_stats` views for KCM sockets. It exposes per-mux, per-KCM socket, per-psock, and aggregate parser/transmit statistics for diagnostics.

## Important APIs, types, and functions
Public init/exit functions are `kcm_proc_init` and `kcm_proc_exit`. Per-net proc setup uses `kcm_proc_init_net` and `kcm_proc_exit_net`. Seq-file iteration is implemented by `kcm_seq_start`, `kcm_seq_next`, `kcm_seq_stop`, and `kcm_seq_show`; formatting helpers include `kcm_format_mux_header`, `kcm_format_sock`, `kcm_format_psock`, and `kcm_format_mux`. Aggregate stats are produced by `kcm_stats_seq_show`.

## Control flow
`kcm_proc_init` registers pernet proc setup. Each namespace creates `kcm_stats` via `proc_create_net_single` and `kcm` via `proc_create_net`. `/proc/net/kcm` iterates the namespace mux list under RCU, prints a header, then formats each mux while taking `mux->lock` to walk its KCM sockets and psocks. `/proc/net/kcm_stats` locks the namespace mutex, folds already-aggregated closed mux/psock stats with active mux and psock stats, then prints mux-level, psock-level, and stream-parser counters.

## State and persistence behavior
No owning state beyond proc registrations. It reads live KCM state plus aggregate stats accumulated during mux release. Proc output is transient.

## Dependencies and integration points
Depends on `kcm_net_id`, KCM data structures from `net/kcm.h`, procfs, seq_file, net namespace generic storage, RCU list traversal, KCM aggregation helpers, and stream parser stats.

## Risks and test signals
Risks include lock ordering with active KCM teardown, reading fields not protected by the selected lock, RCU lifetime during mux iteration, and misleading aggregate labels. Test proc creation/removal per netns, reading while attaching/unattaching psocks, reading while sockets close, aggregate stats after mux release, and builds without `CONFIG_PROC_FS`.
