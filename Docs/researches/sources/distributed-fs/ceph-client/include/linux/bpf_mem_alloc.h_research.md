# sources/distributed-fs/ceph-client/include/linux/bpf_mem_alloc.h

Purpose: Declares the BPF memory allocator abstraction used for fast fixed-size and variable-size object allocation, including percpu modes and RCU-delayed freeing. It separates BPF map/program allocation patterns from raw slab APIs.

Important APIs/types/functions: `struct bpf_mem_alloc` holds percpu cache groups, optional fixed-size cache, object cgroup, percpu mode flag, destruction work, and destructor context/free callbacks. `bpf_mem_alloc_init()` initializes fixed-size or variable-size allocators; `bpf_mem_alloc_percpu_init()` and `bpf_mem_alloc_percpu_unit_init()` handle percpu allocation. `bpf_mem_alloc_destroy()` drains resources, `bpf_mem_alloc_set_dtor()` installs destructors, `bpf_mem_alloc_check_size()` validates sizes, and the allocation families include `bpf_mem_alloc/free/free_rcu()` plus fixed-cache `bpf_mem_cache_alloc/free/free_rcu/raw_free/alloc_flags()`.

Control flow: A BPF subsystem initializes an allocator, allocates objects during map/program operations, frees immediately or after RCU depending on reader lifetime, and destroys the allocator after all users drain. Destructor callbacks run during delayed object release.

State/persistence: Allocator state persists in the owning map/subsystem. Per-CPU caches improve allocation latency. `work` handles asynchronous destruction/drain. `objcg` ties allocations to memory cgroup accounting.

Dependencies/integration: Depends on compiler annotations, workqueues, percpu allocation internals, object cgroups, RCU lifetime expectations, and BPF map/local-storage users.

Risks/test signals: Risks include freeing objects before RCU readers finish, excessive percpu memory use, destructor context leaks, size-class validation mistakes, and memcg charging imbalance. Test signals include BPF allocator selftests, stress tests with concurrent map updates/deletes, RCU stall/leak checks, memcg accounting tests, fault injection on allocation, and allocator destroy under load.
