# sources/distributed-fs/ceph-client/net/netfilter/xt_RATEEST.c

Purpose: `RATEEST` target maintains named packet/byte rate estimators for use by other xtables components.

Important APIs/types/functions: `struct xt_rateest_net`, `xt_rateest_lookup()`, `xt_rateest_put()`, `xt_rateest_tg_checkentry()`, `xt_rateest_tg()`, and pernet operations.

Control flow: check validates name, seeds hash, reuses an existing estimator with matching parameters or allocates a new one, initializes stats/lock/refcount, starts `gen_new_estimator()`, inserts into per-net hash, and stores hidden pointer. Runtime increments byte and packet counters under spinlock. Destroy puts estimator, killing and RCU-freeing final refs.

State and persistence: per-net hash of named estimators, stats, estimator timers, refcounts. Dependencies include gen_stats, pernet storage, mutex/hash, spinlocks, RCU, and x_tables usersize hiding. Risks: parameter mismatch, RCU timer lifetime, refcounting, name termination, and namespace isolation. Test signals: reuse/mismatch, counter increments, lookup/put exports, final free, IPv4/IPv6 registration, and per-net separation.
