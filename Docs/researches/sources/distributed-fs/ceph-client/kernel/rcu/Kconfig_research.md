# sources/distributed-fs/ceph-client/kernel/rcu/Kconfig

## Purpose
`kernel/rcu/Kconfig` defines build-time configuration for Linux RCU implementations, SRCU variants, task-based RCU flavors, stall diagnostics, tree fanout, callback offloading, priority boosting, lazy callbacks, and expert-only tuning.

## Important APIs, types, and functions
This is declarative Kconfig rather than C API. Core symbols include `TREE_RCU`, `PREEMPT_RCU`, `TINY_RCU`, `TINY_SRCU`, `TREE_SRCU`, `TASKS_RCU`, `TASKS_RUDE_RCU`, `TASKS_TRACE_RCU`, `RCU_STALL_COMMON`, `RCU_NEED_SEGCBLIST`, `RCU_FANOUT`, `RCU_FANOUT_LEAF`, `RCU_BOOST`, `RCU_NOCB_CPU`, `RCU_LAZY`, and `RCU_DOUBLE_CHECK_CB_TIME`.

## Control flow
Symbol defaults select the implementation based on SMP, preemption, and expert options. `PREEMPT_RCU` selects `TREE_RCU`; UP non-preemptible builds default to `TINY_RCU`. SRCU defaults to tiny or tree according to the RCU flavor. Task-based RCU options are normally selected by need/force symbols. Offload, lazy, boosting, and fanout options are gated by `RCU_EXPERT`, `NO_HZ_FULL`, `PREEMPT_RT`, and related architecture capabilities.

## State and persistence behavior
The file controls compiled-in code paths and default boot behavior, not runtime state. Some symbols enable runtime boot/module parameters elsewhere, such as callback offload, lazy callback behavior, stall timeouts, and tree geometry.

## Dependencies and integration points
It feeds `kernel/rcu/Makefile`, RCU headers, tree/tiny/SRCU/task implementations, IRQ work, context tracking, RT mutexes, NOCB kthreads, and testing/torture infrastructure. Selection of `RCU_NEED_SEGCBLIST` determines whether segmented callback list support is compiled.

## Risks and invariants
Bad dependencies can compile incompatible combinations or silently remove required RCU infrastructure. Expert defaults must avoid prompting ordinary `oldconfig` users for obscure settings. `RCU_FANOUT` ranges must preserve tree scalability constraints. Offload and boosting options have latency and scheduling side effects.

## Test signals
Signals include allnoconfig/defconfig/SMP/PREEMPT/PREEMPT_RT/NO_HZ_FULL build matrices, Kconfig dependency checks, booting tiny and tree RCU kernels, RCU torture/scalability tests under selected flavors, and verifying generated objects match the selected symbols.
