# sources/distributed-fs/ceph-client/kernel/bpf/queue_stack_maps.c

Purpose: implements BPF queue and stack map types using a fixed-size circular buffer and a shared map implementation with different pop/peek semantics. The source was read as a complete 288-line file.

Important APIs/functions: `queue_stack_map_alloc_check`, `queue_stack_map_alloc`, `queue_stack_map_free`, `queue_stack_map_push_elem`, `queue_map_pop_elem`, `stack_map_pop_elem`, `queue_map_peek_elem`, `stack_map_peek_elem`, unsupported lookup/update/delete/get_next_key stubs, `queue_stack_map_mem_usage`, `queue_map_ops`, and `stack_map_ops`. Important type: `struct bpf_queue_stack`.

Control flow: allocation validates zero key size, nonzero value size, supported flags, and value-size upper bound, then allocates `max_entries + 1` slots so head/tail equality can mean empty. Push validates flags, treats `BPF_EXIST` as overwrite-oldest-on-full, rejects `BPF_NOEXIST`, locks the map, optionally advances tail if replacing on full, copies value at head, and advances head. Queue get reads from tail and optionally advances tail; stack get reads from `head - 1` and optionally moves head back. Empty pop/peek zeroes the output buffer and returns `-ENOENT`.

State and persistence: `head`, `tail`, `size`, and inline `elements[]` persist for map lifetime. All operations mutate in-memory state under `rqspinlock_t`; no external persistence exists.

Dependencies/integration: uses BPF map ops, BTF map ID, map access flags, `bpf_map_area_alloc/free`, resilient spinlocks, and syscall/BPF helper push/pop/peek operations.

Risks and edge cases: full capacity is `max_entries` despite allocating one extra slot. `BPF_EXIST` intentionally overwrites the oldest queue/stack slot when full, while default push returns `-E2BIG`. Lookup/update/delete/get_next_key are unsupported. Lock acquisition can return `-EBUSY` through resilient spinlocks. Large value sizes are capped by `KMALLOC_MAX_SIZE` for user accessibility.

Test signals: queue/stack map selftests for FIFO/LIFO ordering, empty zero-fill, full-map overwrite vs `-E2BIG`, unsupported operations returning errors, map flags validation, BTF metadata, and concurrent producer/consumer stress.
