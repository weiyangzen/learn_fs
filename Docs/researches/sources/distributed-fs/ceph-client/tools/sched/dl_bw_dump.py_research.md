# sources/distributed-fs/ceph-client/tools/sched/dl_bw_dump.py

Purpose: drgn diagnostic that prints deadline scheduling bandwidth accounting fields from each online CPU runqueue.

Important APIs/functions: `print_dl_bws_info()` reads `prog['runqueues']`, iterates `for_each_possible_cpu(prog)`, obtains each `rq` with `per_cpu()`, skips offline runqueues through `rq.online`, then prints `rq.dl.running_bw`, `this_bw`, `extra_bw`, `max_bw`, and `bw_ratio`.

Control flow: argparse is initialized with a descriptive help string, then the script calls `print_dl_bws_info()`. Per-CPU memory access is guarded by exception handlers for `drgn.FaultError`, `AttributeError`, and generic exceptions.

State and persistence: no persistent state; it reads live kernel memory or a drgn target.

Dependencies and integration: requires drgn, scheduler debug symbols/BTF for `runqueues`, and Linux helper functions. It integrates with SCHED_DEADLINE analysis by reporting the per-runqueue `dl_rq` accounting state.

Risks: imports `os` and common helpers that are unused. Kernel structure changes can rename or remove fields. It iterates possible CPUs and manually skips offline CPUs, so hotplug races can produce transient faults.

Test signals: run on a kernel with SCHED_DEADLINE enabled, compare output before and during deadline workloads, and verify graceful messages on kernels lacking expected `dl_rq` fields.
