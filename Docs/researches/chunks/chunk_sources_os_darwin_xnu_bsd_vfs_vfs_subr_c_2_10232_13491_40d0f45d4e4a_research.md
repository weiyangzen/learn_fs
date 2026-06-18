# Chunk Research: sources/os/darwin/xnu/bsd/vfs/vfs_subr.c lines 10232-13491

## Scope

This chunk covers the tail of vnode authorization, vnode attribute validation for create/setattr, assorted mount/vnode state helpers, orphaned AppleDouble cleanup during `rmdir`, panic/debug vnode tracing support, trigger vnode resolver plumbing, optional file lease management, and two small vnode utility APIs.

## APIs and Entry Points

- `vnode_authorize_callback_int()` continues from the previous chunk and completes local KAUTH authorization against vnode and optional parent attributes.
- `vnode_attr_authorize_init()` initializes the `vnode_attr` fields required by `vnode_attr_authorize()`.
- `vnode_attr_authorize()` authorizes already-fetched vnode attributes, including mount read-only/noexec checks and local security completeness checks.
- `vnode_authattr_new()` / `vnode_authattr_new_internal()` default and validate attributes for new objects.
- `vnode_authattr()` validates requested `VNOP_SETATTR` attributes and returns the KAUTH rights needed to apply them.
- Trigger APIs include `vnode_trigger_update()`, `vnode_trigger_rearm()`, `vnode_trigger_resolve()`, `vfs_nested_trigger_unmounts()`, and `vfs_addtrigger()`.
- Under `CONFIG_FILE_LEASES`, public lease APIs include `vnode_setlease()`, `vnode_getlease()`, `vnode_breaklease()`, `vnode_breakdirlease()`, and `vnode_revokelease()`.
- `rmdir_remove_orphaned_appleDouble()` validates and removes only orphaned `._*` entries from an otherwise empty directory before retrying `rmdir`.
- `vnode_rdadvise()` sends `F_RDADVISE`; `vnode_hasmultipath()` detects multiple vnode paths by cached flags or link counts.

## Key Control Flow

Authorization strips action control bits, rejects read-only/noexec violations, handles opaque auth, translates namedstream data rights into extended-attribute rights, fetches vnode/parent attributes, then delegates to `vnode_attr_authorize_internal()`.

New-object attribute handling defaults uid/gid/mode/create time, inherits `UF_DATAVAULT` and `SF_RESTRICTED`, validates flag masks, and enforces non-root ownership, group, UUID, setuid, and setgid constraints.

`vnode_authattr()` fetches only needed old attributes, validates requested setattr changes, may mutate the requested attributes, and returns the KAUTH mask needed to authorize the write.

`rmdir_remove_orphaned_appleDouble()` suspends the directory, scans entries to ensure only dot entries and valid `._*` files remain, then unlinks those files and resumes the vnode.

Trigger vnode code packs resolver status into sequence-numbered results, attaches resolver callbacks to vnodes, resolves/unresolves outside resolver locks, and best-effort unresolves nested trigger mounts during unmount.

File lease code gates operations on entitlement, tracks leases per vnode under vnode lock, sends knote downgrade/release events on conflicts, and waits or forcibly breaks leases after timeout.

## State and Dependencies

State flows through `_vnode_authorize_context`, `vnode_attr`, KAUTH action bits, cached authorization rights, vnode flags, mount flags, `vp->v_resolve`, `vp->v_leases`, and per-mount trigger counts.

Major dependencies include `vnode_getattr()`, `vnode_cache_*`, `kauth_*`, `VNOP_OPEN/CLOSE/READDIR/IOCTL`, `unlink1()`, name cache locks, mount/vnode iteration, MACF trigger checks, kdebug tracing, knotes, UBC writable mapping checks, and IOKit entitlement checks.

## Risks and Edge Cases

- The chunk begins mid-function; correctness depends on initialization and `vnode_attr_authorize_internal()` just before this chunk.
- Namedstream authorization may switch `vp` to the parent vnode, so later reporting/cache behavior refers to the parent.
- `vnode_attr_authorize()` can panic if callers provide incomplete active/supported security attributes.
- `vnode_authattr_new_internal()` applies inherited flags in `out:` even after errors, so failed calls may still mutate `vap`.
- `vnode_authattr()` is not pure validation; it strips `SF_SYNTHETIC` and can mask setuid/setgid bits.
- AppleDouble directory scanning trusts filesystem-provided `d_reclen` and has HFS/NFS EOF workarounds.
- Trigger callbacks run outside locks and comments call out possible deadlock if callbacks access the trigger vnode.
- Trigger results with stale sequence numbers are ignored.
- `vfs_nested_trigger_unmounts()` is best-effort and stops on unresolve errors.
- File lease ownership treats same pid or same fileglob as owned by the caller.
- `wait_for_lease_break()` has suspicious logic equivalent to `error != EWOULDBLOCK`, treating unexpected `msleep()` errors like normal wakeups.
- `vnode_breaklease()` can call `vnode_getattr()` via `is_dataless_file()` while holding the vnode lock.
- `vnode_hasmultipath()` caches negative hardlink state with `VE_NOT_HARDLINK`; later link changes must invalidate that elsewhere.

## Cross-Chunk References

- Previous lines define the fast authorization cache path and `vnode_attr_authorize_internal()`, called here at lines 10395 and 10548.
- Earlier create-preparation code calls `vnode_authattr_new_internal()` around line 8179.
- Earlier wrappers call `vnode_authorize()` for delete, rename, extended attributes, and directory operations; this chunk completes the slow authorization path.
- `rmdir_remove_orphaned_appleDouble()` is declared near the file top and implemented here; its caller is outside this range.
- Trigger lifecycle cleanup is only partially visible here; vnode reclaim/detach callers outside this chunk must invoke resolver detach after draining.
- File lease structs/flags are defined outside this range; this chunk owns the vnode-side lease state machine.