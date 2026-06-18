# sources/distributed-fs/ceph-client/kernel/irq/matrix.c

## Purpose
`matrix.c` implements a per-CPU bitmap allocator for interrupt vectors or similar finite IRQ resources. It tracks system-reserved bits, regular allocations, managed interrupt reservations, online CPU availability, and global reservation accounting.

## Important APIs, types, and functions
The main types are internal `struct irq_matrix` and per-CPU `struct cpumap`. Public functions include `irq_alloc_matrix()`, `irq_matrix_online()`, `irq_matrix_offline()`, `irq_matrix_assign_system()`, `irq_matrix_reserve_managed()`, `irq_matrix_remove_managed()`, `irq_matrix_alloc_managed()`, `irq_matrix_assign()`, `irq_matrix_reserve()`, `irq_matrix_remove_reserved()`, `irq_matrix_alloc()`, `irq_matrix_free()`, `irq_matrix_available()`, `irq_matrix_reserved()`, `irq_matrix_allocated()`, and debugfs-only `irq_matrix_debug_show()`.

## Control flow
Initialization allocates a matrix plus per-CPU maps, with each CPU map carrying allocation and managed bitmaps. CPU online initializes its available count from alloc range minus managed and system bits, then contributes to global availability; offline subtracts it. Allocation picks a best online CPU, finds zero areas after combining system, managed, and allocated maps, marks the selected map, and updates global/per-CPU counters. Managed reservations allocate one managed bit per target CPU and roll back on failure; managed allocation selects the CPU with the lowest managed allocation count.

## State and persistence
State is purely in-memory allocator state: global counters, per-CPU `available`, `allocated`, `managed`, `managed_allocated`, `online` flags, `system_map`, `managed_map`, and `alloc_map`. CPU hotplug changes accounting but does not persist across boot.

## Dependencies and integration points
It depends on bitmap helpers, percpu allocation, CPU masks/hotplug assumptions, tracepoints from `trace/events/irq_matrix.h`, and optional seq_file debug output. Architectures such as x86 vector allocation use this as a resource allocator under genirq affinity and managed IRQ paths.

## Risks and test signals
Risks include counter skew between online/offline paths, managed bits being freed while allocated, allocation from empty masks, global reservation underflow, system-bit replacement misuse, and lockless debug snapshots observing transient state. Test signals include CPU hotplug with active vectors, allocation exhaustion, managed reservation rollback, managed allocation balancing, freeing managed and non-managed bits, system vector replacement, reservation warnings, and debugfs consistency checks.
