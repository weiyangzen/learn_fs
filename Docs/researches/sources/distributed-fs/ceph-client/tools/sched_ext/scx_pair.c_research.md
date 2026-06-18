# sources/distributed-fs/ceph-client/tools/sched_ext/scx_pair.c

Purpose: user-space loader for the CPU-pair core-scheduling demo.

Important APIs/functions: parses `-S` stride, `-v`, and `-h`; uses `RESIZE_ARRAY()` for `pair_cpu`, `pair_id`, and `in_pair_idx`; creates inner queue maps for `cgrp_q_arr`; uses `SCX_OPS_OPEN/LOAD/ATTACH` and UEI reporting.

Control flow: open skeleton, set possible CPU count and batch duration, parse stride, reject non-positive stride and odd CPU counts, resize pair arrays, compute pair relationships by stride, load skeleton, populate the array-of-maps with `MAX_CGRPS` BPF queue maps, attach, print counters periodically, then detach/report/destroy and restart on restart exit code.

State and persistence: no external persistence. Runtime state includes generated pairing arrays and inner BPF queue map fds installed into the outer map.

Dependencies and integration: generated skeleton, libbpf map creation/update APIs, common sched_ext headers, and `scx_pair.h`.

Risks: invalid stride can create self-pairs or three-CPU conflicts and is guarded by `SCX_BUG_ON()`. Initializing many cgroup queues is potentially slow and can be interrupted by `exit_req`. The loader requires even possible CPU count.

Test signals: default pairing, custom stride pair layout, invalid stride errors, array-of-maps population success, stats output under cgroup workloads, and signal cleanup.
