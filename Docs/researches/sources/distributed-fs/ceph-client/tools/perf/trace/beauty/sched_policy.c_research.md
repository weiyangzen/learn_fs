# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sched_policy.c

Purpose: Formats scheduler policy values and policy flags for scheduling syscalls.

Important APIs/types/functions: `syscall_arg__scnprintf_sched_policy` recognizes base policies `SCHED_NORMAL`, `FIFO`, `RR`, `BATCH`, `ISO`, `IDLE`, and `DEADLINE`, plus `SCHED_RESET_ON_FORK`.

Control flow: The function splits the low policy byte from high flag bits using `SCHED_POLICY_MASK`, prints the base policy or raw hex, then appends recognized flags and remaining unknown bits.

State and persistence: Stateless formatting.

Dependencies and integration points: Uses `<sched.h>` plus fallback definitions for newer constants. Bound through `SCA_SCHED_POLICY`.

Risks: `SCHED_ISO` may not exist on all systems but is represented positionally in the local array. Future high-bit flags require updates for symbolic output.

Test signals: Format common policies, `SCHED_RESET_ON_FORK` combinations, and unknown values.
