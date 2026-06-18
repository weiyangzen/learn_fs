# Group Research: group_1865_xfsdump_sources_local_fs_xfsdump_inventory_inv_api_c_sources_local__32d8e3b0838c

Scope checked against `Docs/research_subset_a.md`: all files are within `sources/local-fs/xfsdump`. I read each listed file completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_api.c -->
# File Research: sources/local-fs/xfsdump/inventory/inv_api.c

Implements the public inventory API used by xfsdump/xfsrestore to open inventory databases, create write sessions, create streams, record media files, query prior sessions, reconstruct inventory from packed session records, delete media objects, and print/debug inventory contents.

Key flows:
- `inv_open()` initializes the inventory for a filesystem predicate, creates or opens the filesystem `.InvIndex`, selects the last `.StObj`, and creates a new storage object when the selected one is full.
- `inv_writesession_open()` ensures fstab contains the filesystem, creates an on-disk session header/session record, and updates index start time for newly created index entries.
- `inv_stream_open()`, `inv_put_mediafile()`, and `inv_stream_close()` manage stream records and append linked mediafile records, keeping stream end inode information synchronized.
- `inv_get_sessioninfo()` packs a still-open session into a portable buffer for writing to media; `inv_put_sessioninfo()` reconstructs by inserting unpacked session data.
- Query helpers delegate to `search_invt()` with callbacks for last lower/equal dump level and exact session uuid/label lookup.
- `inv_getopt()` and `inv_DEBUG_print()` implement `-I` inventory printing/checking suboptions.

Important dependencies:
- Uses `inv_priv.h` on-disk structures, token internals, `GET_*`/`PUT_*` macros, and `INVLOCK`.
- Uses `inv_mgr.c` for initialization, search, printing, and reconstruction insertion.
- Uses `inv_idx.c`, `inv_fstab.c`, and `inv_stobj.c` for index, fstab, and storage-object operations.

Notable observations:
- The API assumes callers obey token lifetime order: stream close, write-session close, inventory close.
- String copies into fixed `INV_STRLEN` fields use `strcpy()` and trust upstream lengths.
- `inv_delete_mediaobj()` is wired to `stobj_delete_mobj()`, but the storage-object deletion implementation is effectively incomplete.
- `inv_DEBUG_print()` returns `BOOL_FALSE` after printing, which is intentionally used by `testmain.c` to stop normal debug-test execution.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_api.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_core.c -->
# File Research: sources/local-fs/xfsdump/inventory/inv_core.c

Provides low-level inventory disk I/O helpers over fixed-size on-disk records.

Key functions:
- `get_counters()` reads a counter block at offset zero, validates `INV_VERSION`, and returns `ic_curnum`.
- `get_headers()` allocates and reads a header/entry array from a supplied offset.
- `get_invtrecord()` and `put_invtrecord()` wrap `pread()`/`pwrite()` with optional `flock()` locking.
- `get_headerinfo()` reads counters and, if nonempty, the corresponding header array.
- `get_lastheader()` reads counters plus all headers and copies the last one to a caller-owned allocation.

Important dependencies:
- Used through macros in `inv_priv.h`: `GET_REC`, `GET_REC_NOLOCK`, `GET_ALLHDRS_N_CNTS`, `PUT_REC`, `GET_COUNTERS`, and related helpers.
- Relies on callers to choose locking correctly. Several higher layers call `_NOLOCK` variants only while already holding a lock.

Notable observations:
- Short reads/writes are treated as errors.
- Version mismatch logs and asserts, so unsupported inventory versions are fatal in debug/assert-enabled builds.
- `get_lastheader()` returns the number of headers as well as the copied header, which callers use as a one-based index.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_core.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_files.c -->
# File Research: sources/local-fs/xfsdump/inventory/inv_files.c

Centralizes inventory path selection and path construction.

Key behavior:
- Chooses between FHS path `/var/lib/xfsdump` and legacy `/var/xfsdump`.
- If both bases exist and are distinct filesystems/inodes, setup fails.
- Builds static paths for inventory directory, fstab file, and lock file.
- Exposes `inv_dirpath()`, `inv_fstab()`, `inv_lockfile()`, and `inv_basepath()`.

Important dependencies:
- `INV_DIRPATH`, `INV_FSTAB`, and `INV_LOCKFILE` macros in public/private headers call these functions.
- `inv_setup_base()` must be called before path access; accessors assert `inv_base` is initialized.

