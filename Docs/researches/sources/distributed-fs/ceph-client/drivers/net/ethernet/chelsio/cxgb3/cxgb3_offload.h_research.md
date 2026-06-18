# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_offload.h

## Purpose

`cxgb3_offload.h` defines the public in-driver interface for the Chelsio T3 offload layer. It declares activation/deactivation functions, client registration callbacks, event IDs, CPL handler signatures and return flags, TID table structures, `struct t3c_data`, and helper accessors used by upper-layer offload clients and sibling driver files. It is the contract that allows `cxgb3_main.c`, `cxgb3_offload.c`, `l2t.c`, and protocol clients to share T3 offload state safely.

## Important APIs, types, and functions

- Lifecycle declarations: `cxgb3_offload_init()`, `cxgb3_adapter_ofld()`, `cxgb3_adapter_unofld()`, `cxgb3_offload_activate()`, `cxgb3_offload_deactivate()`, and `cxgb3_set_dummy_ops()`.
- Device conversion: `dev2t3cdev()` maps a netdevice to its owning T3 offload device.
- Client management: `cxgb3_register_client()`, `cxgb3_unregister_client()`, `cxgb3_add_clients()`, `cxgb3_remove_clients()`, and `cxgb3_event_notify()`.
- `struct cxgb3_client`: client name, adapter add/remove callbacks, CPL handler vector, redirect callback, list node, and event callback.
- Event enum: `OFFLOAD_STATUS_UP`, `OFFLOAD_STATUS_DOWN`, `OFFLOAD_PORT_DOWN`, `OFFLOAD_PORT_UP`, `OFFLOAD_DB_FULL`, `OFFLOAD_DB_EMPTY`, and `OFFLOAD_DB_DROP`.
- TID APIs: `cxgb3_alloc_atid()`, `cxgb3_free_atid()`, `cxgb3_insert_tid()`, `cxgb3_queue_tid_release()`, and `cxgb3_remove_tid()`.
- CPL dispatch contract: `cxgb3_cpl_handler_func`, `cpl_handler_func`, `cplhdr()`, `t3_register_cpl_handler()`, priority constants, and return flags `CPL_RET_BUF_DONE`, `CPL_RET_BAD_MSG`, and `CPL_RET_UNKNOWN_TID`.
- TID storage: `struct t3c_tid_entry`, `union listen_entry`, `union active_open_entry`, `struct tid_info`, and `struct t3c_data`.
- Accessor macro: `T3C_DATA(dev)` stores a `struct t3c_data *` in `t3cdev.l4opt`.

## Control flow

The header itself has no executable control flow beyond `cplhdr()`, but it defines the expected sequence for offload consumers. A client registers a `struct cxgb3_client`; when an adapter activates, the driver calls the client's `add()` callback with a `struct t3cdev *`. The client allocates ATIDs or inserts TIDs through the TID APIs, sends work requests through `cxgb3_ofld_send()` declared in `l2t.h`, and receives firmware CPLs through handler vectors indexed by CPL opcode. During connection teardown the client calls `cxgb3_remove_tid()` or release helpers, and during adapter or port events it receives event notifications.

## State and persistence behavior

The main state schema is `struct t3c_data`, which is per-active `t3cdev` and contains work-request limits, MTU table references, TID maps, release-work state, reserve skb, and release-incomplete flag. `struct tid_info` partitions dynamic TID storage into hardware TIDs, server/listen TIDs, and active-open TIDs, with atomics and spinlocks for concurrent use. This header defines volatile runtime state only; it does not describe any on-disk persistence. The `T3C_DATA()` macro is type-punning storage over `t3cdev.l4opt`, so layout compatibility with `struct t3cdev` is essential.

## Dependencies and integration points

The header includes Linux list and skb definitions, `l2t.h`, `t3cdev.h`, and `t3_cpl.h`. It integrates with `cxgb3_offload.c` as the implementation, `cxgb3_main.c` as lifecycle caller, `l2t.c` for L2 table operations, and external protocol modules that register `cxgb3_client` instances. It also exposes exported functions implemented in `cxgb3_offload.c`.

## Risks and edge cases

- Client handler arrays must be sized and indexed according to `NUM_CPL_CMDS`; the header does not enforce bounds for client vectors.
- `T3C_DATA()` uses pointer casting into `t3cdev.l4opt`; changes to `t3cdev` type or constness can silently break this accessor.
- `ctx` in `struct t3c_tid_entry` is overloaded by the release queue implementation as a next pointer after client removal, so clients must not access released entries.
- The cacheline alignment choices in `struct tid_info` are performance and correctness hints for concurrent allocation; refactoring field order could affect lock contention.
- Event IDs are unversioned enum values; external clients must be recompiled together with the driver if values change.

## Test signals

Header-level validation is compile-time: all offload clients should build without type warnings, handler signatures should match, exported symbols should resolve, and sparse/lockdep review should check use of TID APIs in softirq and process contexts. ABI-sensitive changes should be tested by building iSCSI/RDMA clients that use `cxgb3_client`, `T3C_DATA()`, CPL handler arrays, and TID allocation/removal paths.
