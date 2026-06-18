# sources/distributed-fs/ceph-client/kernel/bpf/map_in_map.h

Purpose: declares the map-in-map metadata and FD pointer helper API used by outer map implementations. The source was read as a complete 19-line file.

Important APIs/types: forward declares `struct file` and `struct bpf_map`; declares `bpf_map_meta_alloc`, `bpf_map_meta_free`, `bpf_map_fd_get_ptr`, `bpf_map_fd_put_ptr`, and `bpf_map_fd_sys_lookup_elem`.

Control flow: no runtime flow is defined here. The header gives outer map code a common contract for creating metadata, resolving an inner-map FD to a refcounted pointer, dropping stored pointers, and returning an inner map ID for syscall lookup.

State and persistence: the header owns no storage. It describes helpers that operate on outer-map metadata and inner-map references.

Dependencies/integration: includes `<linux/types.h>` and is included by `map_in_map.c` and map types that support inner map storage. It is part of the BPF map implementation boundary rather than a UAPI header.

Risks and edge cases: callers must pass the correct outer map and honor the `need_defer` lifetime semantics on put. Prototype drift from implementation would break multiple map types at compile time.

Test signals: compile coverage of array-of-maps/hash-of-maps and map-in-map selftests that exercise all helper paths.
