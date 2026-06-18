# sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache-mem-types.h

Purpose: defines memory accounting IDs for the `nl-cache` translator.

Important APIs, types, and functions: `enum gf_nlc_mem_types_` begins at `gf_common_mt_end + 1` and assigns IDs for `nlc_conf`, `nlc_ctx`, `nlc_local`, positive entries, negative entries, timer data, LRU nodes, and `gf_nlc_mt_end`.

Control flow: no runtime control flow; IDs are consumed by `GF_CALLOC`, `GF_MALLOC`, and `xlator_mem_acct_init(this, gf_nlc_mt_end)`.

State and persistence: contributes accounting categories only. Runtime allocation state is managed by Gluster's memory accounting subsystem.

Dependencies and integration: includes `<glusterfs/mem-types.h>` and is included by `nl-cache.h` and implementation files.

Risks and test signals: IDs must remain unique and ordered after `gf_common_mt_end`; adding new allocations requires appending before `gf_nlc_mt_end`. Test signal is successful memory-account initialization and useful statedump/accounting labels under nl-cache workloads.
