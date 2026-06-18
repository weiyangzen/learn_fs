# sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_crr.c

## Purpose

`nrs_crr.c` implements the CRR-N NRS policy, a client-NID round-robin scheduler for PTLRPC requests. It batches requests per client NID up to a configurable quantum, orders batches by scheduling round and sequence, and exposes debugfs control for the quantum.

## Important APIs, Types, and Functions

The policy uses `struct nrs_crrn_net` for per-policy scheduler state and `struct nrs_crrn_client` for per-client resource buckets. The main hooks are `nrs_crrn_start`, `nrs_crrn_stop`, `nrs_crrn_ctl`, `nrs_crrn_res_get`, `nrs_crrn_res_put`, `nrs_crrn_req_get`, `nrs_crrn_req_add`, `nrs_crrn_req_del`, and `nrs_crrn_req_stop`. `crrn_req_compare` is the binheap comparator. `nrs_crrn_hashfn`, `nrs_crrn_cmpfn`, and `nrs_crrn_hash_params` define the client rhashtable keyed by `struct lnet_nid`. The exported configuration is `nrs_conf_crrn`.

Debugfs support is provided by `ptlrpc_lprocfs_nrs_crrn_quantum_seq_show`, `ptlrpc_lprocfs_nrs_crrn_quantum_seq_write`, and `nrs_crrn_lprocfs_init`, which expose `nrs_crrn_quantum` for regular and HP queues.

## Control Flow

Starting the policy allocates `nrs_crrn_net`, creates an atomic-grow binheap, initializes the client rhashtable, sets the default quantum to `OBD_MAX_RIF_DEFAULT`, and seeds sequence numbering at 1. Resource acquisition is two-level: the first call returns the scheduler resource embedded in `nrs_crrn_net`; the second looks up or inserts a client object by request peer NID, increments its reference count, and returns the client resource.

Enqueue obtains the client bucket from the request resource, decides whether the client needs a new scheduling round, assigns round and sequence to the request, inserts it into the heap, increments active request count, and decrements the client's remaining quantum. The comparator sorts by lower round first and lower sequence first, preserving batched client fairness. Dispatch removes the heap root, decrements the client's active count, logs the start, and advances the global round to the next request's round or increments it if the heap is empty. Dequeue has similar root-adjustment logic when removing a queued request before service.

Quantum control reads or writes `cn_quantum` through `ptlrpc_nrs_policy_control`. The write path accepts `reg_quantum:`, `hp_quantum:`, or a bare numeric value, validates against `LPROCFS_NRS_QUANTUM_MAX`, skips stopped policy instances through `-ENODEV`, and returns success if at least one requested live queue accepted the change.

## State and Persistence Behavior

All state is volatile. `nrs_crrn_net` owns the heap, client hash, global round, global sequence, and current quantum. Each client tracks NID, resource, refcount, active queued requests, current round, sequence, and remaining quantum. No state is persisted across service restart; quantum changes are runtime debugfs settings only.

Client objects remain in the rhashtable for the policy lifetime and are freed during policy stop after the heap is empty and all references have been released. The file asserts zero client references when destroying the hash.

## Dependencies and Integration Points

CRR-N depends on NRS core policy hooks, PTLRPC request peer IDs, LNet NID hashing and formatting, Lustre binheap utilities, Linux rhashtable, debugfs/lprocfs helpers, and PTLRPC policy control. It is registered as `crrn` with compatibility for all PTLRPC services when server policies are enabled.

## Risks and Edge Cases

The scheduler trades strict FIFO latency for per-client fairness; inactive clients with unused quantum are moved to a new round to avoid fragmented batches. `cn_quantum` is documented as accessed unlocked in enqueue, so debugfs writes can race with scheduling decisions but keep the value nonzero. Client hash insertion handles duplicate insertion races, but client objects are only reclaimed at policy stop, so workloads with many transient NIDs grow memory until stop. Request movement to HP can allocate client resources with `GFP_ATOMIC` and can fail under pressure.

## Test Signals

Tests should cover two or more clients with different request rates, quantum exhaustion moving a client to the next round, inactive-client unused quantum behavior, heap ordering by round then sequence, dequeue of the root versus non-root, resource lookup/insert races, reference release at finalize, policy stop with empty heap, debugfs regular/HP/bare quantum parsing, invalid zero or oversized quantum, and stopped-policy `-ENODEV` handling.
