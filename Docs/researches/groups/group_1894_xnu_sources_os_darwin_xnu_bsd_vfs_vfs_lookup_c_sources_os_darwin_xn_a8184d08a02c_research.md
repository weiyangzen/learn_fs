# Group Research: group_1894_xnu_sources_os_darwin_xnu_bsd_vfs_vfs_lookup_c_sources_os_darwin_xn_a8184d08a02c

Scope: `Docs/research_subset_a.md`, source tree `sources/os/darwin/xnu`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_lookup.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_lookup.c

Implements Darwin/XNU pathname resolution: `namei`, component lookup, symlink expansion, mountpoint traversal, resource-fork lookup, legacy volfs path translation, relookup, and lookup tracing.

Key behavior:
- `namei` copies user or kernel pathnames into the embedded path buffer, grows to allocated `MAXPATHLEN`/`MAXLONGPATHLEN` buffers when supported, recognizes `/.nofollow/` and `/.resolve/<flags>/` prefixes, sets `NAMEI_*` policy flags, selects root/current/used starting directories, pins root/start vnodes with usecounts, and drives `lookup` until the path completes or a symlink is expanded.
- Resolve-prefix handling maps userspace policy bits into lookup constraints such as no symlinks, no `..`, local-only mounts, no devfs, immovable media only, unique-path requirements, and no xattrs/named streams.
- `lookup` walks path components using `cache_lookup_path` first, authorizes directory search, handles `.`/`..`, chroot boundaries, `NAMEI_RESOLVE_BENEATH`, `NAMEI_NODOTDOT`, read-only mutation checks, mount crossing, union mounts, compound open handoff, and final parent/leaf iocount ownership.
- Cache and identity maintenance are centralized in `lookup_consider_update_cache`, which updates vnode name/parent identity and enters cache records only when flags, vnode cacheability, non-dot names, and directory generation checks permit it.
- `lookup_handle_found_vnode` consumes filesystem-provided extra path bytes, traverses mountpoints, labels multi-label MAC vnodes, detects symlinks, rejects invalid trailing slashes, hides shadow files from ordinary lookup, audits successful paths, and optionally redirects to named resource-fork lookup.
- `lookup_traverse_mountpoints` follows stacked mounts by acquiring mount crossrefs, honoring forced-unmount/nonblocking behavior, enforcing resolve policies against network, devfs, and removable filesystems, resolving trigger vnodes, and caching the real root vnode/generation after traversal.
- `lookup_handle_symlink` reads link text with `VNOP_READLINK`, enforces `MAXSYMLINKS`, validates combined path length, splices link text with remaining suffix, restarts at root for absolute links, and blocks absolute symlink escapes under `NAMEI_RESOLVE_BENEATH`.
- `lookup_handle_rsrc_fork` maps `/..namedfork/rsrc` style requests to `vnode_getnamedstream`, requiring explicit `CN_ALLOWRSRCFORK` authorization and preserving audit path suffixes.
- Volfs compatibility resolves `/.vol/<fsid>/<ino>[/tail]` through `vfs_getrealpath`, `mount_lookupby_volfsid`, `VFS_ROOT`/`VFS_VGET`, chroot containment checks, and `build_path`, with bounded restart on `ENOENT`.
- `relookup` provides a single-component reacquire helper used after prior lookup state, while `nameidone` frees allocated pathname buffers.
- Kdebug helpers encode lookup path bytes across one or more trace events, and `lookup_compound_vnop_post_hook` mirrors audit/cache/trace side effects after compound VNOPs.

Dependencies:
- Uses vnode, mount, namecache, `VNOP_LOOKUP`, `VNOP_READLINK`, `VFS_ROOT`, `VFS_VGET`, audit, MACF, kdebug, trigger, union mount, named-stream, and volfs infrastructure.
- Depends on `struct nameidata`, `struct componentname`, vnode iocount/usecount rules, process root/cwd state, and `rootvnode_rw_lock`.

Research notes:
- This file is the VFS namespace policy choke point for Darwin path lookup. It combines correctness-sensitive lifetime handling with security policy flags and filesystem callbacks.
- The code carefully distinguishes iocounts from usecounts, especially around root/start directories and symlink restarts.
- Several behaviors are compile-time optional (`CONFIG_VOLFS`, `CONFIG_TRIGGERS`, `CONFIG_UNION_MOUNTS`, `NAMEDRSRCFORK`, `NAMEDSTREAMS`, `CONFIG_MACF`) and should be considered when comparing XNU builds.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_quota.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_quota.c

Implements Darwin/XNU generic quota-file and in-core dquot management: global dquot hash initialization, dquot lookup/allocation/reclaim, quota-file open/close synchronization, disk record lookup, dirty orphan sync, and user/kernel quota-structure conversion.

