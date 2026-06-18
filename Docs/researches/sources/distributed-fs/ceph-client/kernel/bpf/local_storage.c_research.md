# sources/distributed-fs/ceph-client/kernel/bpf/local_storage.c

## Purpose

`local_storage.c` implements legacy cgroup local-storage map support under `CONFIG_CGROUP_BPF`. It provides shared and per-CPU cgroup storage maps keyed by cgroup ID or by `(cgroup_inode_id, attach_type)`, plus allocation, lookup, update, seq display, and link/unlink operations used when BPF programs attach to cgroups.

## Important APIs, Types, And Functions

`struct bpf_cgroup_storage_map` embeds `struct bpf_map` and adds a spinlock, rb-tree root, and ordered list of storages. `map_to_storage()` converts from generic map to cgroup storage map. `attach_type_isolated()` distinguishes the full `struct bpf_cgroup_storage_key` key mode from the plain `u64 cgroup_inode_id` mode.

Lookup and indexing use `bpf_cgroup_storage_key_cmp()`, `cgroup_storage_lookup()`, `cgroup_storage_insert()`, and `cgroup_storage_get_next_key()`. Storage objects are indexed in both an rb-tree for lookup and a list for key iteration.

Map operations include `cgroup_storage_lookup_elem()`, `cgroup_storage_update_elem()`, `bpf_percpu_cgroup_storage_copy()`, `bpf_percpu_cgroup_storage_update()`, `cgroup_storage_map_alloc()`, `cgroup_storage_map_free()`, `cgroup_storage_delete_elem()`, `cgroup_storage_check_btf()`, `cgroup_storage_seq_show_elem()`, and `cgroup_storage_map_usage()`.

Program and cgroup integration functions include `bpf_cgroup_storage_assign()`, `bpf_cgroup_storage_alloc()`, `bpf_cgroup_storage_free()`, `bpf_cgroup_storage_link()`, and `bpf_cgroup_storage_unlink()`.

The exported map ops table is `cgroup_storage_map_ops`, with BTF ID metadata for `struct bpf_cgroup_storage_map`.

## Control Flow

Map allocation validates key size, value size, map flags, NUMA node, and zero `max_entries`, then initializes the embedded map, spinlock, rb-tree, and list. Per-CPU storage caps value size at `PCPU_MIN_UNIT_SIZE`; shared storage uses the general local storage max.

Storage lookup locks the map unless the caller already holds it, walks the rb-tree by key comparison, and returns the matching `struct bpf_cgroup_storage` or NULL. Element lookup returns the shared buffer's data pointer. Shared updates either copy under `BPF_F_LOCK` or allocate a new buffer, initialize BTF fields, atomically swap `storage->buf`, and RCU-free the old buffer.

Per-CPU copy/update paths find the storage under RCU, then either copy one CPU selected via `BPF_F_CPU` or iterate all possible CPUs. Values are rounded to 8-byte units for full per-CPU dumps, avoiding kernel data leaks because per-CPU allocation is zero-filled.

When a BPF program using cgroup storage is attached, `bpf_cgroup_storage_alloc()` creates the storage for the map assigned in `prog->aux->cgroup_storage[stype]`, allocating either a shared `bpf_storage_buffer` or per-CPU buffer. `bpf_cgroup_storage_link()` sets the key from cgroup ID and attach type, inserts into the map rb-tree and map list, and links into `cgroup->bpf.storages`. Unlink removes all three relationships.

Map free takes `cgroup_lock()`, walks all storages, unlinks and frees each, validates empty indices, and frees the map memory.

## State And Persistence Behavior

Map-level state is persistent for the map lifetime: rb-tree index, list of storages, spinlock, and map metadata. Storage-level state persists while a cgroup attachment owns it and is tied to both the BPF map and the cgroup.

Shared storage values are RCU-swapped buffers. Per-CPU storage values live in per-CPU allocations. Storage objects are freed after RCU grace periods through shared or per-CPU callbacks.

Delete-by-key is not supported and returns `-EINVAL`; storage lifetime is controlled by cgroup attach/detach and map release paths rather than arbitrary map deletes.

## Dependencies And Integration Points

The file is compiled only under `CONFIG_CGROUP_BPF`. It depends on cgroup internals, `struct bpf_cgroup_storage`, BPF map allocation helpers, BTF type checking and display, spin locks, rb-trees, RCU, per-CPU allocation, and cgroup attach infrastructure.

It integrates with BPF program aux state through `bpf_cgroup_storage_assign()` and with cgroup storage lists through `cgroup->bpf.storages`.

## Risks And Edge Cases

Key shape determines isolation semantics. A map with plain `u64` keys ignores attach type, while `struct bpf_cgroup_storage_key` includes it; BTF validation must match the chosen key size or user space can see confusing failures.

Shared updates allocate a new value and swap it under RCU, so readers must stay in RCU critical sections. Per-CPU copy/update flags pack CPU IDs into upper bits; invalid CPU values or flag combinations should be caught by map syscall validation and these helpers.

Map memory accounting reports only the map object and explicitly does not count dynamically allocated storage elements, which can understate memory usage.

Lock ordering between map spinlock, cgroup lock, and RCU must remain consistent. Link/unlink touches rb-tree, map list, and cgroup list under the map lock.

## Test Signals

Tests should cover shared and per-CPU cgroup storage maps, both key formats, BTF key validation, `BPF_F_LOCK` updates, per-CPU `BPF_F_CPU` and all-CPU copy/update behavior, get-next-key ordering, seq_file display, attach/detach link/unlink, and map free with live storages.
