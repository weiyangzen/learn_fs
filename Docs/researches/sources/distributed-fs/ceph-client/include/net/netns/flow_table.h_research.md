# sources/distributed-fs/ceph-client/include/net/netns/flow_table.h

Purpose: Defines per-net flowtable statistics storage.

Important APIs/types/functions: `struct nf_flow_table_stat` has counters for workqueue add, delete, and stats operations. `struct netns_ft` points to a per-cpu stat block.

Control flow: Flowtable offload code increments these counters through macros in `nf_flow_table.h`; procfs/stat readers aggregate them.

State and persistence: Runtime per-cpu counters scoped to a network namespace.

Dependencies/integration: Depends on nf flowtable, per-cpu allocation, optional procfs stats, and namespace lifecycle.

Risks/test signals: Test allocation failure paths, stat increments under concurrency, procfs output, and cleanup on netns exit.