Key behavior:
- Defines global dquot cache state: hash table keyed by quota vnode and id, desired/actual dquot counts, free list, dirty orphan list, quota magic values, typed dquot allocator, and quota list/file locks.
- `dqhashinit` lazily initializes the dquot freelist, dirty list, and hash table under the quota list mutex; `dqisinitialized` reports readiness.
- Quota list locking tracks a mutation counter so lookup paths can detect that `dq_lock_internal` slept and invalidated assumptions.
- `dq_lock_internal` and `dq_unlock_internal` implement per-dquot logical locking with `DQ_LLOCK`/`DQ_LWANT` while coordinated by the global quota list mutex.
- `qf_get`/`qf_put` serialize quota-file opening and closing with `QTF_OPENING`, `QTF_CLOSING`, `QTF_WANTED`, vnode presence checks, refcount drain, sleeps, and wakeups.
- `qf_ref` and `qf_rele` protect quota files from `quota_off` while `dqget` may read or modify quota-file contents.
- `dqfileopen` validates quota file size/header, checks magic/version/maxentries, initializes grace periods, entry count, max entries, and hash-shift constants.
- `dqfileclose` rereads the quota-file header and writes back the current entry count using big-endian on-disk format.
- `dqget` first searches the in-core hash, removes cache hits from free/dirty lists when refcount rises from zero, otherwise allocates or recycles dquots under target limits, rechecks after sleeps/allocations, inserts the new dquot into the hash before disk initialization, and backs out cleanly on `dqlookup` failure.
- `dqlookup` performs open-addressed probing inside the quota file using `dqhash1`/`dqhash2`, reserves empty entries by writing a new id, increments file entry count, and converts existing big-endian `dqblk` records to host-endian fields.
- `dqrele` syncs modified dquots before returning them to the free list; `dqreclaim` avoids I/O and places modified zero-ref dquots on the dirty orphan list.
- `dqsync_orphans`, `dqsync`, and `dqsync_locked` flush modified dquot records back to their quota file, handling endian conversion and short-write detection.
- `dqflush` detaches all cached dquots associated with a quota vnode once they are unused.
- `munge_dqblk` converts between kernel `dqblk` and 64-bit user `user_dqblk`, with noted precision loss for time fields in one direction.

Dependencies:
- Uses vnode I/O (`VNOP_READ`, `VNOP_WRITE`, `vnode_size`), `uio` stack buffers, XNU locks/sleeps/wakeups, quota format definitions from `sys/quota.h`, byte swapping from `libkern/OSByteOrder.h`, and hash/list queue macros.

Research notes:
- The dquot cache is race-aware: many paths intentionally relookup after any operation that might sleep while the global lock is dropped.
- On-disk quota records are big-endian and probed by a quota-file-specific hash table, not by sequential scanning.
- Dirty dquots can become orphans when reclaimed without I/O, and the orphan list exists to flush them later for a particular quota file.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_support.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_support.c

Provides default vnode operation implementations for filesystems that do not supply every VNOP. Most `nop_*` routines report success with minimal side effects, while corresponding `err_*` routines generally return `ENOTSUP` after any necessary cleanup/default behavior.

Key behavior:
- Defines local argument-struct declarations matching generated VNOP interfaces, then implements default/error handlers for create, whiteout, mknod, open, close, access, getattr, setattr, read, write, ioctl, select, exchange, revoke, mmap, fsync, remove, link, rename, mkdir, rmdir, symlink, readdir, readdirattr, readlink, inactive, reclaim, strategy, pathconf, advlock, allocate, bwrite, pagein, pageout, searchfs, copyfile, block translation, blockmap, and monitor.
- Diagnostic `nop_create`, `nop_mknod`, and `nop_symlink` assert that the component name owns a pathname buffer when expected.
- Most `nop_*` operations simply return `0`; most `err_*` operations return `ENOTSUP`, sometimes after invoking the matching `nop_*` to preserve side effects.
- `nop_revoke` delegates to `vn_revoke`; `err_revoke` performs that default revoke path before reporting unsupported.
- `nop_readdirattr` sets actual count and EOF flag to zero; `err_readdirattr` preserves those output initializations before returning unsupported.
- `nop_allocate` reports zero bytes allocated; `err_allocate` preserves that output value before returning unsupported.
- `nop_bwrite` delegates to `buf_bwrite`, while `err_bwrite` returns unsupported.
- `nop_pagein`, `err_pagein`, `nop_pageout`, and `err_pageout` abort UPL ranges with error/free-on-empty semantics unless `UPL_NOCOMMIT` is set, then return `EINVAL` or `ENOTSUP`.
- `nop_searchfs` reports zero matches; block translation defaults store `(off_t)-1` or `(daddr64_t)-1` sentinel failure values.

Dependencies:
- Exposed by `vfs/vfs_support.h`; uses vnode interface argument types from `sys/vnode_if.h`, authorization types, `vn_revoke`, buffer write support, and UBC UPL abort routines.

