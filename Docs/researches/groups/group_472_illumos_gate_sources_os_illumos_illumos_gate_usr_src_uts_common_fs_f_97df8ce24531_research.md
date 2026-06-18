# Group Research: group_472_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_f_97df8ce24531

Scope verified against `Docs/research_subset_a.md`. All twelve listed illumos source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fifofs/fifovnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fifofs/fifovnops.c

## Role

Implements FIFOFS vnode operations for STREAMS-backed FIFOs and pipes. It is the main VOP layer for opening, closing, reading, writing, polling, attributes, ACL delegation, and stream ioctl handling for `VFIFO` nodes.

## Main Behavior

- Defines `fifo_vnodeops_template`, wiring FIFOFS operations into illumos VFS: open, close, read, write, ioctl, getattr, setattr, access, create, fsync, inactive, fid, rwlock/rwunlock, seek, realvp, poll, pathconf, and security attribute operations.
- `fifo_open()` synchronizes reader and writer opens with `fn_rcnt`, `fn_wcnt`, `fn_rsynccnt`, `fn_wsynccnt`, `FIFOSYNC`, `FIFOROCR`, and `FIFOWOCR`. Blocking opens wait for the opposite end; nonblocking writer opens can fail with `ENXIO`.
- `fifo_close()` serializes open/close teardown with `flk_ocsync`, cleans locks/shares/STREAMS state, sends `M_HANGUP`, wakes sleeping peers, handles named pipe unmount via `nm_unmountall()`, and flushes fast-mode buffers.
- `fifo_read()` uses fast-mode in-memory message blocks when `FIFOFAST` is set, otherwise delegates to `strread()`. It handles EOF/no-writer cases, `FNDELAY`/`FNONBLOCK`, signal interruption, access time updates, and writer wakeups under high-water pressure.
- `fifo_write()` fast-paths writes into the peer fifonode’s message queue, enforces `Fifohiwat` flow control, splits oversized writes into `PIPE_BUF` chunks, wakes readers, updates mtime/ctime, and sends `SIGPIPE`/`EPIPE` when readers disappear.
- `fifo_fastioctl()` services selected ioctl operations without leaving fast mode, including `I_NREAD`, `FIORDCHK`, `I_PEEK`, `FIONREAD`, `I_FLUSH`, `I_CANPUT`, and `_I_GETPEERCRED`. Unsupported STREAMS-sensitive ioctls call `fifo_fastoff()` and fall back to `fifo_strioctl()`.
- `fifo_poll()` implements fast-mode readiness and hangup reporting, including `POLLET` registration via stream poll lists, and delegates to `strpoll()` in STREAMS mode.
- Attribute operations proxy to `fn_realvp` for named FIFOs and synthesize metadata for anonymous pipes.

## Important Details

- `tsol_fifo_access()` enforces Trusted Extensions cross-zone write policy for named FIFOs by comparing the caller zone with the FIFO’s zone path owner.
- Fast-mode/STREAMS-mode conversion is guarded by `FIFOSTAYFAST` and `FIFOWAITMODE` through `fifo_stayfast_enter()` and `fifo_stayfast_exit()`.
- `fifo_inactive()` coordinates vnode count removal with `ftable_lock`, removes real-vnode-backed FIFOs from the FIFO table, releases underlying vfs/vnode references, and frees pipe/fnode cache allocations when the shared lock refcount drops to zero.
- `fifo_fsync()` propagates newer FIFO access/modify times to the underlying real vnode before calling its `VOP_FSYNC`.
- `fifo_setsecattr()` manually locks the real vnode because FIFOFS itself does not implement functional rw locking.

## Dependencies And Interactions

- Depends on `sys/fs/fifonode.h`, STREAMS internals, namefs for mounted pipes, `fs_subr` fallbacks, Trusted Extensions labels/zones, and vnode/VFS infrastructure.
- Closely tied to external FIFO helpers such as `fifo_stropen()`, `fifo_fastoff()`, `fifo_fastflush()`, `fifo_wakewriter()`, and `fifo_wakereader()` defined elsewhere in fifofs.
- The implementation relies on careful shared `fifolock_t` state between paired pipe endpoints.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fifofs/fifovnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fs_reparse.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fs_reparse.h

