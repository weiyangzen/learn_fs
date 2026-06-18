# sources/distributed-fs/ceph-client/samples/damon/prcl.c

Purpose: DAMON virtual-address sample for proactive reclamation of cold regions in a target process.

Important APIs/functions: `target_pid` and `enabled` module parameters; `damon_new_ctx`, `damon_select_ops(DAMON_OPS_VADDR)`, `find_get_pid`, `damon_new_scheme` with `DAMOS_PAGEOUT`, `damon_start`, `damon_call`, and `damon_stop`.

Control flow: enabling creates a VADDR context, attaches one target pid, creates a scheme matching page-sized regions with zero accesses and age at least 50, starts DAMON, and registers a repeated callback that logs WSS by summing accessed regions. Disabling stops and destroys the context.

State and persistence: global context and PID reference while enabled; no persistent storage.

Dependencies and integration: depends on DAMON VADDR support and process PID lifetime. Integrates with kernel logs for WSS reporting.

Risks: target PID may disappear; code obtains a pid reference but does not explicitly `put_pid` outside context destruction assumptions. `DAMOS_PAGEOUT` can reclaim pages from the selected process and affect workload latency.

Test signals: load with `target_pid=<pid> enabled=1`, monitor `dmesg` for WSS and pageout behavior, then write `0` to the enabled parameter and confirm stop logging.
