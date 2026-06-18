# Group Research: group_1868_xfsdump_sources_local_fs_xfsdump_restore_getopt_h_sources_local_fs__8b53e49c5165

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/restore/getopt.h -->
# File Research: sources/local-fs/xfsdump/restore/getopt.h

## Summary
Centralizes the xfsrestore/xfsdump command-line option string and symbolic option-character names so modules that parse their own options use a consistent `getopt(3)` specification.

## Main Contents
- Defines `GETOPT_CMDSTRING` with the complete option set, including option letters that require arguments.
- Maps option characters to descriptive macros such as `GETOPT_WORKSPACE`, `GETOPT_DUMPDEST`, `GETOPT_SUBTREE`, `GETOPT_TOC`, `GETOPT_FORCE`, `GETOPT_FMT2COMPAT`, and `GETOPT_RINGLEN`.
- Documents which subsystem consumes many options, usually `content.c`, `drive.c`, `global.c`, `media.c`, or `getopt.c`.
- Reserves or notes unused letters and platform-specific history.

## Risks
The command string and per-option macros must stay synchronized. A macro added without the matching command-string entry, or vice versa, will make module-local parsing disagree.

This header encodes shared CLI ABI. Scripts and users may depend on these exact option letters and argument requirements.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/restore/getopt.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/restore/inomap.c -->
# File Research: sources/local-fs/xfsdump/restore/inomap.c

## Summary
Implements the restore-side inode map abstraction. It restores the on-media inode map into a housekeeping file, maps it into memory, tracks restore-needed state for non-directories, and offers range queries and iteration over inode states.

## Main Responsibilities
- Restore serialized inode-map hunks from media into the persistent `inomap` housekeeping file.
- Reopen and mmap an existing persistent inode map during resume or later restore phases.
- Store inode state in 64-inode segments with three bitplanes, supporting the `MAP_*` states from `inomap.h`.
- Mark selected non-directory inodes as restore-needed or no-restore for subtree restores.
- Answer whether any inode in an inclusive range still needs restore.
- Iterate all inodes whose state is included in a caller-supplied state mask.
- Discard inode-map bytes from media when a restore path does not need to persist them.

## Important Behavior
`inomap_restore_pers()` takes hunk count, segment count, and last inode from `content_inode_hdr_t`, creates `hkdir/inomap`, mmaps enough space, reads all hunks from the drive, translates each hunk with `xlate_hnk()`, unmaps/closes, and calls `inomap_sync_pers()`.

`inomap_sync_pers()` opens an existing `inomap`, mmaps the persistent header, then mmaps the hunk array separately. It rebuilds `nextp` pointers because persisted pointer values are not valid across process mappings.

`SEG_SET_BITS()` and `SEG_GET_BITS()` encode one 3-bit state per inode by setting or reading the low, middle, and high bitplanes in a segment.

`inomap_sanitize()` converts every `MAP_NDR_CHANGE` entry to `MAP_NDR_NOREST`, which makes later subtree selection explicitly opt non-directories back into restore.

`inomap_rst_add()` and `inomap_rst_del()` mutate a single inode between `MAP_NDR_CHANGE` and `MAP_NDR_NOREST`.

`inomap_rst_needed()` scans mapped hunks and segments to see if any inode in a requested range is `MAP_NDR_CHANGE`.

`map_getsegment()` uses binary search over the mmapped hunk array and then over a hunk’s segment array, relying on sorted, contiguous hunk storage.

## Dependencies
Depends on xfsdump media/content headers, drive read callbacks, `read_buf()`, `open_pathalloc()`, `mmap_autogrow()`, `arch_xlate`, XFS inode types, logging, and the global page-size-derived `perssz`.

## Risks
`map_getsegment()` uses unsigned `min`/`max` values with `max >= min` loops. If a search underflows `max`, the loop can misbehave; this is especially sensitive for inode values before the first hunk or segment.

`inomap_discard()` reads `tmphnkcnt` from the supplied media header but asserts the byte count against global `hnkcnt`, which may be stale or unrelated if no map was restored first.

