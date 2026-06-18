# sources/distributed-fs/ceph-client/include/uapi/linux/oom.h

Purpose: Publishes userspace constants for configuring OOM killer scoring through procfs.

Important APIs/types/functions: Defines `OOM_SCORE_ADJ_MIN`, `OOM_SCORE_ADJ_MAX`, legacy `OOM_DISABLE`, `OOM_ADJUST_MIN`, and `OOM_ADJUST_MAX`.

Control flow: Userspace writes values to `/proc/<pid>/oom_score_adj` or legacy `/proc/<pid>/oom_adj`; the kernel uses them during badness scoring when selecting OOM kill victims.

State and persistence behavior: Values are per-process runtime attributes and do not persist across exec/fork except according to kernel task inheritance rules. This header only fixes the numeric ABI range.

Dependencies and integration points: No external header dependencies beyond include guards. Integrates with procfs, init systems, container runtimes, service managers, and memory pressure policy tools.

Risks: `OOM_SCORE_ADJ_MIN` disables OOM killing for a task, so overly broad use can make system-wide OOM unrecoverable. Legacy `oom_adj` has a different range and mapping, creating migration risk for old tools.

Test signals: Write min/max/out-of-range values through procfs, verify inherited values for child processes, check container runtime policy, and trigger controlled memory pressure to confirm scoring changes.