## Role

Declares shared kernel/user interfaces and constants for illumos filesystem reparse-point support.

## Main Behavior

- Defines reparse marker tokens such as `FS_REPARSE_TAG_STR`, token delimiters, `MAXREPARSELEN`, and the reparsed door path `/var/run/reparsed_door`.
- Defines `REPARSED_DOORCALL_MAX_RETRY` and SMF service name `REPARSED`.
- Declares `reparsed_door_res_t`, the door response structure shared across 32-bit userland and 64-bit kernel code. Its `res_len` is explicitly `int` for ABI compatibility.

## API Surface

- Common nvlist helpers: `reparse_init()`, `reparse_free()`, `reparse_parse()`, and `reparse_validate()`.
- Kernel-only functions: `reparse_kderef()` and `reparse_vnode_parse()`.
- Userland-only functions: `reparse_add()`, `reparse_remove()`, `reparse_unparse()`, `reparse_create()`, `reparse_delete()`, and `reparse_deref()`.

## Dependencies And Interactions

- Uses kernel `sys/nvpair.h` under `_KERNEL` or `_FAKE_KERNEL`; uses `libnvpair.h` for userland.
- Implemented in part by `fs_subr.c` for kernel vnode parsing and door upcall dereferencing.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fs_reparse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fs_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fs_subr.c

## Role

Provides generic vnode/VFS helper routines used by many filesystems: default operation stubs, locking/share wrappers, pathconf defaults, ACL fabrication, reparse-point kernel helpers, antivirus hook registration, and global pseudo-vfs construction.

## Main Behavior

- Defines common default operations: `fs_nosys()`, `fs_inval()`, `fs_notdir()`, `fs_sync()`, `fs_syncfs_nop()`, `fs_fsync()`, `fs_putpage()`, `fs_ioctl()`, `fs_rwlock()`, `fs_rwunlock()`, `fs_cmp()`, `fs_seek()`, `fs_setfl()`.
- `fs_frlock()` translates `fcntl` lock commands to reclock flags, handles remote/PXFS/OFD restrictions, supports NBMAND validation, serializes locks with `nbl_start_crit()`, and uses callback wrapping for blocking serialized locks.
- `fs_poll()` returns immediate readiness for regular filesystem polling, but rejects epoll and edge-triggered poll use with `EPERM` through `fs_reject_epoll()`.
- `fs_pathconf()` supplies defaults for link/path/name limits, pipe buffer, truncation, chown restriction, large-file bits, ACL support, case behavior, system attributes, and access filtering.
- `fs_dispose()` frees or destroys pages; `fs_nodispose()` panics if incorrectly invoked.
- `fs_fab_acl()` fabricates trivial ACLENT or ACE ACLs from mode/uid/gid for filesystems without native ACLs.
- `fs_shrlock()` implements common DOS share reservation handling and NBMAND validation.
- `fs_acl_nontrivial()` probes supported ACL styles and determines whether ACLs are nontrivial.
- `fs_need_estale_retry()` bounds retry attempts using tunable `fs_estale_retry`.

## Reparse Support

- `reparse_vnode_parse()` reads symlink data into a kernel buffer and parses it as reparse nvlist data.
- `reparse_point_init()` initializes door locking.
- `reparse_kderef()` builds `svc_type:svc_data`, calls the reparsed daemon via kernel door upcall, retries `EAGAIN`/`EINTR`, resets/reopens stale door handles on `EBADF`, handles `EOVERFLOW`, and copies returned service data into the caller buffer.

## Other Interfaces

- `fs_vscan_register()` installs an antivirus scan callback; `fs_vscan()` invokes it for regular files.
- `fs_vfsp_global()` builds an immortal pseudo-filesystem `vfs_t` for subsystems such as sockfs/fifofs that do not mount normally.

