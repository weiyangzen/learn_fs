# sources/distributed-fs/ceph-client/kernel/bpf/arraymap.c

Purpose: implements BPF array-family map types: plain arrays, per-CPU arrays, program arrays for tail calls, perf event arrays, cgroup fd arrays, and array-of-maps.

Important APIs/types/functions: allocation and common ops include `array_map_alloc_check`, `array_map_alloc`, `array_map_lookup_elem`, `array_map_update_elem`, `bpf_percpu_array_copy`, `bpf_percpu_array_update`, `bpf_array_get_next_key`, `array_map_mmap`, iterator seq ops, and `bpf_for_each_array_elem`. FD-backed variants use `bpf_fd_array_map_lookup_elem`, `bpf_fd_array_map_update_elem`, `__fd_array_map_delete_elem`, and type-specific get/put callbacks. Program arrays add `prog_array_map_poke_track`, `prog_array_map_poke_run`, deferred clear work, and `prog_array_map_ops`.

Control flow: creation validates key/value sizes and flags, rounds element size to 8 bytes, optionally expands backing storage for Spectre v1 masking, and either allocates contiguous map memory or per-cpu pointers. Lookup checks bounds and applies `index_mask`. Updates copy values or per-cpu values and free BTF-described fields. mmapable arrays remap vmalloc storage. Iterators pin a map uref and feed entries into BPF iterator programs. FD arrays exchange stored object pointers with `xchg` and release old pointers through map-specific callbacks; program arrays patch JIT tail-call sites under `poke_mutex`.

State and persistence: plain arrays preallocate all slots for map lifetime. Per-cpu arrays persist one allocation per entry per possible CPU. Program/perf/cgroup/array-of-map variants persist referenced kernel objects and release them on delete, map release, or map free. `BPF_F_PRESERVE_ELEMS` changes perf event array release behavior.

Dependencies and integration: uses BPF map core, BTF record cleanup, JIT direct lookup generation, RCU, perf events, cgroups, map-in-map metadata, BPF iterators, SHA-256 hashing for map hash, and architecture poke hooks for tail calls.

Risks: boundary and overflow checks protect preallocated memory. Speculation masking must stay aligned with generated lookup instructions. FD map object lifetime relies on RCU and put callbacks. Program array tail-call patching is subtle because tracked program aux data may be visible before final JIT stability. Per-cpu copy flags must not expose padding or cross invalid CPU IDs.

Test signals: BPF map selftests for array/percpu array, mmapable arrays, batch ops, BTF spin_lock values, map iterators, `bpf_for_each_map_elem`, tail calls and prog-array updates, perf event arrays, cgroup arrays, and array-of-maps should detect regressions.
