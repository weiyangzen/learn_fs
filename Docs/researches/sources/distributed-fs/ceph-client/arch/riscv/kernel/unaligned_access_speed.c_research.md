<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/unaligned_access_speed.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/unaligned_access_speed.c

Purpose: Measures and records scalar and vector unaligned access performance so the kernel and hwprobe can distinguish fast, slow, emulated, unsupported, and unknown behavior.

Important APIs/types/functions: Defines per-CPU `misaligned_access_speed` and `vector_misaligned_access`, boot parameters `unaligned_scalar_speed=` and `unaligned_vector_speed=`, static key `fast_unaligned_access_speed_key`, measurement helpers, CPU hotplug callbacks, and late init `check_unaligned_access_all_cpus()`.

Control flow: Boot or parameter handling sets fixed classifications or schedules per-CPU measurement. Scalar measurement compares aligned versus unaligned copy cycle counts and updates static branches. Vector measurement schedules work per CPU when vector support exists. Hotplug callbacks classify late CPUs and maintain the fast-access static key.

State and persistence: Per-CPU classification variables, `fast_misaligned_access` cpumask, static branch state, and boot-parameter overrides persist after probing.

Dependencies and integration points: Feeds `sys_hwprobe.c`, interacts with `traps_misaligned.c`, vector assembly copy helpers, CPU hotplug, alternatives/static keys, and boot command line.

Risks: Microbenchmarks can be noisy and affect ABI-reported performance. Static key changes must account for heterogeneous CPUs. Vector probing must avoid unsupported traps on CPUs without V.

Test signals: Boot with/without override parameters, heterogeneous CPU hotplug, hwprobe misaligned keys, static-key state inspection, and workloads using optimized unaligned copy branches.

Source read size: 446 lines, 12999 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/unaligned_access_speed.c -->