Research notes:
- This file is fallback glue for vnode operation vectors. Its main importance is side-effect correctness, especially for UPL cleanup and output-parameter initialization.
- The `err_*` wrappers are not always pure error returns; callers relying on output values or cleanup must account for the paired `nop_*` behavior.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_support.c -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_support.h -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_support.h

Declares the default and error vnode operation helpers implemented by `vfs_support.c`.

Key behavior:
- Provides include guards and pulls in kernel/VFS headers needed for vnode operation argument types.
- Wraps declarations in `__BEGIN_DECLS`/`__END_DECLS` for C++ compatibility.
- Declares paired `nop_*` and `err_*` functions for vnode operations including namespace mutation, open/close, metadata, I/O, locking, directory enumeration, lifecycle, paging, search, copyfile, block mapping, and monitoring.
- Function declarations mirror the generated `struct vnop_*_args` interfaces consumed by vnode operation vectors.

Dependencies:
- Includes `sys/param.h`, `sys/systm.h`, `sys/kernel.h`, `sys/file.h`, `sys/stat.h`, `sys/proc.h`, `sys/conf.h`, `sys/mount.h`, `sys/vnode.h`, `sys/vnode_if.h`, `sys/malloc.h`, and `sys/dirent.h`.

Research notes:
- This header is the public declaration surface for filesystem fallback VNOP routines.
- It intentionally contains prototypes only; behavior is in `vfs_support.c`.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_support.h -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_unicode.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_unicode.c

Implements XNU UTF-8 normalization, optional case folding, comparison, hashing, UTF-32/UTF-8 conversion, and substring matching for filesystem names and paths using generated Unicode trie data.

Key behavior:
- Reports Unicode normalization/casefold data version `16.0.0` with code revision `0`.
- `utf8_normalizeOptCaseFoldAndHash` streams an input UTF-8 filename into normalized UTF-32 buffers, optionally case-folds, canonical-orders combining marks, rejects NUL and slash, and feeds normalized code units to a caller-supplied hash function.
- `utf8_normalizeOptCaseFoldAndCompare` normalizes two UTF-8 strings in parallel, reorders combining marks independently, compares buffer chunks, supports early non-equal returns, and includes special pushback handling for Greek iota case-folding at buffer boundaries.
- `utf8_normalizeOptCaseFold` converts a UTF-8 string to normalized UTF-32 output, returning `ENOMEM` when the caller buffer cannot hold the result.
- `utf8_normalizeOptCaseFoldToUTF8_internal` normalizes and optionally case-folds, then converts normalized UTF-32 code points back to UTF-8; the public filename variant rejects slash, while the path variant allows slash but still rejects NUL.
- `utf8_normalizeOptCaseFoldAndMatchSubstring` searches for an already-normalized UTF-32 substring inside a UTF-8 source after on-demand normalization into caller-provided workspace, avoiding normalization when the substring is clearly too long.
- `nextBaseAndAnyMarks` is the shared streaming engine: it decodes ASCII fast paths, validates illegal ASCII characters, decodes non-ASCII UTF-8, normalizes/case-folds each code point, accumulates a base plus following combining marks, enforces stream-safe buffer limits, and flags when canonical reordering is needed.
- `doReorder` performs simple combining-class bubble sort with `swapBufCharCCWithPrevious`.
- `u32CharToUTF8Bytes` encodes valid Unicode code points into one to four UTF-8 bytes.
- `utf8ToU32Code` validates and decodes UTF-8 sequences using ICU-derived lead/trail logic, rejects overlong forms, malformed trails, surrogate mappings, out-of-range code points, and illegal lead-byte lengths.
- `normalizeOptCaseFoldU32Char` maps one UTF-32 code point through generated normalization/case-fold trie tables, rejects unassigned/invalid/noncharacter ranges, handles high private-use area, algorithmic Hangul decomposition, direct combining-class flags, invalid masks, UTF-16/UTF-32 decomposition sequence tables, and case-fold-only mappings.
- `adjustCase` applies simple case folding and the U+0345-to-U+03B9 special case when case-insensitive behavior is requested.
- `getCombClassU32Char` retrieves combining classes for decomposition expansion tail characters, including special treatment for U+03B9 as folded U+0345.
- `decomposeHangul` decomposes precomposed Hangul syllables into leading, vowel, and optional trailing Jamo code points.

Dependencies:
- Includes `sys/unicode.h` and generated `vfs_unicode_data.h` tables such as `nfTrieHi`, `nfTrieMid`, `nfTrieLo`, sequence tables, invalid masks, and simple case-fold tables.
- Logic is adapted from ICU UTF-8 and normalization behavior but implemented as kernel-local code with fixed stack buffers.

Research notes:
- The exported APIs are streaming and allocation-free from the caller perspective; callers provide hash callbacks, output buffers, or working memory.
- Filename-oriented functions reject `/`, while the explicit path normalization variant allows it. All variants reject embedded NUL.
- Error behavior can be intentionally partial: compare and substring APIs may return a definitive unequal/match result before later invalid bytes would have been decoded.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_unicode.c -->