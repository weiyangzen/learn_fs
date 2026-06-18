# sources/distributed-fs/ceph-client/samples/damon/wsse.c

Purpose: DAMON virtual-address working set size estimation sample for a single process.

Important APIs/functions: module parameters `target_pid` and callback-backed `enabled`; `damon_new_ctx`, `damon_select_ops(DAMON_OPS_VADDR)`, `damon_new_target`, `find_get_pid`, `damon_start`, `damon_call`, and repeated `damon_for_each_target`/`damon_for_each_region`.

Control flow: enabling creates and starts a DAMON context for the target process, then schedules a repeated callback that sums all regions with `nr_accesses > 0` and logs `wss`. Disabling stops and destroys the context.

State and persistence: runtime-only DAMON context and pid reference. Module parameters persist only while loaded.

Dependencies and integration: depends on DAMON VADDR support and kernel logging.

Risks: no reclamation action is taken, but monitoring overhead and PID-lifetime issues remain. Repeated logging can be noisy.

Test signals: run with a known process pid, compare logged WSS with workload memory behavior, and verify disable stops callbacks.
