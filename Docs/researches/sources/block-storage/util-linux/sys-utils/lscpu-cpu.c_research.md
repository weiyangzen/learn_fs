# File Research: sources/block-storage/util-linux/sys-utils/lscpu-cpu.c

`lscpu-cpu.c` owns allocation, reference counting, and lookup for per-logical-CPU objects.

Key behavior:
- `lscpu_new_cpu()` allocates a `struct lscpu_cpu`, initializes reference count and logical ID, and sets topology fields to `-1`.
- `lscpu_ref_cpu()` and `lscpu_unref_cpu()` manage CPU object lifetime.
- `lscpu_unref_cpu()` releases the associated CPU type and per-CPU frequency/BogoMIPS strings before freeing.
- `lscpu_create_cpus()` creates the context CPU array from a possible-CPU cpuset.
- `lscpu_cpu_set_type()` swaps a CPU’s referenced `struct lscpu_cputype` safely.
- `lscpu_get_cpu()` performs a linear lookup by logical CPU ID.

Important dependencies:
- CPU set macros and allocation sizing from util-linux cpuset support.
- CPU type reference management from `lscpu-cputype.c`.

Risk notes:
- Lookup is linear over possible CPUs; acceptable for this utility but not optimized for very large CPU counts.
- Callers must follow the comment on `lscpu_get_cpu()` and take a reference when retaining the returned pointer.
