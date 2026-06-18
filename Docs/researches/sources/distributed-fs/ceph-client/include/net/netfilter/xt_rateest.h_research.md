# sources/distributed-fs/ceph-client/include/net/netfilter/xt_rateest.h

Purpose: Defines shared state for xtables rate estimator targets/matches.

Important APIs/types/functions: `struct xt_rateest` contains synchronized basic stats, a spinlock, refcount, hlist node, estimator name, `gnet_estimator` parameters, RCU head, and RCU pointer to `net_rate_estimator`. APIs are `xt_rateest_lookup` and `xt_rateest_put`.

Control flow: The target updates `bstats` under the cache-local lock; matches read the estimator pointer positioned away from hot update data. Lookup returns a named estimator with a reference; put releases it.

State and persistence: Runtime per-net estimator objects are refcounted and RCU-freed. No durable persistence.

Dependencies/integration: Depends on generic net stats/estimators, xtables match/target modules, RCU, spinlocks, and net namespace lookup.

Risks/test signals: Test refcount under concurrent rule replacement, RCU estimator updates, name lookup isolation by namespace, stats update/read races, and module unload with active matches.
