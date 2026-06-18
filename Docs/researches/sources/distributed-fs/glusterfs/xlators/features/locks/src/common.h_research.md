# sources/distributed-fs/glusterfs/xlators/features/locks/src/common.h

## Purpose

`common.h` exposes the shared interface for the posix-locks translator. It defines lock dump format strings, the common unwind-and-cleanup macro, byte-range lock return codes, and prototypes for byte-range locking, inode/entry domain locking, tracing, mandatory-lock helpers, reserve-lock helpers, and inode-removal coordination.

## Important APIs, types, and functions

- Dump format macros (`RANGE_FMT`, `ENTRY_FMT`, `DUMP_*`, `ENTRY_*`, `RANGE_*`) standardize statedump/log rendering for granted and blocked locks.
- `PL_STACK_UNWIND_AND_FREE()` unwinds a strict fop and then releases all resources held by `pl_local_t`, including inodelk domain-count data, two locs, fd, inode, xdata, and the local object.
- `enum { PL_LOCK_GRANTED, PL_LOCK_WOULD_BLOCK, PL_LOCK_QUEUED }` describes `pl_setlk()` results.
- Prototypes expose byte-range lock lifecycle (`new_posix_lock`, `pl_getlk`, `pl_setlk`, `pl_lock_preempt`, `grant_blocked_locks`, `posix_lock_to_flock`, `locks_overlap`, `same_owner`, `__delete_lock`, `__destroy_lock`).
- Domain and inode helpers (`get_domain`, `pl_inode_get`, `pl_update_refkeeper`) are shared by entrylk, inodelk, and other lock families.
- Inodelk/entrylk grant, cleanup, count, and contention APIs are declared for cross-file use.
- Tracing helpers (`pl_trace_*`, `entrylk_trace_*`, `pl_print_*`) centralize request/response/block logging.
- Mandatory and removal helpers (`pl_is_mandatory_locking_enabled`, `pl_inode_remove_*`) define the cross-module removal protocol.

## Control flow

The header itself has no runtime control flow, but it defines cleanup control through `PL_STACK_UNWIND_AND_FREE()`: callers must detach `frame->local`, unwind, then release every referenced member. The prototypes reveal the module boundaries: common byte-range code calls out to inodelk/entrylk grant functions, while inodelk/entrylk call back into common for domains, tracing, owner validation, local cleanup, and removal synchronization.

## State and persistence behavior

The macro encodes ownership transfer of `pl_local_t` fields after a fop unwinds. It clears pointers after unref/wipe to avoid accidental reuse during cleanup. No persistent state is declared here, but APIs include mandatory-lock enforcement and count functions that observe in-memory `pl_inode_t` state and xattr-backed policy.

## Dependencies and integration points

This header depends on lock types from `locks.h`, Gluster fop stack APIs, loc/fd/inode/dict reference APIs, and lk-owner/flock types. It is included by core implementation files such as `common.c`, `entrylk.c`, and `inodelk.c`, making it the contract layer for lock operations across the xlator.

## Risks and edge cases

- `PL_STACK_UNWIND_AND_FREE()` is a large macro with side effects and assumes `frame` and local fields are valid in a narrow ownership context.
- Several double declarations appear (`__pl_inodelk_unref` is listed twice), which is harmless in C but signals interface sprawl.
- Functions with `__` prefixes are exposed across files, so internal locking assumptions are not enforced by the type system.
- Dump format macros require caller-supplied arguments to match exactly; mismatches would be compile-time warnings only when format checking sees through macro expansion.

## Test signals

Compilation with strict warnings is important for prototype drift and format mismatches. Runtime tests should exercise `PL_STACK_UNWIND_AND_FREE()` paths for successful, failed, and blocked lock unwinds to detect leaked loc/fd/inode/dict references.