Notable observations:
- Uses fixed 64-byte path buffers because paths are known constants.
- Path migration logic prefers the new `/var/lib/xfsdump` base unless the old base exists.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_files.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_fstab.c -->
# File Research: sources/local-fs/xfsdump/inventory/inv_fstab.c

Manages the inventory fstab, the top-level table mapping filesystem UUIDs to mount points and device paths.

Key functions:
- `fstab_getall()` opens `INV_FSTAB`, reads the counter and all `invt_fstab_t` entries, and leaves the file locked exclusive for the caller.
- `fstab_put_entry()` creates the fstab if missing, initializes counters, avoids duplicate UUID entries, and appends a new filesystem entry.
- `fstab_get_fname()` resolves an inventory filesystem prefix path from UUID, mount point, or device path.
- `fstab_DEBUG_print()` prints mount, device, and filesystem UUID entries.

Important dependencies:
- Feeds `init_idb()` and any code needing a filesystem-specific `.InvIndex` path.
- Uses `INV_DIRPATH/<uuid>` plus `.InvIndex` naming convention.

Notable observations:
- Duplicate detection is UUID-only; commented code suggests mount/device matching was once considered.
- `fstab_getall()` locks exclusive even for read-only access, so callers must unlock/close.
- Some error paths in `fstab_get_fname()` can return without freeing `arr` when no UUID is found.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_fstab.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_idx.c -->
# File Research: sources/local-fs/xfsdump/inventory/inv_idx.c

Implements per-filesystem inventory index files. Each `.InvIndex` contains a counter plus `invt_entry_t` records, where each record names a `.StObj` and its covered time range.

Key functions:
- `idx_create()` creates a new `.InvIndex` and its first storage object.
- `idx_create_entry()` appends a new storage-object entry and returns a token/descriptor for it.
- `idx_get_stobj()` opens the storage object referenced by the last index entry.
- `idx_put_sesstime()` updates an index entry’s start/end time when a session starts or ends.
- `idx_find_stobj()` and `idx_insert_newentry()` select a storage object for reconstruction by session time.
- `idx_put_newentry()` inserts a new index entry after the current index position during storage-object splitting.
- Debug helpers print index entries and display sessions.

Important dependencies:
- Calls `stobj_create()` and `stobj_makefname()` to allocate storage objects.
- Relies on `invt_idxinfo_t` during reconstruction and split operations.
- Uses `IDX_HDR_OFFSET()` to address index entries after the counter.

Notable observations:
- Several insertion branches that would create new in-between entries are commented out; current behavior often reuses an adjacent existing stobj.
- `idx_insert_newentry()` asserts unreachable if no placement is found.
- The index model assumes non-overlapping time periods and that the last entry is the writable target for normal dumping.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_idx.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_mgr.c -->
# File Research: sources/local-fs/xfsdump/inventory/inv_mgr.c

Coordinates inventory database initialization, token creation, cross-filesystem searches, inventory printing/checking, reconstruction insertion, and directory creation.

Key functions:
- `init_idb()` ensures inventory directory availability, resolves the filesystem inventory filename, opens or creates `.InvIndex`, and returns either an fd or sentinel.
- `get_token()`, `destroy_token()`, and `get_sesstoken()` allocate internal token descriptors.
- `search_invt()` scans index entries and storage-object session headers in reverse chronological order, skipping pruned sessions and optionally filtering by filesystem UUID.
- `invmgr_query_all_sessions()` searches every filesystem in fstab and handles ambiguous multiple hits.
- `invmgr_inv_print()` and `invmgr_inv_check()` implement inventory display and time-range consistency checks.
- Search callbacks implement “last lower dump level”, “last equal level”, and time-only lookups.
- `insert_session()` reconstructs inventory state from packed session info.
- `make_invdirectory()` recursively creates the inventory directory path.

Important dependencies:
- Connects fstab, index, and storage-object layers.
- Uses callbacks from `inv_stobj.c` for exported session construction and UUID/label matching.

Notable observations:
- `insert_session()` has inverted-looking error logic: it sets `ret = BOOL_TRUE` when insert/time update fails, then returns `BOOL_FALSE` if `ret` is true.
- `inv_priv.h` declares `init_idb()` as returning `bool_t`, while implementation returns `int` sentinels/fds.
- Global lock-file helpers are inside `#ifdef NOTDEF`; normal locking is per-file with `flock()`.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_mgr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_oref.c -->
# File Research: sources/local-fs/xfsdump/inventory/inv_oref.c