## Dependencies And Interactions

- Uses kernel vnode, lock manager, share reservation, ACL, door, nbmlock, pathname, and poll internals.
- Provides prototypes through `fs_subr.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fs_subr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fs_subr.h

## Role

Kernel-facing declaration header for the generic filesystem helper routines implemented mainly in `fs_subr.c`.

## Main Contents

- Declares default vnode/VFS operations such as `fs_nosys`, `fs_inval`, `fs_sync`, `fs_fsync`, `fs_putpage`, `fs_ioctl`, `fs_rwlock`, `fs_cmp`, `fs_seek`, `fs_poll`, and `fs_pathconf`.
- Declares page disposal helpers `fs_dispose()` and `fs_nodispose()`.
- Declares ACL/share helpers `fs_fab_acl()`, `fs_shrlock()`, and `fs_acl_nontrivial()`.
- Declares vnode event support stubs `fs_vnevent_nosupport()` and `fs_vnevent_support()`.
- Declares `fs_need_estale_retry()`, antivirus scan registration/callout functions, and `fs_vfsp_global()`.
- Declares `fs_reject_epoll()` for filesystems that need to reject epoll use in custom `VOP_POLL` handlers.

## Dependencies And Interactions

- Pulls in vnode, vfs, credential, poll, page, ACL, share, and flock types.
- Guarded for `_KERNEL` or `_FAKE_KERNEL`; provides C++ linkage guards.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fs_subr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fsflush.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fsflush.c

## Role

Implements the `fsflush` kernel daemon that periodically writes old dirty filesystem data, scans pages for writeback/release, coalesces free pages, and triggers filesystem attribute sync.

## Main Behavior

- Global tunables `doiflush` and `dopageflush` control inode/attribute flushing and page flushing.
- `fsflush_iflush_delay` delays inode flushing after boot to reduce boot-time atime churn, except in single-user mode.
- `fsflush_do_pages()` scans a rotating subset of physical pages based on `t_fsflushr` and `v_autoup`.
- Dirty filesystem pages are detected with `hat_ismod()` or `hat_pagesync()` and written asynchronously with `VOP_PUTPAGE()`.
- Unmapped clean pages can be released with `page_release()`.
- Free adjacent pages are opportunistically promoted to larger page sizes using `page_promote_size()`.
- Maintains recent and cumulative scan statistics in `fsf_recent`, `fsf_total`, and `fsf_cycles`.

## Daemon Loop

- `fsflush()` initializes CPR state, waits on `fsflush_cv`, serializes reboot with `fsflush_sema`, then:
  - scans delayed-write buffer freelists and writes buffers older than `v_autoup`;
  - updates `bfreelist.b_bcount`;
  - calls `fsflush_do_pages()` if enabled;
  - periodically calls `fsop_sync_by_kind(..., SYNC_ATTR, ...)` across installed filesystems.

## Dependencies And Interactions

- Uses buffer cache lists, page/hat VM APIs, UFS buffer write path for UFS-backed delayed writes, and VFS switch iteration.
- Cooperates with CPR via `CALLB_CPR_*` and reboot serialization through `fsflush_sema`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fsflush.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/gfs.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/gfs.c

## Role

Provides Generic File System support for in-kernel pseudo-filesystems. It offers reusable vnode creation, directory lookup/readdir, inactive cleanup, vnodeops creation, and read-only mmap support.

## Main Behavior

- `gfs_make_opsvec()` builds multiple vnodeops vectors and unwinds prior creations on failure.
- Low-level readdir helpers:
  - `gfs_get_parent_ino()` resolves parent/self inode numbers.
  - `gfs_readdir_init()` allocates reusable dirent/edirent state and validates offsets.
  - `gfs_readdir_emit()` and `gfs_readdir_emitn()` emit named or numeric entries.
  - `gfs_readdir_pred()` handles `.` and `..` and calculates virtual offsets.
  - `gfs_readdir_fini()` frees state and reports EOF.
- `gfs_lookup_dot()` handles empty name, `.`, and `..`.

## Managed GFS Objects

- `gfs_file_create()` allocates private data and vnode, initializes parent relationship, vnode ops, type/vfs/dev, and parent hold.
- `gfs_dir_create()` extends file creation for directories with static entries, dynamic callbacks, inode callback, max name length, and directory lock.
- `gfs_root_create()` and `gfs_root_create_file()` create VFS-rooted directory/file vnodes with `VROOT`, `VNOCACHE`, `VNOMAP`, `VNOSWAP`, and `VNOMOUNT`.

## Lookup And Readdir

- `gfs_dir_lookup_static()` searches static entries, optionally constructs and caches vnodes, resolves races where another thread caches first, and supports case-insensitive real-name output.
- `gfs_dir_lookup_dynamic()` calls a filesystem callback outside the directory lock, then annotates GFS vnode metadata.
- `gfs_dir_lookup()` combines dot, static, and dynamic lookup, including case-conflict detection via `ED_CASE_CONFLICT`.
- `gfs_dir_readdir()` emits static entries and dynamic callback entries through common readdir state.

## Cleanup And Mapping

- `gfs_file_inactive()` removes cached static references, handles xattrdir parent state, releases parent or VFS references, and frees vnode if refcount permits.
- `gfs_dir_inactive()` also destroys directory locks and static entry storage.
- `gfs_vop_inactive()`, `gfs_vop_lookup()`, and `gfs_vop_readdir()` are direct vnode op adapters.
- `gfs_vop_map()` supports read-only mmap by creating a zero-fill-on-demand mapping, then filling it through `vn_rdwr()`; it rejects executable/writable mappings.

## Dependencies And Interactions

- Used by pseudo-filesystems that place `gfs_file_t` or `gfs_dir_t` first in `v_data`.
- Interacts with VFS feature flags for case behavior and vnode extended attribute directory state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/gfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_node.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_node.c

## Role

Implements HSFS vnode/hsnode lifecycle, directory lookup, directory record parsing, ISO/Joliet/Rock Ridge name handling, and hsnode hash/free-list management.

## Node Cache And Hashing

- `hs_init_hsnode_cache()` and `hs_fini_hsnode_cache()` manage the `hsfs_hsnode_cache` kmem cache.
- `hs_hsnode_cache_reclaim()` purges DNLC entries and frees per-mount free-list hsnodes during memory pressure.
- `hs_getfree()` allocates or reuses hsnodes, invalidating cached pages and freeing symlink storage before reinitialization.
- `hs_findhash()` finds and reactivates cached hsnodes by inode; for `HS_DUMMY_INO`, it additionally matches directory LBN and offset.
- `hs_makenode()` normalizes directory entry location, chooses node id from RRIP inode, extent LBN, or dummy inode, creates/reuses vnode, installs `hsfs_vnodeops`, handles device nodes through `specvp()`, and inserts into the hash.
- `hs_freenode()` either fully frees vnode/hsnode resources or places nodes on the per-filesystem free list.
- `hs_synchash()` invalidates pages and frees all hsnodes during unmount, returning busy if referenced nodes remain.
- `hs_remakenode()` rereads a directory record by LBN/offset to reconstruct a vnode for `VFS_VGET`.

## Directory Lookup

- `hs_dirlook()` checks directory execute access, consults DNLC, prepares a comparison name based on RRIP/ISO/Joliet policy, then scans directory data with `fbread()` and `process_dirblock()`.
- Supports wraparound searching from the previous successful offset (`hs_offset`) for locality.
- Rejects ISO/Joliet lookup for raw `\1` names because `\1` represents `..` on disk.
- Adds successful results to DNLC when enabled.

## Directory Record Parsing

- `hs_parsedir()` parses High Sierra and ISO/Joliet directory records into `hs_direntry`.
- Sets extent LBN, size, XAR length, interleave data, type, mode, link count, uid/gid, dates, protection, inode, and symlink.
- Invokes `parse_sua()` when SUSP is implemented, allowing RRIP fields to override names, modes, times, devices, links, and relocation.
- Validates directory entry length, filename length, interleave constraints, multi-volume set expectations, and unsupported type bits.
- Falls back to ISO/Joliet name copying when RRIP did not change the name.

## Name Handling

- `hs_namecopy()` converts ISO names to Unix form, handles `.`/`..`, optional version stripping, lowercase mapping, and trailing-space trimming.
- `hs_jnamecopy()` converts Joliet UCS-2 names to UTF-8 and reports truncation as a negative length.
- `hs_uppercase_copy()`, `hs_iso_copy()`, and `hs_joliet_cp()` prepare lookup comparison names.
- `hs_ucs2_2_utf8()` implements UCS-2 to UTF-8 conversion.
- `strip_trailing()` and `hs_namelen()` support defensive warnings and version-aware length checks.

## Directory Block Processing

- `process_dirblock()` validates each directory entry boundary and name length, obtains RRIP names when present, handles ISO version stripping and strict ISO ordering, compares names, parses matching entries, releases fbuf before node creation, and returns `FOUND_ENTRY`, `WENT_PAST`, or `HIT_END`.
- The function contains hardening against malformed or malicious media: invalid short records, overlong names, bad RRIP symlink allocations, and sector boundary inconsistencies.

## Dependencies And Interactions

- Uses HSFS volume structures, vnode/page cache APIs, DNLC, SUSP/RRIP parsers, and VM page invalidation.
- Works with `hsfs_vfsops.c` for mount/unmount and `hsfs_vnops.c` for page invalidation callbacks such as `hsfs_putapage()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_node.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_rrip.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_rrip.c

