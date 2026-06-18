# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/lpar.c

## Purpose
Provides pSeries LPAR hypervisor integration for hcalls, dispatch trace logs, VPA registration, hash/radix MMU setup, HPT operations, HPT resizing, CMO page hints, hcall tracing, memory entitlement helpers, and debug/proc visibility.

## Important APIs, Types, And Functions
Externally visible functions include exported hcall wrappers, `alloc_dtl_buffers`, `register_dtl_buffer`, `vpa_init`, `pseries_paravirt_steal_clock`, `hpte_init_pseries`, `radix_init_pseries`, `arch_free_page`, `h_get_mpp`, and `h_get_mpp_x`. Hash MMU ops include `pSeries_lpar_hpte_insert`, `pSeries_lpar_hpte_remove`, `pSeries_lpar_hpte_updatepp`, `pSeries_lpar_hpte_invalidate`, `pSeries_lpar_flush_hash_range`, `pseries_hpte_clear_all`, and hugepage invalidation helpers. Dispatch statistics use `struct dtl_worker`, `struct vcpu_dispatch_data`, `dtl_access_lock`, per-CPU DTL indices, and proc handlers for `powerpc/vcpudispatch_stats`.

## Control Flow
During CPU setup, `vpa_init` registers the lppaca as VPA, optionally registers SLB shadow for SPLPAR hash-MMU guests, and registers any allocated DTL buffer. DTL accounting allocates per-CPU buffers, registers them with the hypervisor, and optionally starts delayed workers that parse DTL records to update vCPU dispatch locality statistics. Hash MMU init installs pSeries `mmu_hash_ops`; HPTE insert/update/remove paths translate Linux page attributes into PAPR hcalls. Flush paths choose H_BLOCK_REMOVE, H_BULK_REMOVE, or per-entry invalidation based on firmware features and block-size characteristics. HPT resize prepares with the hypervisor, commits under stop-machine, then updates local hash-table globals.

## State And Persistence
State is mostly per-CPU and MMU-global: paca DTL pointers, lppaca DTL/VPA fields, dispatch-stat counters, VPHN associativity caches, `hblkrm_size`, hash table globals, CMO hint boot parameter state, and hcall trace recursion depth. Debugfs can expose raw VPA data. No durable storage is used.

## Dependencies And Integration Points
Depends on PAPR hcalls, paca/lppaca layout, SPLPAR firmware features, VPHN topology hcalls, CPU hotplug, procfs/debugfs, generic hash and radix MMU code, stop_machine, fadump/kexec paths, CMO firmware support, and tracepoints. `lparcfg.c` consumes `h_get_mpp` and `h_get_mpp_x`.

## Risks And Edge Cases
Hash table hcalls are low-level and often `BUG_ON` unexpected hypervisor results. TLB invalidation batching must preserve AVPN/slot ordering and obey block alignment. DTL workers must stay pinned to the intended CPU and coordinate with hotplug. HPT resize has timeout and stop-machine failure modes. CMO free-page hints are disabled for radix and gated by firmware/boot parameter. Hcall tracepoints guard against recursion but cannot catch every tracing-induced hcall.

## Test Signals
Boot SPLPAR with hash and radix MMU, enable/disable `vcpudispatch_stats`, vary `vcpudispatch_stats_freq`, hotplug CPUs, run THP and hugetlb workloads, kexec with hash MMU, exercise `bulk_remove=off`, test HPT resize under load, verify paravirt steal time, inspect VPA debugfs, and check `lparcfg` memory entitlement output.
