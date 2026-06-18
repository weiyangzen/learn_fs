# Research: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-lock.h

## Purpose

`dht-lock.h` is the public interface for the DHT lock helper implementation. It exposes a small set of functions used by DHT operations that need to allocate lock descriptors, acquire or release inode locks, release entry locks, protect a namespace entry with parent and dentry locks, and count or free lock arrays.

## Important APIs, Types, and Functions

The header includes `dht-common.h`, which supplies all referenced types. `dht_lock_array_free` owns element cleanup for arrays of `dht_lock_t *`. `dht_lock_count` reports how many requests in a `dht_lock_wrap_t` are currently marked locked. `dht_lock_new` constructs one request against a target subvolume, loc, POSIX lock type, lock domain, optional basename, and failure reaction.

The unlock APIs split by lock type. `dht_unlock_entrylk_wrapper` releases entry locks stored in a wrapper and is intentionally wrapper-oriented, while `dht_unlock_inodelk` accepts an explicit callback and `dht_unlock_inodelk_wrapper` provides the cleanup wrapper form. `dht_blocking_inodelk` is the exported acquisition primitive for arrays of inode locks. `dht_unlock_namespace` releases both namespace entry locks and parent layout inode locks from a `dht_dir_transaction_t`. `dht_protect_namespace` is the high-level helper that takes the parent inodelk and then the child entrylk for one loc/subvolume pair.

## Control Flow and Integration

The header makes lock acquisition asynchronous from the caller's perspective: exported functions take callbacks matching Gluster FOP callback types, and implementation callbacks eventually invoke those callbacks on the original frame. Higher-level DHT code builds arrays of requests with `dht_lock_new`, stores them in `dht_lock_wrap_t` or `dht_dir_transaction_t`, and passes them to these helpers. Cleanup code usually calls the wrapper variants after moving arrays out of active transaction state.

## State and Persistence Behavior

No state is declared in this header. The state contract is implicit in the referenced structures: lock arrays contain per-request `locked` flags, callback pointers, request counts, and aggregate error fields. The lower translators persist live lock state while held; this interface itself is an in-memory orchestration boundary.

## Dependencies and Constraints

Because `dht-lock.h` exposes `dht_dir_transaction_t` and `struct dht_namespace`, its ABI is tightly coupled to `dht-common.h`. The lock domains named by callers, such as `DHT_LAYOUT_HEAL_DOMAIN` and `DHT_ENTRY_SYNC_DOMAIN`, must match the synchronization domain used by other DHT paths. Callers must preserve callback lifetime and must not free arrays while acquisition or unlock callbacks are outstanding.

## Risks and Test Signals

The primary risks are misuse risks: calling wrappers with uninitialized `dht_lock_wrap_t`, using mismatched callbacks, or freeing arrays before async completion. API tests should compile paths that include only this header plus `dht-common.h`, and behavioral tests should validate that namespace lock users always pair `dht_protect_namespace` with `dht_unlock_namespace`.
