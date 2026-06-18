# sources/distributed-fs/ceph-client/fs/nfsd/stats.h

Purpose: `stats.h` declares NFSD stats proc setup/teardown and provides inline helpers for updating per-net and per-export counters. The source was read as a complete 76-line file.

Important APIs/types/functions: declarations are `nfsd_proc_stat_init` and `nfsd_proc_stat_shutdown`. Inline counter helpers are `nfsd_stats_rc_hits_inc`, `nfsd_stats_rc_misses_inc`, `nfsd_stats_rc_nocache_inc`, `nfsd_stats_fh_stale_inc`, `nfsd_stats_io_read_add`, `nfsd_stats_io_write_add`, `nfsd_stats_payload_misses_inc`, `nfsd_stats_drc_mem_usage_add`, `nfsd_stats_drc_mem_usage_sub`, and, for NFSv4, `nfsd_stats_wdeleg_getattr_inc`.

Control flow: callers pass `struct nfsd_net` and, when available, `struct svc_export`. The helpers increment or add/subtract `percpu_counter` values indexed by UAPI `NFSD_STATS_*` constants. Export-aware helpers update both the namespace counter and the export's `ex_stats` counter when present.

State and persistence: state is live in per-net and per-export counter arrays. There is no persistence. The helpers are intentionally low-overhead and avoid locking around each increment by relying on percpu counters.

Dependencies and integration points: depends on `uapi/linux/nfsd/stats.h` for stable counter indexes and `linux/percpu_counter.h`. It is pulled through `nfsd.h` and used by reply cache, filehandle verification, I/O paths, duplicate reply cache memory accounting, and NFSv4 delegation getattr paths.

Risks: counter index drift between UAPI and `nfsd_net` allocation would corrupt reporting. Export stats are optional, so helpers must keep null checks. Per-cpu counters are approximate until summed, which is appropriate for stats but not for enforcement. Negative DRC memory accounting must remain balanced.

Test signals: compile tests should verify all helpers see complete `struct nfsd_net` and export stats declarations. Runtime tests should assert namespace and export counters both move for stale filehandles and I/O, DRC memory add/sub pairs balance, and `/proc/net/rpc/nfsd` displays updated values.