## Role

Implements Rock Ridge Interchange Protocol handlers used by HSFS SUSP parsing.

## Main Behavior

- Defines `rrip_signature_table` mapping RRIP signatures to handlers: `CL`, `NM`, `PL`, `PN`, `PX`, `RE`, `RR`, `SL`, and `TF`.
- `rrip_dev_nodes()` parses device major/minor numbers from `PN`.
- `rrip_file_attr()` parses mode, nlink, uid, gid, optional inode, and vnode type from `PX`.
- `rrip_file_time()` parses access, modify, and change/attribute times from `TF`, using long or short ISO date forms.
- `rrip_name()` parses alternate names from `NM`, including special `.` and `..` handling.
- `rrip_sym_link()` builds synthetic symlink targets from `SL` components, handling continued components and final slash removal.
- `rrip_namecopy()` asks `parse_sua()` for an RRIP name and falls back to uppercase ISO comparison setup when no alternate name exists.
- `rrip_reloc_dir()` marks relocated directories so the ISO-visible relocated entry is hidden.
- `rrip_child_link()` and `rrip_parent_link()` follow relocated directory links by updating extent LBN and refilling directory metadata.
- `rrip_rock_ridge()` is a placeholder handler for `RR`.

## Important Details

- `name_parse()` is shared by filename and symlink parsing. It handles root/current/parent flags, unsupported volume-root/host flags, continuation/change flags, and binary-safe bounded copying because SUSP fields are not necessarily NUL-terminated.
- Symlink buffers are dynamically allocated according to computed target length and stored in `hs_direntry.sym_link`; `ext_size` becomes symlink length.