Most corruption handling depends on assertions after reads and mmap sizing. Release builds with assertions disabled may continue after inconsistent metadata.

The persistent hunk array is trusted to be sorted and structurally valid; bad media could make binary search, `lastsegp`, or iteration assumptions unsafe.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/restore/inomap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/restore/inomap.h -->
# File Research: sources/local-fs/xfsdump/restore/inomap.h

## Summary
Defines restore inode-map states, the persistent segment/hunk layout, and the public restore-side inode-map API.

## Main Contents
- `MAP_INO_UNUSED`, directory/non-directory changed and unchanged states, subtree-support state, and `MAP_NDR_NOREST`.
- `seg_t`, representing 64 inodes starting at `base` with three 64-bit bitmaps.
- `hnk_t`, a 4-page chunk containing many segments, a `maxino`, and a transient linked-list pointer.
- `INOPERSEG`, `HNKSZ`, and `SEGPERHNK` sizing macros.
- APIs to restore, sync, delete, sanitize, query, mutate, discard, and iterate inode maps.

## Risks
The persistent layout is ABI-sensitive because map hunks are serialized on dump media and stored in housekeeping files.

`hnk_t` includes a pointer that must be reconstructed after mmap; persisted pointer values are intentionally not portable.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/restore/inomap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/restore/mmap.c -->
# File Research: sources/local-fs/xfsdump/restore/mmap.c

## Summary
Provides `mmap_autogrow()`, a Linux replacement for IRIX-style `MAP_AUTOGROW` behavior. It extends a backing file before mapping so the requested shared writable mapping is accessible.

## Main Responsibilities
- `fstat()` the target file.
- If the file is smaller than `offset + len`, seek to the last required byte and write one NUL byte.
- Call `mmap()` with `PROT_READ | PROT_WRITE` and `MAP_SHARED`.

## Dependencies
Depends on POSIX `fstat`, `lseek`, `write`, and `mmap`.

## Risks
The `lseek()` and `write()` calls used to extend the file are not checked. If either fails, the subsequent `mmap()` may fail or map a file smaller than expected.

`offset + len` is not overflow-checked.

The function always requests read/write shared mappings; it is not a general-purpose mmap wrapper.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/restore/mmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/restore/mmap.h -->
# File Research: sources/local-fs/xfsdump/restore/mmap.h

## Summary
Declares the restore helper `mmap_autogrow()`.

## Interface
`void *mmap_autogrow(size_t len, int fd, off_t offset);`

The caller provides a byte length, backing file descriptor, and mapping offset. Return semantics follow `mmap()`: a valid pointer or `MAP_FAILED`.

## Risks
The header does not include the system types needed for `size_t` and `off_t`; callers must include suitable system headers first.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/restore/mmap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/restore/namreg.c -->
# File Research: sources/local-fs/xfsdump/restore/namreg.c

## Summary
Implements the restore name registry. It stores directory-entry names in a persistent housekeeping file and returns compact offset handles used by tree nodes.

## Main Responsibilities
- Create or reopen the `namreg` housekeeping file.
- Store persistent append offset in the first page.
- Append names as one-byte length plus raw name bytes.
- Buffer append writes for performance.
- Resolve a name handle back to a NUL-terminated name.
- Optionally mmap the name payload area for faster lookups after all names have been added.

## Important Behavior
`namreg_init()` creates a prefilled file sized from `inocnt * NAMREG_AVGLEN` for new restores, or reopens an existing file for resume. It mmaps the first page as `namreg_pers_t`.

`namreg_add()` flushes/seeks to append position when needed, buffers one length byte plus the name, advances `np_appendoff`, and returns the previous file offset as the handle.

`namreg_flush()` writes the buffered name data to disk and resets the in-memory buffer offset.

`namreg_get()` converts the handle to a file offset, then either indexes the mmapped name area or seeks and reads up to 256 bytes into a static buffer. It copies the name into the caller buffer and NUL-terminates it.