Appears to be an unfinished alternate “object reference” abstraction for lazily resolving fstab, inventory index, and storage-object structures.

Intended responsibilities:
- Resolve object type (`INVIDX`, `FSTAB`, `STOBJ`) and resource depth (counters, entries, headers, sessions, streams, mediafiles).
- Cache loaded structures in an `invt_oref_t`.
- Synchronize counters/entries back to disk.
- Resolve child storage objects from index entries.
- Create new inventory index and storage objects through oref state.

Important dependencies:
- Uses `inv_oref.h` macros and `inv_priv.h` storage helpers.
- Intended to replace or abstract parts of `inv_idx.c`/`inv_mgr.c`.

Notable observations:
- This file does not look buildable as written: calls like `OREF_ISRESOLVED(INVT_OTYPE_STOBJ)` omit the object argument; symbols such as `oref`, `OREF_CNT`, `OREF_CHILD`, `fd`, `stobj`, `tok`, `rval`, and `invfd` are used inconsistently or undeclared.
- Function calls to `fstab_get_fname()` omit the `forwhat` argument required by `inv_priv.h`.
- Several storage-object resource resolvers referenced by `oref_resolve_upto()` are not implemented in this file.
- Best classified as stale/dead experimental code rather than active inventory logic.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_oref.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_oref.h -->
# File Research: sources/local-fs/xfsdump/inventory/inv_oref.h

Defines the intended object-reference structure and macros for the unfinished `inv_oref.c` abstraction.

Key contents:
- Object type flags for inventory index, fstab, and storage object.
- Resolution-depth flags for counters, entries, storage-object headers, sessions, streams, mediafiles, and parent/child kinship.
- `invt_oref_t`, which stores fd, resolved counters, resolved entries/session components, parent/child refs, type flags, lock state, and token pointer.
- Macros for initializing/destroying refs, locking, setting resolved fields, accessing counters/entries, and clearing child refs.
- Prototypes for oref resolution functions.

Notable observations:
- Contains multiple macro/name inconsistencies: `cu_sescnt` maps to `oref_sescnt_u.sescnt`, but the union is named `oref_cnt_u`; child/parent macros use `ku_child`/`ku_parent`, while aliases define `ku_invidx`/`ku_stobj`.
- `OREF_ISLOCKED()` appears logically inverted: it returns true when `lockflag` is `0` or `LOCK_UN`.
- Tail section under `#ifdef NOTDEF` contains unrelated/stale XLV oref declarations.
- This header reinforces that the oref layer is incomplete and not the reliable API surface.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_oref.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_priv.h -->
# File Research: sources/local-fs/xfsdump/inventory/inv_priv.h

Private inventory header defining the on-disk format, token internals, helper macros, and internal function prototypes.

Key contents:
- Documents the three-level inventory hierarchy: fstab -> per-filesystem inventory index -> storage objects.
- Defines constants for object capacities, flags, permissions, return values, offsets, and locking.
- Defines on-disk structures: `invt_session_t`, `invt_seshdr_t`, `invt_stream_t`, `invt_mediafile_t`, `invt_entry_t`, `invt_counter_t`, `invt_sescounter_t`, and `invt_fstab_t`.
- Defines token structures: inventory token, session token, and stream token.
- Defines reconstruction/query containers: `invt_sessinfo_t`, `invt_idxinfo_t`, `invt_mobjinfo_t`, and `invt_pr_ctx_t`.
- Provides I/O macros over `inv_core.c`.
- Declares internal functions across index, storage-object, fstab, manager, and debug modules.

Important on-disk layout:
- Index/fstab files start with `invt_counter_t`, followed by fixed-size entry arrays.
- Storage objects start with `invt_sescounter_t`, then reserved session headers, session records, then variable stream/mediafile data from `ic_eof`.
- `INVT_STOBJ_MAXSESSIONS` is 5, so storage objects split frequently.

Notable observations:
- Prototypes include some inconsistencies with implementations, notably `init_idb()` return type.
- Public structs in `inventory.h` are distinct from private on-disk structs; conversion lives in `inv_stobj.c`.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_priv.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_stobj.c -->
# File Research: sources/local-fs/xfsdump/inventory/inv_stobj.c

