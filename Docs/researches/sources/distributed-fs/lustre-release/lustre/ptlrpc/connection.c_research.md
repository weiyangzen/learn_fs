# Research: sources/distributed-fs/lustre-release/lustre/ptlrpc/connection.c

## Purpose
`connection.c` manages PTLRPC client connection objects keyed by LNet process identity and maintains per-CPU latency QoS requests used by PTLRPC. It provides connection lookup/creation/reference helpers and module-level initialization/finalization for the connection hash and CPU latency structures.

## Important APIs, Types, And Functions
The global connection table is `conn_hash`, an rhashtable keyed by `struct lnet_processid`. `cpus_latency_qos` is a per-CPU array of `struct cpu_latency_qos`. Public functions are `ptlrpc_connection_get()`, `ptlrpc_connection_addref()`, `ptlrpc_connection_init()`, and `ptlrpc_connection_fini()`.

`lnet_process_id_hash()` and `lnet_process_id_cmp()` avoid raw byte hashing because `struct lnet_processid` may contain unassigned bytes. `conn_hash_params` supplies key/head offsets plus custom hash and compare callbacks.

## Control Flow
`ptlrpc_connection_get()` normalizes the peer NID to its primary NID, looks up an existing connection, and increments its refcount if found. On miss, it allocates a new `struct ptlrpc_connection`, initializes peer and refcount, then inserts it with `rhashtable_lookup_get_insert_fast()`. If another thread inserted the same peer concurrently, the new allocation is freed and the existing object is referenced. Transient rhashtable resize errors `-ENOMEM` or `-EBUSY` sleep briefly and retry.

`ptlrpc_connection_addref()` atomically increments the refcount and returns the same object. `conn_exit()` is the rhashtable destroy callback and asserts that every remaining connection has zero references before freeing it.

`ptlrpc_connection_init()` allocates `cpus_latency_qos` for `nr_cpu_ids`, initializes each delayed work item, mutex, and default max time, then initializes `conn_hash`. `cpu_latency_work()` fires when a per-CPU QoS request deadline expires, clears the active request under the per-CPU mutex, and removes/frees the PM QoS request outside the lock. If the deadline has not arrived, it reschedules itself for the remaining jiffies.

`ptlrpc_connection_fini()` removes any active per-CPU PM QoS requests, cancels their delayed work, frees the per-CPU array, and destroys the connection hash with `conn_exit()`.

## State And Persistence
Connection state is volatile. Each connection stores peer process identity and an atomic refcount. The rhashtable provides process-wide sharing so imports to the same peer reuse a connection object. CPU latency QoS state is per CPU and includes a mutex, delayed work, active `dev_pm_qos_request`, deadline, and max timeout. No state is persisted across module unload.

## Dependencies And Integration Points
The file depends on Linux rhashtable, device PM QoS, LNet NID helpers, Lustre allocation/debug helpers, and `ptlrpc_internal.h`. `ptlrpc_uuid_to_connection()` in `client.c` resolves UUIDs to LNet peer/self IDs and calls `ptlrpc_connection_get()`. Import code holds and releases connection references around RPC communication.

## Risks
The CPU index calculation in `cpu_latency_work()` depends on pointer arithmetic over the allocated per-CPU array and must match the allocation type. Connection finalization asserts zero refs; leaked import references will trip `LASSERTF`. The insert path must tolerate rhashtable resizing and duplicate insertion races; unexpected errors currently cause the allocation to be freed and `NULL` returned.

## Test Signals
Tests should cover concurrent connection creation for the same peer, lookup after primary NID normalization, module init/fini with and without successful QoS allocation, active PM QoS cleanup on fini, rhashtable resize retry behavior, and leak detection by ensuring all connection references are dropped before `ptlrpc_connection_fini()`.
