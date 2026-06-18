# sources/distributed-fs/ceph-client/tools/rcu/rcu-cbs.py

Purpose: drgn script that sums outstanding RCU callbacks across possible CPUs and prints the total callbacks in flight.

Important APIs/functions: `get_rdp0(prog)` attempts to locate `rcu_preempt_data`, falls back to `rcu_sched_data`, then to `rcu_data` in `kernel/rcu/tree.c`, returning the per-CPU symbol address. The main loop uses `for_each_possible_cpu(prog)`, `per_cpu_ptr()`, and `rdp.cblist.len.value_()`.

Control flow: resolve the correct RCU per-CPU data symbol, initialize `sum`, iterate all possible CPUs, fetch the per-CPU RCU data pointer, read callback list length, add it to the sum, then print one summary line.

State and persistence: no persistent state. It reads live or crash-dump kernel memory through drgn.

Dependencies and integration: requires `drgn`, kernel debug/BTF information sufficient to resolve RCU symbols and fields, and helpers from `drgn.helpers.linux`. It integrates with RCU diagnostics by exposing a compact backlog count.

Risks: field and symbol names differ across kernels; the fallback chain handles old RCU flavors but still assumes `cblist.len`. The script shadows built-in names `sum` and `len`. It reports only a total, not per-CPU distribution, so it can hide skew.

Test signals: run under `sudo drgn rcu-cbs.py` on kernels with `rcu_preempt_data`, older kernels with `rcu_sched_data`, and kernels exposing only `rcu_data`; compare totals with optional per-CPU debug prints.