Implements storage-object operations. A `.StObj` holds session headers, session records, stream records, and linked mediafile records for one filesystem/time range.

Key functions:
- `stobj_create()` creates and initializes a storage object with `invt_sescounter_t`.
- `stobj_create_session()` and `stobj_put_session()` allocate session header/session/stream space and update counters.
- `stobj_put_mediafile()` appends a mediafile record, updates stream start/end positions, and maintains the linked mediafile chain.
- `stobj_insert_session()` supports reconstruction, rejecting duplicate session IDs and splitting full storage objects.
- `stobj_split()` creates a new storage object, moves later sessions, adjusts index time ranges, and inserts the new session.
- `stobj_pack_sessinfo()` serializes one session, its streams, and mediafiles into the packed inventory format.
- `stobj_unpack_sessinfo()` validates the cookie, handles packed versions 1 and 2, performs endian/architecture translation, and points an `invt_sessinfo_t` into the packed buffer.
- `stobj_make_invsess()`/`stobj_copy_invsess()` convert on-disk structures to public `inv_session_t`.
- `DEBUG_sessionprint()` prints sessions with filtering by depth, dump level, and media object.

Important dependencies:
- Uses `arch_xlate.h` conversion routines for packed session portability.
- Uses index helpers for split/insertion and manager search callbacks for queries.
- Uses `ctime32()` for display.

Notable observations:
- `stobj_delete_mobj()` is mostly stubbed/commented and always returns false to continue iteration; media-object deletion is therefore not functionally complete.
- `stobj_delete_sessinfo()` only decrements the in-memory counter and intentionally leaves data space wasted.
- Packed version 1 alignment workaround leaks a small allocated buffer by design, as documented in comments.
- `stobj_hdrcmp()` subtracts `time32_t` values and returns `int`, which is simple but can overflow if widened ranges are introduced.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/inventory/inv_stobj.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/inventory/inventory.h -->
# File Research: sources/local-fs/xfsdump/inventory/inventory.h

Public inventory API header for xfsdump/xfsrestore clients.

Key contents:
- Defines inventory path macros, filename suffixes, inventory versions, packed inventory versions, and print-depth constants.
- Defines open predicates (`INV_BY_UUID`, `INV_BY_MOUNTPT`, `INV_BY_DEVPATH`) and open modes (`INV_SEARCH_ONLY`, `INV_SEARCH_N_MOD`).
- Defines public exported session model: `inv_mediafile_t`, `inv_stream_t`, and `inv_session_t`.
- Opaquely declares token pointer types for inventory, session, and stream access.
- Declares lifecycle APIs: `inv_open()`, `inv_close()`, write-session open/close, stream open/close, mediafile append.
- Declares query APIs for last lower/equal dump level, session lookup by UUID/label, and session freeing.
- Declares packed session APIs for dump/restore reconstruction and inventory debug/printing helpers.
- Declares inventory path setup/accessors.

Important design:
- Public callers never see on-disk private structs directly.
- Write path is hierarchical: inventory token -> session token -> stream token -> mediafiles.
- Reconstruction path bypasses token lifecycle using packed session info.

Notable observations:
- Header documents that inventory is intentionally dump/restore-specific, not a generic database.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/inventory/inventory.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/inventory/testmain.c -->
# File Research: sources/local-fs/xfsdump/inventory/testmain.c

Legacy low-level debug/test driver for the inventory subsystem.

Key functions:
- `write_test()` generates fake filesystem/session/media UUIDs, opens inventory write sessions, creates streams/mediafiles, and optionally writes packed session info for reconstruction testing.
- `query_test()` exercises index printing and last-session/last-time queries.
- `recons_test()` reads serialized session buffers and reinserts them.
- `delete_test()` tests media-object deletion from a saved `moids` file.
- `sess_queries_byuuid()` and `sess_queries_bylabel()` query and print a session.
- `main()` parses a local debug command set and delegates to the above.

Notable observations:
- The file is explicitly described as hacked-up low-level debugging code.
- Several calls no longer match current public prototypes, for example missing `fsidp` arguments to query functions and old `inv_put_sessioninfo()` shape in reconstruction code.
- Uses old UUID APIs such as `uuid_create()`/`uuid_to_string()` in places, while other files use libuuid-style APIs.
- `main()` lacks an explicit return type, reflecting old C style.
- Best treated as historical/debug scaffolding, not a maintained test suite.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/inventory/testmain.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/invutil/Makefile -->
# File Research: sources/local-fs/xfsdump/invutil/Makefile

