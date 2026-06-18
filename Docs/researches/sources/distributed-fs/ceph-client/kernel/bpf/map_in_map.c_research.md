# sources/distributed-fs/ceph-client/kernel/bpf/map_in_map.c

Purpose: provides shared helpers for map-in-map outer maps, including cloning inner-map metadata at outer-map creation, validating later inner-map file descriptors against that metadata, and managing references when inner maps are stored or removed. The source was read as a complete 134-line file.

Important APIs/functions: `bpf_map_meta_alloc`, `bpf_map_meta_free`, `bpf_map_meta_equal`, `bpf_map_fd_get_ptr`, `bpf_map_fd_put_ptr`, and `bpf_map_fd_sys_lookup_elem`. It uses `struct bpf_map`, BTF records, BTF refs, array map metadata extensions, and map refcount/free-defer fields.

Control flow: `bpf_map_meta_alloc` resolves the supplied inner map FD, rejects nested map-in-map, requires the inner map to provide `map_meta_equal`, allocates either a base `struct bpf_map` clone or `struct bpf_array`-sized clone for array/percpu-array verifier needs, copies ABI-relevant attributes, duplicates the BTF record, and refs the same BTF object. `bpf_map_fd_get_ptr` resolves an inserted FD, checks it against the outer map's stored metadata, and increments the inner map reference only on match. `bpf_map_fd_put_ptr` optionally marks inner-map free deferral according to sleepable users, then drops the map ref.

State and persistence: outer maps persist a metadata-only clone in `inner_map_meta`; stored inner maps carry normal BPF map references. Metadata includes BTF record and optional array fields but no live contents. Free deferral flags persist on inner maps until normal map release observes them.

Dependencies/integration: includes `map_in_map.h`, uses `__bpf_map_get`, `bpf_map_inc`, `bpf_map_put`, `btf_record_dup/equal`, `btf_get/put`, `array_map_ops`, and `percpu_array_map_ops`. It is called by array-of-maps/hash-of-maps implementations and syscall FD lookup paths.

Risks and edge cases: BTF record duplication must keep the same BTF object because internal record fields point into BTF-owned data. Equality ignores `max_entries` in this file, relying on type-specific comparisons where needed; map type covers ops equality. Nested maps are rejected. Sleepable reference accounting affects whether one or multiple RCU grace periods are required before freeing removed inner maps.

Test signals: map-in-map selftests for valid/invalid inner FD insertion, metadata mismatches, BTF-enabled value records, array/percpu-array inner maps, nested-map rejection, reference leak checks, and sleepable-program map lifetime tests.