`namreg_map()` flushes pending names and mmaps the payload region after the persistent page; if mapping fails, it falls back to seek/read lookup.

`namreg_del()` is intentionally unimplemented; the registry grows for the life of the restore state.

## Dependencies
Depends on `open_pathalloc()`, `create_filled_file()`, `mmap_autogrow()`, xfsdump locking, logging, page-size globals, and optional `NAMREGCHK` handle check bits.

## Risks
Names are limited to 255 bytes by assertion. A release build with assertions disabled would still store the length in one byte and truncate modulo 256.

`namreg_get()` reads the stored length through `char`; on platforms where `char` is signed, lengths above 127 can become negative before conversion to `size_t`.

The static read buffer is protected by the global `lock()`, but the mmap lookup path still shares global registry state and is not independently reentrant.

Deletion is a no-op, so long or repeated restores accumulate dead name records in the housekeeping file.

Short reads in `namreg_get()` are accepted as long as `read()` returns positive; the code does not verify that the full length byte plus name was read before copying.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/restore/namreg.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/restore/namreg.h -->
# File Research: sources/local-fs/xfsdump/restore/namreg.h

## Summary
Declares the directory-entry name registry API used by the restore tree.

## Main Contents
- `nrh_t` as a 64-bit name-registry handle.
- `NRH_NULL` sentinel.
- `namreg_init()` for creating or resyncing the registry.
- `namreg_add()` to register a non-NUL-terminated name.
- `namreg_del()` to remove a handle, though the implementation is currently a no-op.
- `namreg_map()` to switch to mmap-backed lookups.
- `namreg_get()` to resolve a handle into a caller buffer.

## Risks
The API exposes integer handles that are persistent file offsets; callers must not invent or reuse handles after deletion.

`namreg_get()` has multiple negative error returns, so callers must distinguish short buffer, missing handle, and syscall failure if they want precise recovery.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/restore/namreg.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/restore/node.c -->
# File Research: sources/local-fs/xfsdump/restore/node.c

## Summary
Implements a persistent, mmap-windowed node allocator used by the restore tree. Nodes are addressed by 32-bit handles and stored in segments inside a housekeeping file.

## Main Responsibilities
- Initialize or resync persistent node allocator metadata.
- Choose segment size, nodes-per-segment, and window count from node size, alignment, estimated inode count, and virtual memory budget.
- Allocate nodes from a free list or a virgin node counter.
- Map node handles to memory through the `win` abstraction.
- Free nodes back to a singly-linked free list.
- Optionally validate handles and node state when compiled with `NODECHK`.

## Important Behavior
`node_init()` rounds user node size up to alignment, picks a power-of-two `nodesperseg`, ensures at least `WINMAP_MIN` windows can fit in available virtual memory, mmaps the allocator header, initializes persistent fields, and calls `win_init()`.

`node_sync()` mmaps an existing node header and reinitializes the window abstraction using persisted segment parameters.

`node_alloc()` first reuses `nh_freenh` if available. Otherwise it takes `nh_virgnh`, pre-grows a new segment with `ftruncate64()` when entering a segment, and returns the handle unless it exceeds `NH_MAX`.

`node_map()` uses bit shifts and masks to split a handle into segment index and node index, then delegates segment mapping to `win_map()`.

`node_free()` writes the old free-list head into the freed node’s first word, updates `nh_freenh`, unmaps the node, and clears the caller’s handle.

## Dependencies
Depends on page-size globals, `mmap_autogrow()`, `win`, xfsdump types/logging, and optional `NODECHK` validation macros.

## Risks
The allocator uses the beginning of each node for free-list linkage and requires the caller to reserve a housekeeping byte; callers must honor the layout constraints passed to `node_init()`.

A failed segment `ftruncate64()` is logged as a warning but allocation continues, relying on later mmap/autogrow behavior.

Most structural errors are assertions. With assertions disabled, stale handles or corrupted persistent state could cause wrong mappings or list corruption.

