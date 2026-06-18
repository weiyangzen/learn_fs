<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_ma.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_ma.c

Purpose: Stress tests BPF memory allocator object and percpu object allocation/free through kptr map values.

Important APIs/types/functions: Defines generated maps for many object sizes, BTF id arrays, batch alloc/free helpers, and fentry tests for batch allocation, free-through-map-free, percpu allocation, and percpu map free.

Control flow: Handlers gated by pid allocate batches with `bpf_obj_new_impl` or `bpf_percpu_obj_new_impl`, exchange into map kptr fields, then free or rely on map cleanup.

State and persistence: Persistent state is many array maps holding kptr/percpu-kptr values plus `err`/`pid` globals.

Dependencies and integration: Depends on experimental allocator helpers, kptr map fields, BTF ids supplied by userspace, and fentry attach.

Risks: Refilling/freeing allocator caches, zero-sized layouts, and map cleanup ownership are risks.

Test signals: Tests set BTF ids/pid, trigger nanosleep, and expect `err==0` after allocation/free cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_ma.c -->