Builds the `xfsinvutil` inventory maintenance utility.

Key contents:
- Includes top-level xfsdump build definitions.
- Symlinks common headers/sources from `../common` and inventory headers/sources from `../inventory`.
- Always includes `invutil.c`; conditionally includes curses UI sources when `ENABLE_CURSES=yes`.
- Curses sources include `cmenu.c`, `fstab.c`, `invidx.c`, `list.c`, `menu.c`, `screen.c`, and `stobj.c`.
- Links with `LIBUUID` and `LIBCURSES`.
- Installs the command into `$(PKG_SBIN_DIR)`.

Notable observations:
- `LCFLAGS = -DDUMP` is always set; `-DHAVE_CURSES` is added only for curses builds.
- When curses is disabled, UI sources are still listed as source files but not compiled into the command.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/invutil/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/invutil/cmenu.c -->
# File Research: sources/local-fs/xfsdump/invutil/cmenu.c

Implements the curses menu controller for `xfsinvutil`.

Key functions:
- Defines key bindings for expand/collapse, delete/undelete, import, commit, quit, and select.
- `signal_handler()` rebuilds windows after `SIGWINCH`.
- `menu_commit()` walks menu nodes, calls node-specific commit handlers once, then frees the list.
- `menu_import()` prompts for an inventory path, loads its fstab subtree, and marks imported nodes.
- Expand/collapse helpers show/hide child nodes recursively.
- Delete/undelete helpers mark nodes and their descendants/ancestors.
- `list_prune()` applies node-specific prune predicates and delete/undelete operations.
- `generate_menu()` starts tree generation from fstab.
- `create_windows()` initializes curses pads/windows.
- `invutil_interactive()` runs the interactive menu and closes all mapped/open files at exit.

Important dependencies:
- Uses menu operations supplied by fstab, invidx, and stobj modules.
- Depends on `list.c`, `menu.c`, and `screen.c` for list allocation and UI drawing.

Notable observations:
- `list_delete()` has a likely bug: `if(current == NULL && current->data == NULL)` should use `||`; as written it can dereference null.
- Import marks text column `[1] = 'I'`, relying on generated display string layout.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/invutil/cmenu.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/invutil/cmenu.h -->
# File Research: sources/local-fs/xfsdump/invutil/cmenu.h

Declares curses menu types, globals, convenience macros, and operations.

Key contents:
- Defines info-window size and macros for header/footer/error/info/option drawing.
- Defines `alignment_t`.
- Defines `menu_ops_t`, the per-node operation vtable used by fstab, index, and storage-object nodes.
- Defines `menukey_t` for key binding dispatch.
- Defines shared fileinfo structs for mapped fstab, invidx, and stobj files.
- Declares global curses windows and redraw flags.
- Declares menu/list operation entry points and `generate_menu()`.

Important dependencies:
- Includes private inventory structures, so invutil edits the raw on-disk format directly.
- Depends on `list.h` `node_t`/`data_t` definitions.

Notable observations:
- This header is the coupling point between generic curses menu code and inventory-specific file editors.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/invutil/cmenu.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/invutil/fstab.c -->
# File Research: sources/local-fs/xfsdump/invutil/fstab.c

Implements invutil operations for viewing, pruning, importing, deleting, and committing fstab entries.

Key functions:
- `generate_fstab_menu()` opens/maps a fstab file, creates one menu node per filesystem, and then generates child invidx menus.
- `fstab_highlight()` displays device and UUID in the info window.
- `fstab_prune()` matches entries by mount point or UUID.
- `fstab_commit()` deletes native entries by shifting mmap contents and decrementing counters, or imports entries after committing children.
- `find_matching_fstab()` avoids duplicate imports.
- `remmap_fstab()` grows/remaps the fstab file and rebuilds data pointers.
- `open_fstab()`, `close_fstab()`, and `close_all_fstab()` manage locked, mmap-backed fstab files.

Important dependencies:
- Uses invutil path helpers such as `GetFstabFullPath()` and `GetNameOfInvIndex()`.
- Calls `invidx_commit()` for child inventory-index entries.

