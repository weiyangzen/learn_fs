# Research: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-lock.c

## Purpose

`dht-lock.c` implements the DHT translator's internal distributed lock orchestration for inode locks, entry locks, and the combined namespace protection sequence used by operations that must avoid racing with layout changes, renames, and migration. It converts arrays of `dht_lock_t` requests into ordered Gluster FOP winds, tracks which subvolume locks were acquired, unwinds partial acquisitions on failure, and provides wrapper helpers for deferred cleanup from higher-level DHT transaction state.

## Important APIs, Types, and Functions

The file operates on types declared in `dht-common.h`: `dht_lock_t`, `dht_lock_wrap_t`, `dht_dir_transaction_t`, `dht_reaction_type_t`, and `dht_lock_type_t`. Public functions exported by `dht-lock.h` are implemented here: `dht_lock_array_free`, `dht_lock_count`, `dht_lock_new`, `dht_unlock_entrylk_wrapper`, `dht_unlock_inodelk`, `dht_unlock_inodelk_wrapper`, `dht_blocking_inodelk`, `dht_unlock_namespace`, and `dht_protect_namespace`.

Key internal helpers include `dht_lock_frame`, which clones the parent frame and assigns a unique lock owner derived from the root frame pointer; `dht_lock_request_cmp` and `dht_lock_order_requests`, which sort lock requests by subvolume name and GFID; `dht_local_entrylk_init` and `dht_local_inodelk_init`, which attach lock arrays and callbacks to `dht_local_t`; and the recursive wind/callback pairs for blocking entry locks and inode locks. `dht_lock_new` allocates from `conf->lock_pool`, duplicates the lock domain and optional basename, and deliberately fills only `loc.inode` plus GFID to avoid path based resolution races after delete and recreate.

## Control Flow

Lock acquisition is serial, not fan-out. For entry locks, `dht_blocking_entrylk` creates a lock frame, stores the sorted request array, copies the lock owner into every lock, and calls `dht_blocking_entrylk_rec` starting at index 0. Each callback marks the request locked or applies its failure policy. On unrecoverable failure it calls `dht_entrylk_cleanup`, which unlocks all already-acquired entry locks before invoking the original callback on the main frame. On success or tolerated ENOENT/ESTALE, it recurses to the next request and finally calls `dht_entrylk_done`.

The inode lock path mirrors the entry lock path with `inodelk` FOPs and `F_SETLKW` for blocking acquisition. `dht_unlock_inodelk` and the entry lock unlock helper issue unlocks only for locks marked `locked`, restore each lock's saved `lk_owner` before winding, and use `local->call_cnt` plus `dht_frame_return` to detect the last callback.

`dht_protect_namespace` composes the two lock types for one subvolume. It builds the parent loc, creates a read `inodelk` on `DHT_LAYOUT_HEAL_DOMAIN`, creates a write `entrylk` on `DHT_ENTRY_SYNC_DOMAIN` for `loc->name`, takes the parent inodelk first, and then takes the entrylk in `dht_blocking_entrylk_after_inodelk`. If entry locking fails after inode locking, it frees the entry request array and unlocks the parent layout lock before invoking the namespace callback.

## State and Persistence Behavior

Lock state is in memory only. `locked`, `lk_owner`, `op_ret`, and `op_errno` fields in `dht_lock_t` and `dht_lock_wrap_t` drive cleanup decisions. The actual locks are persisted only as live locks in lower translators and bricks via `entrylk` and `inodelk`; this file does not write durable metadata. `dht_lock_array_reset` clears ownership of arrays from a wrapper without freeing them, while `dht_lock_array_free` and `dht_lock_free` wipe locs, free duplicated strings, and return lock objects to the configured mem-pool.

## Dependencies and Integration Points

This layer depends on Gluster frame and stack primitives (`copy_frame`, `STACK_WIND_COOKIE`, `DHT_STACK_DESTROY`), DHT local allocation (`dht_local_init`), loc helpers (`dht_build_parent_loc`, `loc_gfid`, `loc_wipe`), lock owner helpers, and lower subvolume FOP tables. It logs using IDs from `dht-messages.h`, including lock allocation, unlock, and inode lock failure IDs. Callers in DHT create, rename, layout heal, and migration paths can store locks in `local->lock` or `local->current->ns` and invoke the wrappers for cleanup.

## Risks and Edge Cases

The deterministic lock ordering is critical. Any caller bypassing it or mixing differently ordered lock paths can reintroduce distributed deadlocks. Cleanup is best effort: if a frame or local cannot be allocated for unlock, the code logs that stale locks might be left. The tolerated failure policy is subtle; `IGNORE_ENOENT_ESTALE` and `IGNORE_ENOENT_ESTALE_EIO` are safe only when the higher-level operation can proceed if a target disappeared or returned EIO.

One suspicious detail is in `dht_blocking_inodelk_cbk`: the final "did any lock succeed" loop checks `!dht_lock->locked` using the current lock pointer rather than `!my_layout->locks[i]->locked`, unlike the entry lock path. That makes the all-failed test depend on the last callback's lock state and is a useful regression-test target.

## Test Signals

Useful tests should cover ordered acquisition across multiple subvolumes, partial acquisition followed by cleanup, wrapper unlock after ownership transfer, namespace protection failure after the parent lock succeeds, and tolerated ENOENT/ESTALE/EIO policy combinations. Log signals include `DHT_MSG_INODELK_FAILED`, `DHT_MSG_ENTRYLK_FAILED_AFT_INODELK`, `DHT_MSG_UNLOCKING_FAILED`, and stale-lock warnings. Runtime validation can assert no remaining brick locks after induced mid-sequence failures.
