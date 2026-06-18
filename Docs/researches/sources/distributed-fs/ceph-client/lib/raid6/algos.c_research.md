# sources/distributed-fs/ceph-client/lib/raid6/algos.c

Purpose: owns RAID6 syndrome and recovery algorithm selection.

Important APIs and flow: exports global `raid6_call`, `raid6_2data_recov`, and `raid6_datap_recov`. `raid6_algos[]` lists generation implementations by architecture and fallback integer routines. `raid6_recov_algos[]` lists recovery implementations. `raid6_choose_gen()` selects the first valid highest-priority algorithm unless `CONFIG_RAID6_PQ_BENCHMARK` measures throughput, then stores `raid6_call`. `raid6_choose_recov()` picks the highest-priority valid recovery implementation and installs global function pointers. `raid6_select_algo()` allocates pages, seeds test data from `raid6_gfmul`, runs both selectors, frees pages, and is called at `subsys_initcall`.

State and persistence: runtime global dispatch state lives in `raid6_call` and recovery function pointers. No filesystem persistence.

Dependencies and integration: depends on `linux/raid/pq.h`, generated GF tables, jiffies/preemption for benchmarking, and architecture validity callbacks.

Risks and test signals: global selection affects all RAID6 users. Risks include priority mistakes, invalid CPU feature checks, and disabled benchmarking selecting a suboptimal first candidate. Signals include boot logs for selected gen/recovery algorithms, RAID6 recovery tests, and architecture feature matrix boots.
