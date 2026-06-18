# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt-stats.c

Purpose: Implements RTRS client statistics collection, formatting, reset operations, and per-path stats allocation.

Important APIs/types/functions: Exports `rtrs_clt_update_wc_stats()`, `rtrs_clt_inc_failover_cnt()`, string formatters for CPU migration, reconnects, and RDMA stats, reset helpers for RDMA/CPU migration/reconnect/all stats, `rtrs_clt_update_all_stats()`, and `rtrs_clt_init_stats()`.

Control flow: Work completion stats compare `con->cpu` with `raw_smp_processor_id()`; if completion migrated, the current CPU's `to` counter increments and the original CPU's atomic `from` counter increments. RDMA update adds request user/data lengths to per-CPU READ or WRITE totals and increments `inflight` for min-inflight multipath policy. Formatters aggregate per-CPU counters into sysfs strings. Reset helpers require an enabled boolean, zero selected per-CPU/global stats, and reset `inflight` for reset-all.

State and persistence: `rtrs_clt_stats` owns per-CPU stats, reconnect counters, and an atomic inflight counter. `rtrs_clt_init_stats()` allocates per-CPU memory and initializes `successful_cnt` to `-1` until the first session establishment sets it to zero.

Dependencies and integration: Depends on `rtrs-clt.h` structures, Linux percpu counters, atomics, and sysfs formatting helpers. The sysfs file uses these formatter/reset functions through `STAT_ATTR` declarations in `rtrs-clt-sysfs.c`; client IO paths call update functions.

Risks: Mixed atomic and non-atomic per-CPU fields assume correct CPU-local access and serialization through `get_cpu_ptr()` or `this_cpu_*`. Resetting stats while IO updates are active can yield transient partial values. `inflight` is incremented here but must be decremented elsewhere in the client core; policy accounting tests need both sides. Test signals include CPU migration under IRQ/workqueue affinity changes, concurrent sysfs reads/resets during IO, failover counter increments, reconnect success/failure formatting, and per-CPU allocation failure handling.