Handle capacity is capped by `nh_t`; very large restores can return `NH_NULL` when node count exceeds `NH_MAX`.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/restore/node.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/restore/node.h -->
# File Research: sources/local-fs/xfsdump/restore/node.h

## Summary
Declares the persistent node pool abstraction used by restore tree code.

## Main Contents
- `nh_t` as a 32-bit node handle and `NH_NULL` sentinel.
- `node_init()` for creating a node pool inside an existing backing file.
- `node_sync()` for reconnecting to persisted node state.
- `node_alloc()`, `node_map()`, `node_unmap()`, and `node_free()`.

## Risks
Mapped node pointers are valid only until `node_unmap()` and may pin scarce windows while held.

Callers must pass a node size, alignment, and housekeeping-byte index compatible with `node.c`’s internal free-list and validation requirements.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/restore/node.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/restore/tree.c -->
# File Research: sources/local-fs/xfsdump/restore/tree.c

## Summary
Implements xfsrestore’s persistent directory tree model. It ingests dumped directories and entries, tracks hard links and subtree selections, resolves paths, creates/removes/renames directories, drives non-directory restore callbacks, restores directory metadata, and manages the restore orphanage.

## Main Responsibilities
- Create or resync the `tree` housekeeping file.
- Allocate persistent tree nodes through `node.c` and index them by inode/generation through a persistent hash array.
- Maintain parent/child/sibling relationships and hard-link lists.
- Track node state with flags for real filesystem objects, selected subtrees, references, written files, directories, dumped directories, and new orphans.
- Build and maintain an `orphanage` directory under the restore destination.
- Apply directory dump records through `tree_begindir()` and `tree_addent()`.
- Post-process restored directory state by removing unreferenced entries, creating missing directories, renaming directories, and processing hard links.
- Select subtrees from command-line paths or interactive commands and synchronize selection with `inomap`.
- Walk hard-link lists to invoke file restore/link callbacks.
- Restore directory attributes, timestamps, ownership, mode, and XFS project/extent flags.
- Provide optional tree consistency checks under `TREE_CHK`.

## Core State
`treepers_t` persists root inode, root node handle, orphanage node handle, hash sizing, restore ownership/full-dump flags, orphan-handling mode, and generation-number compatibility mode.

`tran_t` stores transient restore context: housekeeping and destination paths, orphanage path, destination-XFS flag, persistent fd, mapped hash array, temporary name buffer, and interactive dialog state.

Each `node_t` represents a directory entry or hard-link entry with inode, name-registry handle, directory-attribute handle, hash link, parent/sibling/child links, hard-link link, generation, and flags.

## Important Behavior
`tree_init()` creates the orphanage directory, creates and maps the persistent tree file, initializes the hash and node abstractions, creates root and orphanage nodes, links them into the hash, and adopts orphanage under root.

`tree_sync()` reopens persisted tree state, recreates the orphanage if needed, remaps the hash and node abstractions, and updates the current full-dump mode.

`tree_check_dump_format()` prevents applying old format-2 generation-number dumps after a restore has already begun in format-3-or-newer mode unless compatibility truncation was enabled from the start.

`tree_begindir()` handles a directory header. It finds an existing hard-link head by inode/generation, upgrades prior non-directory placeholders to directories, refreshes directory attributes, or creates new orphaned directory nodes until a parent entry adopts them.

`tree_addent()` handles directory entries. It updates existing directories, records pending directory renames in `n_lnkh`, retains or creates non-directory hard-link nodes, reserves the root-level `orphanage` name, and marks referenced entries.

`tree_post()` runs the post-directory pass: remove or orphan unreferenced entries for incremental restores, create missing directories, rename directories out of orphanage, and process hard links.

`tree_cb_links()` is called for each non-directory inode. It resolves all selected hard-link paths, enforces overwrite policy, unlinks stale existing files before restore when needed, invokes the caller callback to restore the first path and link later paths, and creates orphanage entries for unreferenced file data.

