# File Research: sources/cow-pools/bcachefs-tools/include/linux/percpu.h

This header implements the bcachefs-tools percpu model. Static per-CPU variables are placed in a custom `bch_percpu` linker section. Each thread gets a private chunk, tracked through TLS (`bch_percpu_my_chunk`, `bch_percpu_my_id`) and a global chunk registry.

It declares percpu allocation/free functions and defines `DEFINE_PER_CPU`, `DECLARE_PER_CPU`, `this_cpu_ptr()`, `per_cpu_ptr()`, and raw/this CPU read/write/add/and/or/xchg/cmpxchg helpers. `this_cpu_ptr()` lazily initializes a thread chunk on first access to avoid crashes from threads not explicitly initialized by bcachefs-tools.

Dynamic percpu pointers are represented as small offsets into a dynamic arena; static section addresses are resolved by offset from `__start_bch_percpu`. The header contains detailed comments on the pointer model and notes that dynamic percpu integration is still a staged design.
