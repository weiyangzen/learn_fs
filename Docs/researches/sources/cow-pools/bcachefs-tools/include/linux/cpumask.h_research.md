# File Research: sources/cow-pools/bcachefs-tools/include/linux/cpumask.h

This header maps kernel CPU concepts to bcachefs-tools per-thread percpu slots. The global `bch_percpu_nr_cpus` is treated as the count of available CPU-like slots.

`num_online_cpus()`, `num_possible_cpus()`, `cpu_online()`, and related macros all use that slot count. `raw_smp_processor_id()` returns `0`, while `for_each_cpu*()` and `for_each_possible_cpu()` iterate from `0` to `bch_percpu_nr_cpus`.

The comments tie this directly to `linux/percpu.c` and the `bch_percpu_chunks[]` registry; consumers should understand “CPU” here as a registered thread chunk, not a hardware CPU.
