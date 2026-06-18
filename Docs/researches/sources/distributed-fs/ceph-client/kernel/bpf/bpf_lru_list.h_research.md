# sources/distributed-fs/ceph-client/kernel/bpf/bpf_lru_list.h

## Purpose
`bpf_lru_list.h` declares the private LRU data model used by BPF LRU hash maps. It defines list states, embedded node metadata, shared and per-CPU list containers, the delete callback contract, and the small public API implemented by `bpf_lru_list.c`.

## Important APIs, Types, and Functions
`enum bpf_lru_list_type` separates global list states (`ACTIVE`, `INACTIVE`, `FREE`) from local-only states (`LOCAL_FREE`, `LOCAL_PENDING`). `struct bpf_lru_node` is embedded in map elements and carries `list`, `cpu`, `type`, and `ref`. `struct bpf_lru_list` contains the three global lists, active/inactive counts, `next_inactive_rotation`, and a cacheline-aligned raw spinlock. `struct bpf_lru_locallist` contains local free/pending lists, a round-robin steal cursor, and a raw spinlock. `struct bpf_lru` is the owning controller and stores either a common-LRU layout or a per-CPU-LRU layout, plus `del_from_htab`, `hash_offset`, scan/free targets, and mode. `bpf_lru_node_set_ref()` is the inline hot-path reference marker used by hash-map lookup/update code.

## Control Flow
Callers initialize a `struct bpf_lru`, populate it with preallocated elements and their embedded-node offsets, mark references as entries are used, pop nodes for insertion, push nodes back on deletion or failed insertion, and finally destroy per-CPU allocations. The header intentionally exposes only the high-level pop/push/init/populate/destroy operations plus reference-bit setting; all list migration details stay in the C file.

## State and Persistence Behavior
The structures persist for the lifetime of the owning map. The `ref` byte is a second-chance hint rather than a refcount; it is set without locking by callers through `READ_ONCE`/`WRITE_ONCE` and cleared when nodes rotate or are reinserted. The `cpu` field records the local/per-CPU owner used for per-CPU free return and common-LRU pending ownership. No state is persistent across map destruction or reboot.

## Dependencies and Integration Points
The header depends on Linux cacheline alignment, intrusive lists, spinlock types, and BPF integer types from surrounding includes. Its primary consumer is BPF hashtable code, but the API is intentionally map-internal rather than UAPI. The `del_from_htab_func` callback is the handshake between generic LRU policy and map-specific hash bucket deletion.

## Risks
ABI-like coupling exists between the map element layout and `hash_offset`/`node_offset` values passed to the implementation. Incorrect offsets corrupt element memory. Because `type` is an 8-bit state machine shared with list membership, any unsynchronized direct mutation outside the implementation can make subsequent list operations unsafe. Ref-bit semantics are lossy by design, so tests should not interpret them as precise usage counts.

## Test Signals
Build coverage should catch missing type declarations across kernel configuration variants. Runtime signals include BPF LRU hash selftests, map element layout tests, ref-bit preservation tests under lookup/update churn, and teardown tests that verify `bpf_lru_destroy()` frees only the per-CPU container chosen by `bpf_lru_init()`.
