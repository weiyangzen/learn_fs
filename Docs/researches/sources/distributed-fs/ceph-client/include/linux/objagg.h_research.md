
# sources/distributed-fs/ceph-client/include/linux/objagg.h

Purpose: declares an object aggregation library that groups raw objects into roots plus deltas, useful when hardware tables can share common state and represent differences compactly.

Important APIs/types/functions: `struct objagg_ops` defines object size, delta feasibility, delta create/destroy, root create/destroy, and root ID handling. `objagg_create()` / `objagg_destroy()` manage an aggregator. `objagg_obj_get()` / `objagg_obj_put()` acquire/release aggregated objects. Accessors return root private data, delta private data, and raw object data. Stats structures report root count, user counts, delta user counts, and root/delta classification. Hint APIs compute and consume optimization hints using algorithms such as simple greedy.

Control flow: a client creates an aggregator with callbacks, submits raw objects, and the library either reuses an existing root/delta relation or creates a new root. Releasing objects drops users and destroys delta/root private data when unused. Hints can be generated from one run and used to improve a later aggregation plan.

State and persistence: aggregation state is in-memory: roots, deltas, user counts, raw object copies, stats, and hints. Hardware state may be programmed by callbacks but is owned by the client.

Dependencies and integration points: depends on client callback semantics and unsigned root IDs. It integrates with networking/offload-style drivers that need compact shared hardware representations.

Risks and test signals: risks include callback-created hardware state leaking on partial failure, invalid delta equivalence, root ID exhaustion, stats lifetime misuse, and poor hints causing unexpected resource growth. Test signals include duplicate object get/put, delta/root destroy ordering, simulated callback failures, hint generation/application comparisons, and hardware table resource-limit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/objagg.h -->
