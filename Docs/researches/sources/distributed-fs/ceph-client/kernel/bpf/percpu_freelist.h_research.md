# sources/distributed-fs/ceph-client/kernel/bpf/percpu_freelist.h

Purpose: declares the per-CPU freelist structures and API used by BPF preallocated maps. The source was read as a complete 33-line file.

Important APIs/types: `struct pcpu_freelist_head`, `struct pcpu_freelist`, `struct pcpu_freelist_node`, `pcpu_freelist_push`, `pcpu_freelist_pop`, `__pcpu_freelist_push`, `__pcpu_freelist_pop`, `pcpu_freelist_populate`, `pcpu_freelist_init`, and `pcpu_freelist_destroy`.

Control flow: no executable flow is defined here. The comments specify that public functions perform spin_lock_irqsave-style IRQ handling while the double-underscore variants only spin-lock and require callers to have disabled IRQs.

State and persistence: the header defines the per-CPU head pointer and embedded node format but owns no storage.

Dependencies/integration: includes spinlock, percpu, and `rqspinlock` declarations. It is a private kernel BPF header consumed by the implementation and map code.

Risks and edge cases: misuse of the underscore variants without IRQ exclusion can race with public paths. Element structs must embed `pcpu_freelist_node` in compatible storage.

Test signals: compile coverage of map users and runtime freelist push/pop tests through preallocated map operations.
