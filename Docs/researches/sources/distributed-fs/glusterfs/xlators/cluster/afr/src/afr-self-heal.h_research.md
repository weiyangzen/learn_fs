# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal.h

## Purpose

`afr-self-heal.h` declares the shared AFR self-heal API and several macros used to wind synchronous operations across replica children. It is the contract between the common self-heal engine, the data/metadata/entry/name heal implementations, and self-heald.

The header centralizes public helper prototypes, split-brain user messages, lock APIs, source/sink preparation APIs, and reply/xattr utility functions.

## Important APIs, Types, and Functions

`afr_granular_esh_args_t` carries state for granular entry self-heal callbacks: heal fd, xlator, frame, and a mismatch flag.

`AFR_ONALL`, `AFR_ONLIST`, and `AFR_SEQ` are synchronous stack-wind macros. They wipe local replies, wind a requested FOP to all up children or a supplied child mask, and wait on `local->barrier`.

`ALLOC_MATRIX` allocates a child-count square matrix on the stack. `IA_EQUAL` compares `struct iatt` fields by their `ia_` member.

The header declares top-level operations: `afr_selfheal()`, `afr_throttled_selfheal()`, `afr_selfheal_name()`, `afr_selfheal_data()`, `afr_selfheal_metadata()`, and `afr_selfheal_entry()`.

It declares lock APIs for inode and entry locks, including tie-breaker variants and unlock functions.

It declares discovery/lookup APIs: `afr_selfheal_unlocked_discover()`, `afr_selfheal_unlocked_discover_on()`, `afr_selfheal_unlocked_lookup_on()`, `afr_selfheal_unlocked_inspect()`, and `afr_lookup_and_heal_gfid()`.

It declares direction, xattr, and post-op APIs such as `afr_selfheal_find_direction()`, `afr_selfheal_extract_xattr()`, `afr_selfheal_fill_matrix()`, `afr_selfheal_undo_pending()`, `afr_selfheal_post_op()`, and `afr_selfheal_restore_time()`.

It declares source policy and split-brain helpers, including favorite-child functions, GFID split-brain source selection, source/sink marking for empty files, and child index lookup.

## Control Flow

Callers use this header in two layers. High-level callers invoke `afr_selfheal()` for a GFID or `afr_selfheal_name()` for a specific parent/name. Type-specific modules call the common prepare functions and helpers to implement their healing sequence.

The wind macros define the common asynchronous-to-synchronous control pattern: prepare a child mask, set the barrier wait count, clear prior replies, wind child FOPs with the child index as cookie, and wait for callbacks to fill `local->replies`.

The prepare functions declared here provide a common source/sink contract for data, metadata, and entry heals: callers pass locked children, reply arrays, and output arrays for sources, sinks, and healed sinks.

## State and Persistence Behavior

The header itself persists no state, but its APIs operate on AFR pending xattrs, inode/entry locks, `afr_local_t` reply arrays, inode tables, and brick namespace state.

`AFR_ONALL` snapshots `priv->child_up` before winding so a single operation sees a stable set of children even if child-up state changes concurrently.

Stack allocation macros mean most source/sink matrices and child masks are transient and frame-scoped. Callers must not retain them after returning.

The declared message constants are used in xdata responses and logs for split-brain and CLI heal operations.

## Dependencies and Integration Points

The header assumes inclusion after AFR core types are available, especially `xlator_t`, `call_frame_t`, `inode_t`, `fd_t`, `dict_t`, `afr_private_t`, `afr_local_t`, `struct afr_reply`, and `afr_transaction_type`.

It integrates all files in this subset and is also included by other AFR files that need self-heal primitives. `afr-self-heald.h` separately declares daemon-specific types but depends on functions declared here.

## Risks and Edge Cases

`AFR_ONALL` and `AFR_ONLIST` set `barrier.waitfor` to the child count and then call `syncbarrier_wait()`. Incorrect masks or callbacks that fail to wake the barrier will deadlock self-heal.

The macros use `alloca`, so child-count-dependent allocations consume stack. `ALLOC_MATRIX` is especially expensive for large replica counts.

Because macros wipe `local->replies`, callers must copy replies they still need before issuing another macro-driven FOP.

The header exposes many internal helpers, making cross-file coupling tight. Changing source/sink array semantics in one implementation can break others.

## Test Signals

Compile-time coverage should catch prototype drift among self-heal files. Runtime tests should indirectly validate `AFR_ONALL`, `AFR_ONLIST`, and `AFR_SEQ` through lock, lookup, xattrop, fsync, and setattr paths across child masks.

Useful fault-injection tests include missing callback wakeups, child-down changes during a macro invocation, reply wiping between operations, and large replica counts that stress stack allocation.