`tree_adjref()` propagates reference state through unchanged-but-referenced directories, based on whether parent directories were dumped.

`tree_subtree_parse()`, `tree_markallsubtree()`, `selsubtree()`, and `selsubtree_recurse_down()` manage selected restore subtrees and update `inomap` for non-directory restore inclusion.

`tree_subtree_inter()` implements the interactive selector with `pwd`, `ls`, `cd`, `add`, `delete`, `extract`, `quit`, and `help` commands.

`Node2path()` recursively builds restore paths from parent links. Nodes under orphanage are named as `ino.gen`; the orphanage node itself is named `orphanage`.

`setdirattr()` restores times, mode, optional owner/group, and XFS-specific `fsxattr` values using handle APIs when the destination is XFS.

`hash_*()` implements a power-of-two inode hash table whose entries point to hard-link-list heads. `link_*()` layers hard-link list operations on top of that hash.

`parse()` is a small shell-like tokenizer for the interactive dialog, supporting quotes, backslash escapes, hex/octal escapes, and whitespace collapsing.

## Dependencies
Depends on restore content and inode headers, `inomap`, `namreg`, `dirattr`, `node`, `bag`, dialog/logging/control helpers, path/open utilities, XFS handle and ioctl APIs, POSIX filesystem operations, and global restore policy such as `restore_rootdir_permissions` and `need_fixrootdir`.

## Risks
This file is the restore metadata coordinator; corruption in node links, hash entries, name handles, or directory-attribute handles can affect deletion, rename, hard-link creation, and final path resolution.

Many invariants are enforced by assertions, including node relationships, name handles, generation handling, and tree layout. Release builds may not stop on malformed state.

`Node2path_recurse()` uses recursion and a thread-local parent-path cache. Very deep directory trees risk recursion depth and pathname-length failures.

The orphanage is a real directory named `orphanage` in the destination root, so the code reserves that name and warns or fails when it collides with existing user content.

Incremental restore behavior is complex: unreferenced real entries may be unlinked, renamed into orphanage, retained, or used as hard-link sources depending on flags and hard-link lists.

`setdirattr()` may attempt XFS-specific handle operations and later use `fd` for `XFS_IOC_FSSETXATTR`; failures are logged, but metadata restoration may be partial.

The interactive parser mutates its input buffer in place and uses custom escape handling, so command parsing is not equivalent to a full shell parser.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/restore/tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/restore/tree.h -->
# File Research: sources/local-fs/xfsdump/restore/tree.h

## Summary
Declares the restore directory-tree API used by content restore code.

## Main Contents
- Initialization and resume: `tree_init()`, `tree_sync()`, `tree_check_dump_format()`.
- Root workaround: `tree_fixroot()`.
- Directory ingest: `tree_begindir()`, `tree_addent()`, `tree_enddir()`.
- Selection: `tree_markallsubtree()`, `tree_subtree_parse()`, `tree_subtree_inter()`.
- Post-processing: `tree_marknoref()`, `tree_adjref()`, `tree_post()`, `tree_delorph()`.
- Non-directory restore traversal: `tree_cb_links()`.
- Directory metadata/extattr traversal: `tree_setattr()`, `tree_extattr()`.
- Optional `tree_chk()` sanity check when `TREE_CHK` is enabled.

## Risks
The interface exposes a multi-phase protocol. Callers must initialize/sync, ingest directories, adjust references, post-process, restore files, and set attributes in the intended order.

Many functions assume the global persistent tree context exists; the header does not encode those lifecycle preconditions.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/restore/tree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/restore/win.c -->
# File Research: sources/local-fs/xfsdump/restore/win.c

## Summary
Implements an mmap window cache over a large file. It maps fixed-size file segments on demand, reference-counts them, and reuses idle windows through an LRU list.

