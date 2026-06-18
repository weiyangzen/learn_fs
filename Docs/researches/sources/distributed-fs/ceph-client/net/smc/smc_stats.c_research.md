# sources/distributed-fs/ceph-client/net/smc/smc_stats.c

Purpose: Provides per-network-namespace SMC statistics allocation and generic-netlink dump handlers for aggregate SMC transport and fallback counters.

Important APIs/types/functions: `smc_stats_init()` allocates `net->smc.fback_rsn` and per-CPU `struct smc_stats`; `smc_stats_exit()` frees them. `smc_nl_get_stats()` folds per-CPU counters into one temporary `struct smc_stats` and emits nested SMC-D and SMC-R attributes. `smc_nl_get_fback_stats()` dumps server/client fallback reason counters incrementally. Helpers fill RMB counters, payload/RMB size histograms, and per-technology counters.

Control flow: Net namespace init allocates storage. Runtime macros in `smc_stats.h` update per-CPU fields and fallback arrays elsewhere. Netlink GET_STATS emits one multipart record and uses callback position to avoid repeating it. GET_FBACK_STATS walks fallback reason slots, emits server and client records when present, and tracks list position plus half-emitted server/client state in `cb_ctx->pos[]`.

State and persistence behavior: Stats are in-memory per-net state. Most counters are per-CPU and folded during dump without locking. Fallback reasons are protected by `net->smc.mutex_fback_rsn`. State is reset when the namespace exits.

Dependencies and integration points: Integrates with `smc_netlink.h` generic netlink family and UAPI attributes from `linux/smc.h`. It depends on all SMC paths using the macros consistently for handshake success/errors, payload byte counts, RMB sizes, and buffer pressure.

Risks and test signals: Risks include netlink message-size failures, inconsistent per-CPU aggregation if structure layout changes, partial fallback dump cursor bugs, and missing locking on fallback arrays. Test net namespace init failure unwind, stats dump with SMC-D and SMC-R traffic, fallback reason dumping across multipart boundaries, zero-counter dumps, and netlink attribute compatibility.