## Dependencies And Interactions

- Called from `parse_sua()` in `hsfs_susp_subr.c`.
- Overrides fields initialized by `hs_parsedir()` in `hsfs_node.c`.
- Uses HSFS date parsing helpers from `hsfs_subr.c`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_rrip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_subr.c

## Role

Provides HSFS miscellaneous helpers: ISO/HSFS date conversion, filesystem warning throttling, directory validity checks, and HSFS read kstats setup/update.

## Main Behavior

- Defines `hsfs_error[]`, a per-error warning table used to emit nonfatal media consistency warnings once per mount unless marked repeatable.
- `hs_parse_dirdate()` parses short directory-entry timestamps into Unix `timeval`.
- `hs_parse_longdate()` parses long volume-descriptor timestamps and preserves hundredths of seconds as microseconds.
- `hs_date_to_gmtime()` converts 1970-2099 dates plus GMT offset into seconds since epoch, with leap-year handling.
- `hsfs_valid_dir()` validates that an HSFS directory record is nonempty and has directory type.
- `hs_log_bogus_disk_warning()` emits structured warnings for malformed ISO/Joliet/Rock Ridge data and sets per-mount error flags.

## Kstats

- Defines named kstats for mountpoint, pages lost, physical read pages, cache read pages, readahead pages, coalesced pages, and total requested pages.
- `hsfs_kstats_update()` snapshots counters while holding HSFS queue locks.
- `hsfs_setup_named_kstats()` creates and installs virtual named kstats.
- `hsfs_init_kstats()` and `hsfs_fini_kstats()` manage per-mount kstat lifetime.

