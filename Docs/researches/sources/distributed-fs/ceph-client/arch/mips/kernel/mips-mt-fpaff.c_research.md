<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-mt-fpaff.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/mips-mt-fpaff.c

### Purpose
`mips-mt-fpaff.c` adds MIPS MT FPU affinity policy by wrapping scheduler affinity syscalls. It keeps FP-heavy tasks on VPEs/TCs that have an FPU while preserving the user's requested CPU mask.

### Important APIs, Types, And Functions
Public state includes `mt_fpu_cpumask` and `mt_fpemul_threshold`. Public syscall wrappers are `mipsmt_sys_sched_setaffinity()` and `mipsmt_sys_sched_getaffinity()`. Helpers include `find_process_by_pid()`, `check_same_owner()`, `fpaff_thresh()`, and `mt_fp_affinity_init()`.

### Control Flow
`sched_setaffinity` copies the user mask, finds and pins the target task under CPU and RCU locks, checks ownership/capability and LSM scheduler permission, records the user mask in `p->thread.user_cpus_allowed`, then intersects it with `mt_fpu_cpumask` when the task has `TIF_FPUBOUND`. If a concurrent cpuset update changes allowed CPUs, it retries with the cpuset mask. `sched_getaffinity` reports the union of saved user mask and current effective mask, restricted to active CPUs. Boot parameter `fpaff=` overrides the emulation threshold; otherwise init derives it from `loops_per_jiffy`.

### State, Persistence, And Dependencies
State is task `thread.user_cpus_allowed`, `TIF_FPUBOUND`, global FPU-capable CPU mask, and the emulation threshold. Dependencies include scheduler affinity APIs, cpusets, credentials, security hooks, uaccess, and MIPS MT FP emulation accounting.

### Integration Points
The wrappers replace normal affinity syscalls on MIPS MT systems so FPU emulation can trigger binding to FPU-capable CPUs without hiding the user's original affinity request.

### Risks
The source comments note this code mirrors scheduler core logic and must stay in sync with upstream permission and cpuset behavior. The local `cpumask_var_t new_mask` declaration shadows the earlier stack variable pattern and must be handled carefully by compilers/configs. Races with cpuset updates are explicitly retried.

### Test Signals
Test affinity set/get for current and remote tasks, permission failures, cpuset changes during affinity updates, FP-bound tasks intersecting `mt_fpu_cpumask`, and `fpaff=` threshold override.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-mt-fpaff.c -->
