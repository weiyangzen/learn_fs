# sources/distributed-fs/ceph-client/kernel/bpf/bpf_inode_storage.c

Purpose: provides inode-owned BPF local storage maps and LSM/helper accessors.

Important APIs/types/functions: `DEFINE_BPF_STORAGE_CACHE(inode_cache)`, `inode_storage_ptr`, `inode_storage_lookup`, `bpf_inode_storage_free`, fd-based lookup/update/delete ops, `bpf_inode_storage_get`, `bpf_inode_storage_delete`, and `inode_storage_map_ops`.

Control flow: fd-based syscalls use `CLASS(fd_raw, f)` to resolve a file and operate on `file_inode`. Updates reject inodes without a BPF storage blob. BPF helpers accept a `struct inode *`, require BPF RCU, optionally create storage using `BPF_LOCAL_STORAGE_GET_F_CREATE`, and return a map value pointer or deletion result. Inode teardown calls `bpf_inode_storage_free`, which destroys all local storage attached to the inode.

State and persistence: storage lives in the inode's `bpf_storage_blob` and persists with the inode until deletion, map free, or inode destruction.

Dependencies and integration: integrates with generic BPF local storage, inode BPF blobs, file descriptor handling, BPF LSM/BTF id validation, RCU read-side sections, and map BTF validation.

Risks: helper callers must guarantee the inode has a refcount and cannot be freed. Not all inodes have storage blobs, so update/create must check `inode_storage_ptr`. Lifetime bugs can become UAFs because storage is owner-attached.

Test signals: BPF LSM inode storage selftests, fd-based map operation tests, deletion on inode eviction, invalid fd handling, and inodes without storage blobs.