## Dependencies And Interactions

- Used by HSFS node parsing and mount code for dates, warnings, and read statistics.
- References `hsfs_lostpage` from HSFS vnode/page code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_susp.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_susp.c

## Role

Defines System Use Sharing Protocol signature tables and handlers for HSFS, plus the extension registry that enables RRIP parsing.

## Main Behavior

- Defines `susp_signature_table` mapping common SUSP signatures:
  - `SP` to `share_protocol()`
  - `CE` to `share_continue()`
  - `PD` to `share_padding()`
  - `ER` to `share_ext_ref()`
  - `ST` to `share_stop()`
- Exposes `susp_sp` and `susp_ce` as stable pointers to the first two table entries.
- Defines `extension_name_table` with SUSP first and RRIP second; the order matters because RRIP bit position is assumed by RRIP macros.

## Handlers

- `share_protocol()` validates SUSP check bytes, verifies supported version, sets the SUSP implemented bit, and records the SUA offset.
- `share_ext_ref()` scans known extension names and sets implemented bits for matching extension references.
- `share_continue()` records continuation area LBN, offset, and length for later reading.
- `share_padding()` skips padding records.
- `share_stop()` marks end of SUA parsing.

## Dependencies And Interactions

- Used by `parse_sua()` and `hs_check_root_dirent()` in `hsfs_susp_subr.c`.
- Enables RRIP handlers from `hsfs_rrip.c` after `ER` records are recognized.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_susp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_susp_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_susp_subr.c

## Role

Implements the core SUSP parser used by HSFS to process System Use Areas and continuation areas, including root-directory probing for SUSP/RRIP support.

## Main Behavior

- `parse_sua()` locates the System Use Area inside an ISO directory record, validates lengths, initializes `sig_args_t`, parses signatures, follows continuation areas, and returns name-change or relocation status.
- Defensively rejects negative SUA lengths and SUA ranges extending past the current directory record/block.
- `parse_signatures()` walks SUSP fields, dispatches to handlers for implemented extensions, advances by `SUF_LEN`, detects malformed lengths, and stops on end-of-SUA, relocation, allocation, or validation failures.
- Unknown signatures are skipped using their SUSP length field, with failsafes for short/invalid records.

## Root Probing

- `hs_check_root_dirent()` reads the root directory `.` entry, checks for an initial `SP` signature, invokes the SUSP handler, then runs `hs_parsedir()` twice so RRIP extension records discovered late can affect the cached root vnode metadata.
- If only SUSP and no real extension is found, it clears extension implementation bits and treats the media as plain ISO.

## Continuation Areas

- `get_cont_area()` validates continuation offset/length, reads continuation sectors, and handles areas that cross into the next sector by copying partial data into a zeroed buffer.
- `free_cont_area()` releases continuation buffers.

## Dependencies And Interactions

- Bridges SUSP handlers in `hsfs_susp.c`, RRIP handlers in `hsfs_rrip.c`, and directory parsing in `hsfs_node.c`.
- Uses HSFS warning machinery for inconsistent SUSP/RRIP data.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_susp_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_vfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_vfsops.c

