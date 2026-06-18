<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/syscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/syscall.c

Purpose: Exercises BPF syscall programs that invoke `bpf_sys_bpf`/`bpf_sys_close` to create BTF, maps, programs, and update map-in-map entries from BPF context.

Important APIs/types/functions: Defines `bpf_attr_array`, `inner_map`, `outer_array_map`, raw BTF construction helpers, `load_prog`, and `update_outer_map`.

Control flow: `load_prog` builds minimal BTF, creates a BTF-typed hash map, updates it, patches a raw instruction with the map fd, then loads an XDP program. `update_outer_map` obtains an outer map fd by id, creates a new inner map, updates then deletes the outer entry, and closes fds.

State and persistence: Persistent state includes created fds returned in `struct args`, the outer map contents during the update, and the attr scratch array.

Dependencies and integration: Depends on syscall program type, `union bpf_attr`, raw BTF layout, map-in-map support, and close semantics.

Risks: Fd lifetime, attr zeroing, BTF type ids, and map-in-map update/delete permissions are the main risks.

Test signals: Tests expect positive return, valid fds, no leaked fds, and successful outer-map update/delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/syscall.c -->