Notable observations:
- Mmap growth uses `lseek()` plus a one-byte write because Linux mappings do not autogrow.
- Closing truncates unused capacity and unlinks empty fstab files.
- Imported fstab entries commit their child index/storage-object data before adding the fstab row.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/invutil/fstab.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/invutil/fstab.h -->
# File Research: sources/local-fs/xfsdump/invutil/fstab.h

Declares invutil fstab operations.

Key contents:
- `generate_fstab_menu()` for building the fstab subtree.
- File lifecycle helpers: `open_fstab()`, `close_all_fstab()`, `remmap_fstab()`.
- Matching helper: `find_matching_fstab()`.
- Menu operations: select, highlight, commit, prune.

Important dependencies:
- Includes `inv_priv.h`, `list.h`, and `cmenu.h`, so declarations expose curses/menu and private inventory types.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/invutil/fstab.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/invutil/getopt.h -->
# File Research: sources/local-fs/xfsdump/invutil/getopt.h

Defines command-line option constants for `xfsinvutil`.

Key contents:
- `GETOPT_CMDSTRING` is `dilnu:wCFM:m:s:`.
- Defines option characters for debug, interactive, noninteractive, UUID prune, wait for locks, check/prune fstab, force, prune mount point, prune media label, and prune session id.

Notable observations:
- `-n` is marked obsolete in favor of `-F`.
- This header is distinct from `inventory/getopt.h`; option meanings are invutil-specific.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/invutil/getopt.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/invutil/invidx.c -->
# File Research: sources/local-fs/xfsdump/invutil/invidx.c

Implements invutil operations for inventory index entries and import/merge behavior across `.InvIndex` and `.StObj` files.

Key functions:
- `generate_invidx_menu()` opens/maps an index file, creates one node per `invt_entry_t`, and generates child storage-object menus.
- `invidx_commit()` handles deletion of native index entries, importing new entries, copying storage objects, and merging overlapping imported time ranges.
- Merge helpers read sessions from source stobjs and insert them into destination stobjs, splitting full storage objects as needed.
- `read_stobj_info()`, `insert_stobj_into_stobjfile()`, `delete_stobj_entries()`, `find_stobj_insert_point()`, and `update_invidx_entry()` implement raw stobj editing for import/merge.
- `find_overlapping_invidx()` and `find_invidx_insert_pos()` place imported index entries by time range.
- `remmap_invidx()`, `open_invidx()`, `close_invidx()`, and `close_all_invidx()` manage locked, mmap-backed index files.
- Local copies of `stobj_create()` and `stobj_put_streams()` support creating/rewriting storage objects during invutil import.

Important dependencies:
- Uses global `stobj_file` state from invutil’s stobj module.
- Uses raw private inventory structures and offset macros from `inv_priv.h`.
- Uses shell `cp` via `system()` for shortcut storage-object file copies when no merge is needed.

Notable observations:
- The import path has two modes: copy whole stobj files for non-overlap, or merge individual sessions for overlap.
- Some insertion/copy code assumes streams and mediafiles are present; `insert_stobj_into_stobjfile()` returns early if any of `hdr`, `ses`, `strms`, or `mfiles` is null, so zero-stream or zero-media sessions may not import through that path.
- `remmap_invidx()` uses a size expression similar to fstab remap; it grows capacity by `num` but maps `(nEntries + 1) * (num * sizeof(entry)) + counter`, which only behaves as expected for `num == 1`.
- Shell command construction for `cp` is not quoted, so paths with spaces or shell metacharacters would be unsafe.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/invutil/invidx.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/invutil/invidx.h -->
# File Research: sources/local-fs/xfsdump/invutil/invidx.h

Declares invutil inventory-index operations.

Key contents:
- Menu generation and file lifecycle: `generate_invidx_menu()`, `open_invidx()`, `close_invidx()`, `close_all_invidx()`, `remmap_invidx()`.
- Lookup helpers for matching stobj/invidx files and finding overlapping/insert positions.
- Raw stobj import helpers: `read_stobj_info()`, `insert_stobj_into_stobjfile()`, `insert_stobj_into_inventory()`.
- Menu operations: undelete, select, highlight, commit, prune.

Notable observations:
- Header exposes raw on-disk structs because invutil directly manipulates inventory files.
- `insert_stobj_into_inventory()` is declared here but not present in the read `invidx.c`, suggesting either stale declaration or implementation elsewhere/removed.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/invutil/invidx.h -->