## Role

Implements HSFS VFS operations, module initialization/finalization, mount option handling, volume descriptor discovery/parsing, root vnode setup, unmount, statvfs, vget, and root mounting.

## Module And Options

- Registers filesystem `hsfs` with VFS ops for mount, unmount, root, statvfs, vget, and mountroot.
- Defines mount options for global/noglobal, lowercase mapping, trailing dot, Rock Ridge, Joliet, Joliet long names, ISO9660:1999 `vers2`, read-only, and sector.
- `_init()`, `_fini()`, and `_info()` manage module lifecycle. `_fini()` frees vfs/vnode ops, mount lock, hsnode cache, and scheduler caches.
- `hsfsinit()` installs VFS ops, builds vnode ops, initializes `hs_mounttab_lock`, hsnode cache, and scheduler caches.

## Mount And Unmount

- `hsfs_mount()` enforces mount privilege, directory mountpoint, read-only mount, no unsupported remount, mountpoint busy checks, mount option flags, device lookup, tape rejection, and calls `hs_mountfs()`.
- `hsfs_unmount()` rejects forced unmount, requires root vnode count of one, calls `hs_synchash()`, removes mount table entry, closes/releases device vnode, frees path table data, kstats, scheduler queue, locks, and `hsfs`.
- `hsfs_root()` returns a held root vnode.
- `hsfs_statvfs()` reports read-only filesystem stats, fsid, base type, flags, name max, and volume id.
- `hsfs_vget()` finds an existing vnode by file id or reconstructs it via `hs_remakenode()`.

## Mount Core

- `hs_mountfs()` opens the block device read-only, rejects swap devices and zero-size devices, allocates `hsfs` and supplemental volume structs, discovers ISO or High Sierra volume descriptors, computes an fsid, links the mount into `hs_mounttab`, initializes VFS fields and locks, creates the root vnode, probes RRIP, chooses the active namespace, sets name limits/flags, initializes I/O scheduling and kstats, and marks the filesystem magic.
- Namespace selection prefers RRIP, ISO9660:1999, or Joliet according to discovered descriptors and explicit mount options. Explicit Joliet or `vers2` can force RRIP off; disabled options suppress their corresponding namespace.
- `hs_getrootvp()` creates the root vnode from the volume root record or remakes it if the root record is invalid.

## Volume Discovery And Parsing

- `hs_findhsvol()` scans up to 32 High Sierra volume descriptor sectors and parses the Standard File Structure descriptor.
- `hs_parsehsvol()` extracts volume size, logical block size, shifts, dates, path table info, volume set data, label, and root directory record; rejects zero or non-power-of-two block sizes.
- `hs_findisovol()` scans ISO descriptors for PVD, ISO9660:1999 SVD, and Joliet SVD, parses discovered volumes, then probes for an `MKI ` signature allowing extent LBNs as stable inode numbers.
- `hs_joliet_level()` recognizes Joliet levels from SVD escape sequences.
- `hs_parseisovol()` parses ISO volume metadata similarly to High Sierra parsing.
- `hs_copylabel()` copies volume labels, converting Joliet UCS-2 labels through `hs_joliet_cp()`.

## Device And Root Mount Helpers

- `hs_getmdev()` resolves the mount source, supports lofi-backed mounts through `vfs_get_lofi()`, checks block-device type, read access, mount conflicts, and major validity.
- `hsfs_mountroot()` mounts HSFS as root on `ROOT_INIT`, handles root device lookup, VFS locking/addition, root vnode assignment, and clock setting from volume dates.
- `hs_findvoldesc()` returns the starting volume descriptor sector, optionally using `CDROMREADOFFSET` for multisession media.

## Dependencies And Interactions

- Coordinates with `hsfs_node.c` for root/vnode creation and hash cleanup, `hsfs_subr.c` for dates/kstats/warnings, SUSP/RRIP probing for extension selection, and HSFS scheduler code for read scheduling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_vfsops.c -->