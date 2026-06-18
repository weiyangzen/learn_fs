# sources/distributed-fs/ceph-client/kernel/bpf/bpf_cgrp_storage.c

Purpose: provides cgroup-owned BPF local storage maps and helper prototypes.

Important APIs/types/functions: `DEFINE_BPF_STORAGE_CACHE(cgroup_cache)` creates the storage cache. `cgroup_storage_ptr`, `bpf_cgrp_storage_free`, `cgroup_storage_lookup`, fd-based map ops, `bpf_cgrp_storage_get`, and `bpf_cgrp_storage_delete` wrap generic local storage for `struct cgroup`. `cgrp_storage_map_ops` wires the map into BPF core.

Control flow: userspace map lookup/update/delete takes a cgroup fd, obtains a cgroup reference, performs generic local-storage lookup/update/unlink, and drops the cgroup. BPF helpers operate on a `struct cgroup *` under BPF RCU, optionally create storage if the cgroup refcount is not dying, and return a map-value pointer or delete status.

State and persistence: storage attaches to `cgroup->bpf_cgrp_storage` and persists until explicit deletion, map free, or cgroup destruction through `bpf_cgrp_storage_free`.

Dependencies and integration: depends on cgroup fd lookup, generic `bpf_local_storage`, BTF id for cgroup helper argument validation, BPF RCU locking, and map memory accounting from the generic engine.

Risks: helper create must not attach to dying cgroups. fd operations must correctly refcount cgroups. Missing BPF RCU lock is warned. No key iteration is supported.

Test signals: cgroup local storage selftests should cover fd lookup/update/delete, helper get with and without create, deletion during cgroup teardown, and invalid fd/refcount-dying cases.