## Main Responsibilities
- Initialize windowing over a backing fd, first file offset, segment size, and maximum window count.
- Map a segment index to a memory pointer, reusing existing mappings when possible.
- Unmap caller references and move idle windows onto an LRU list.
- Grow the segment-index-to-window map as new segment indexes are requested.
- Allow locking to be disabled during single-threaded tree reconstruction phases.
- Report how many mmap calls were made.

## Important Behavior
`win_init()` validates page alignment, allocates transient state, initializes the segment map, and allocates a qlock.

`win_map()` checks the segment map first. If the segment is already mapped, it removes an idle window from the LRU list if needed and increments the reference count. Otherwise it allocates a new window descriptor until `t_winmax`, or reuses the LRU head by `munmap()`ing the old segment.

`win_map()` calls `mmap_autogrow()` for the target segment and returns `NULL` if no window is available or mapping fails.

`win_unmap()` validates the pointer belongs to the mapped segment, decrements the reference count, adds newly idle windows to the LRU tail, and clears the caller’s pointer.

`win_locks_off()` and `win_locks_on()` bypass the qlock for phases known to be single-threaded.

## Dependencies
Depends on `qlock`, xfsdump logging/types, page-size globals, and `mmap_autogrow()`.

## Risks
There is one global `tranp`; the abstraction is not designed for multiple independent window caches in one process.

If all windows are referenced, mapping another segment fails and callers must handle a `NULL` pointer.

Mapping failure decrements `t_winmax`, which can permanently reduce mapping capacity for the process.

Correctness relies on every caller balancing `win_map()` with `win_unmap()`; leaked references prevent LRU reuse.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/restore/win.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/restore/win.h -->
# File Research: sources/local-fs/xfsdump/restore/win.h

## Summary
Declares the mmap window abstraction used by the node allocator.

## Main Contents
- `segix_t` segment index type.
- `win_init()` to configure windowing over a file range.
- `win_map()` and `win_unmap()` for segment mapping and pointer invalidation.
- `win_locks_off()` and `win_locks_on()` for single-threaded phases.
- `win_getnum_mmaps()` for diagnostics.

## Risks
The API returns raw pointers and requires strict map/unmap pairing.

The lock toggle is global and assumes the caller can guarantee single-threaded access while locks are disabled.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/restore/win.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/tools/git-contributors.py -->
# File Research: sources/local-fs/xfsdump/tools/git-contributors.py

## Summary
Python helper that extracts contributor email addresses from git commit logs for a supplied revision spec.

## Main Responsibilities
- Run `git log --pretty=medium <revspec>`.
- Parse trailer-like lines such as `Signed-off-by`, `Acked-by`, `Cc`, `Reviewed-by`, `Reported-by`, `Tested-by`, `Suggested-by`, and `Reported-and-tested-by`.
- Extract email addresses using `email.utils.parseaddr()`.
- Handle some malformed or kernel-style `Cc:` annotations.
- Print a sorted unique address list with a configurable separator.

## Important Behavior
`backtick()` is a generator over subprocess stdout lines.

`find_developers.__init__()` compiles regexes for known tags, comma-separated address detection, and fallback angle-bracket extraction.

`_handle_addr()` strips everything after `#` to work around common kernel stable-CC annotations, uses `parseaddr()`, falls back to text inside angle brackets, and finally returns the raw string.

`run()` scans lines for known tags, splits likely multi-address lines on commas, normalizes each address, and returns `sorted(set(addr_list))`.

`main()` parses `revspec`, `--separator`, and hidden `--debug`, runs the extractor over git log output, prints contributors, and exits zero.

## Dependencies
Depends on Python 3 standard library modules `argparse`, `email.utils`, `io`, `re`, `subprocess`, and `sys`, plus a working `git` executable in the target repository.

## Risks
Comma splitting is heuristic and can mishandle quoted display names containing commas unless the fallback angle-bracket regex saves the address.

`backtick()` does not check the git subprocess return code, so invalid revisions may produce an empty list without a nonzero script exit.

Stripping at `#` can corrupt a technically valid address or display name containing `#`, intentionally favoring common kernel trailer conventions.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/tools/git-contributors.py -->