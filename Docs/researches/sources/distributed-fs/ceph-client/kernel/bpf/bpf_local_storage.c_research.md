# sources/distributed-fs/ceph-client/kernel/bpf/bpf_local_storage.c

Purpose: generic engine for BPF local storage maps, attaching map values to kernel owner objects such as sockets, cgroups, and inodes while also indexing those values by map for cleanup.

Important APIs/types/functions: allocation and ownership helpers include `bpf_selem_alloc`, `bpf_local_storage_alloc`, `bpf_local_storage_update`, `bpf_local_storage_lookup` (declared elsewhere), `bpf_selem_unlink`, `bpf_local_storage_destroy`, `bpf_local_storage_map_alloc_check`, `bpf_local_storage_map_check_btf`, `bpf_local_storage_map_alloc`, and `bpf_local_storage_map_free`. Internal helpers manage owner storage pointers, map buckets, local-storage caches, RCU freeing, memory charge/uncharge, and nofail unlink during destroy/free races.

Control flow: update validates flags and spin_lock usage, finds or creates owner storage through the map's `map_owner_storage_ptr`, allocates a storage element, links it first into the map bucket and then into owner storage under rqspinlocks, and unlinks any replaced element. Delete unlinks from map then owner storage and schedules RCU/Tasks-Trace freeing. Owner destruction walks storage elements and uses `bpf_selem_unlink_nofail` to tolerate races with map free. Map free prevents new users, synchronizes RCU, walks all buckets unlinking elements, waits for storage users and RCU callbacks, then frees buckets and map memory.

State and persistence: each owner has a `bpf_local_storage` list plus small cache slots; each element is linked both to owner storage and to a per-map bucket. Elements persist until deleted, owner destruction, or map free. Memory charge counters track owner-attached storage and element sizes.

Dependencies and integration: depends on BPF map core, owner-specific map ops for storage pointer and optional memory charge hooks, raw rescheduling spinlocks, RCU and RCU Tasks Trace, BTF record field cleanup, map value copy/swap helpers, and cache-index allocation shared by owner-specific storage caches.

Risks: this is concurrency-sensitive two-index lifetime code. Races between owner destruction, map free, update, and delete can leak or double free without the state bits and RCU barriers. rqspinlock timeout paths intentionally warn and may defer cleanup. Cache insertion must not publish deleted elements. BTF object fields must be freed exactly once.

Test signals: local-storage selftests for sockets/cgroups/inodes, concurrent update/delete/map free/owner free stress, BTF spin_lock values, clone flags, memory accounting, RCU torture/KCSAN, and leak detection around nofail unlink paths.
