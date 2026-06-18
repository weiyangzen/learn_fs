# sources/distributed-fs/lustre-release/lustre/mdt/mdt_identity.c

## Purpose
This file implements the MDT identity upcall cache operations. It invokes the configured userspace identity helper, parses downcall identity/group/permission data into kernel cache entries, manages delayed freeing for group_info references, and exposes helpers for getting/putting/flushing identity entries and selecting NID-specific permission masks.

## Important APIs, Types, And Functions
`mdt_identity_upcall_cache_ops` binds the cache callbacks: `mdt_identity_entry_init()`, `mdt_identity_entry_free()`, `mdt_identity_free_delay()`, `mdt_identity_do_upcall()`, and `mdt_identity_parse_downcall()`. Public helpers are `mdt_identity_get()`, `mdt_identity_put()`, `mdt_flush_identity()`, and `mdt_identity_get_perm()`.

## Control Flow
Cache entry initialization zeros `md_identity` and back-points it to its cache entry. On cache miss, `mdt_identity_do_upcall()` validates the upcall path is not `NONE` or empty under `uc_upcall_rwsem`, invokes the helper with cache name and UID key, and returns success after `UMH_WAIT_EXEC`. Downcall parsing bounds group count, allocates/sorts group_info, allocates permission entries, converts legacy NID format to `lnet_nid`, and stores UID/GID/groups/perms in the entry. Freeing releases permission arrays immediately, then either schedules asynchronous work to `put_group_info()` and free the entry or frees directly when no group_info is present.

## State And Persistence
Identity state is an in-memory `upcall_cache` entry keyed by UID. It stores primary UID/GID, optional `group_info`, and optional `md_perm` array. There is no direct on-disk persistence here; freshness and lifetime are controlled by the generic upcall cache. Permission lookup treats `perm[0]` as the default/NID-any permission when applicable.

## Dependencies And Integration Points
The file depends on generic Lustre upcall cache infrastructure, Linux group_info allocation/freeing, `call_usermodehelper()`, identity downcall formats, LNET NID conversion, and credential code in `mdt_lib.c`. MDT credential initialization uses this cache to validate setuid/setgid/setgroups permissions and Kerberos group trust.

## Risks
The upcall path can change concurrently, so `mdt_identity_do_upcall()` guards with the upcall rwsem but still treats `NONE`/empty as `-EREMCHG`. Downcall group counts must remain bounded by `NGROUPS_MAX`; permission allocation failures need to free any already allocated group_info. Delayed free exists because `put_group_info()` can sleep while cache locks may be held; bypassing that pattern would risk sleeping in atomic/locked context. Permission matching assumes any default entry is at index zero.

## Test Signals
Test identity cache miss/upcall invocation, `NONE` and empty upcall behavior, downcall parsing with zero and many groups, over-`NGROUPS_MAX` rejection, multiple permission entries with exact NID match before default, cache flush by UID and idle flush, and cleanup paths with and without `group_info`.
