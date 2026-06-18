# Group Research: group_499_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_s_d2bd3a41d6f5

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included. All 11 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_kshare.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_kshare.c

This file manages kernel-side SMB share lifecycle for the illumos SMB server. It bridges userland share definitions, door upcalls, server export state, AVL-backed share lookup, and asynchronous unshare cleanup.

Key responsibilities:
- Initializes and destroys global share/unexport kmem caches.
- Starts and stops per-server share export state.
- Maintains `sv->sv_export.e_share_avl`, an AVL tree of `smb_kshare_t` objects using `smb_avl_*` helpers from `smb_kutil.c`.
- Exports built-in transient shares: `IPC$`, `c$`, and `vss$`.
- Decodes userland nvlist share definitions into kernel `smb_kshare_t`.
- Handles autohome reference counting and special/admin share flags.
- Resolves disk-share roots through `smb_server_share_lookup`.
- Handles continuous availability share setup through `smb2_dh_new_ca_share`.
- Queues unexport events to `e_unexport_thread` so disconnect/cleanup work is decoupled from ioctl or unmount contexts.
- Provides host access filtering by upcalling to `smbd`.

Important functions:
- `smb_export_start` creates the share AVL and publishes transient shares.
- `smb_export_stop` flips export readiness off and destroys the AVL.
- `smb_kshare_export_list` unpacks an nvlist of shares from ioctl data and exports each decoded share.
- `smb_kshare_unexport_list` unexports shares, then queues asynchronous server unshare cleanup.
- `smb_kshare_lookup` returns a held share object; callers must release with `smb_kshare_release`.
- `smb_kshare_export` handles duplicate/autohome logic, root-node lookup, AVL insertion, and CA setup.
- `smb_kshare_unexport` removes a share from the AVL or decrements autohome count.
- `smb_kshare_decode` maps nvlist properties and SMB share options to `smb_kshare_t` fields and flags.
- `smb_kshare_destroy` releases CA/root nodes and all duplicated strings.
- `smb_kshare_hostaccess` maps share-level host allow/deny/read-only lists into ACE permissions.

Concurrency and lifetime:
- Export readiness is protected by `sv_export.e_mutex`.
- Share objects use `shr_refcnt` and `shr_mutex`; AVL callbacks increment/decrement references.
- AVL destruction waits for in-flight AVL users through `smb_avl_destroy`.
- Unexport cleanup is intentionally asynchronous to avoid deadlocks during forced unmount or stuck filesystem operations.
- `smb_kshare_export` consumes ownership of `shr` only on success; callers destroy it on failure.

Filesystem relevance:
- Disk shares hold a root `smb_node_t` for the shared path.
- Unexport paths call `smb_server_unshare` asynchronously, which disconnects trees/files associated with the share.
- CA shares may create or import persistent handle directories.

Edge cases and risks:
- ioctl nvlist size is checked against the ioctl buffer length before unpacking.
- `smb_kshare_decode` relies on required nvlist fields `name`, `path`, `smb`, and `type`; malformed definitions fail decode.
- OEM share names longer than `SMB_SHARE_OEMNAME_MAX` become `NULL` and are skipped by RAP enumeration.
- Autohome shares are treated specially: duplicate export increments `shr_autocnt`; unexport removes only when count reaches zero.
- Door upcall code is marked non-thread-safe and expects caller serialization.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_kshare.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_kutil.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_kutil.c

This file is a shared kernel utility layer for the SMB server. It implements string-size helpers, wildcard conversion, DOS attribute checks, ID pools, locked list/AVL containers, synchronization wrappers, time conversion, utilization accounting, thresholds, and simple hash bucket allocation.

Key responsibilities:
- Computes SMB ASCII/OEM vs UTF-16 string lengths depending on dialect and Unicode flags.
- Converts old DOS/LanMan wildcard syntax to NT wildcard syntax.
- Checks DOS search attributes against file attributes.
- Allocates 16-bit IDs with a bitmap-backed `smb_idpool_t`.
- Implements locked AVL/list containers with deferred destructor queues.
- Implements synchronized lists with wait-for-empty behavior.
- Provides `smb_rwx_t`, an rwlock plus condition variable helper.
- Converts between Unix, NT, DOS, GMT, and local SMB timestamps.
- Wraps AVL trees with ref-counted lifetime protection.
- Tracks latency and service-request queue utilization.
- Implements threshold gates for limiting concurrent command classes.
- Creates/destroys a simple power-of-two bucket hash table.

Important functions:
- `smb_idpool_constructor`, `smb_idpool_alloc`, `smb_idpool_free`, `smb_idpool_destructor`.
- `smb_lavl_*` for locked AVL operations and deferred object destruction.
- `smb_llist_*` for locked linked lists and deferred object destruction.
- `smb_slist_*` for mutex-protected lists with condition-variable wakeups.
- `smb_rwx_cvwait` drops and reacquires an rwlock while waiting on a CV.
- `smb_time_unix_to_nt`, `smb_time_nt_to_unix`, `smb_time_dos_to_unix`, `smb_time_unix_to_dos`.
- `smb_gmtime_r` and `smb_timegm` provide internal UTC conversion.
- `smb_avl_create`, `smb_avl_add`, `smb_avl_remove`, `smb_avl_lookup`, `smb_avl_iterate`, `smb_avl_release`, `smb_avl_destroy`.
- `smb_threshold_enter`, `smb_threshold_exit`, `smb_threshold_wake_all`.
- `smb_hash_create`, `smb_hash_destroy`, `smb_hash_uint64`.

Concurrency and lifetime:
- `smb_lavl` and `smb_llist` use rwlocks for tree/list access plus mutex-protected delete queues.
- Deferred destruction intentionally drops the delete-queue mutex while invoking destructors, allowing recursive posts.
- `smb_avl_t` protects tree destruction with `avl_state`, `avl_refcnt`, and `avl_cv`.
- Objects returned by `smb_avl_lookup` and `smb_avl_iterate` are held and must be released.
- `smb_slist_wait_for_empty` waits until `sl_count` reaches zero and is signaled by remove/move/exit paths.
- Queue/latency statistics use spin mutexes because they may be updated in high-frequency paths.

Filesystem relevance:
- These primitives back share storage, lock lists, request queues, and many SMB server object tables.
- Time conversion functions are used by protocol marshaling and file metadata translation.
- Attribute filtering affects directory search results.

Edge cases and risks:
- ID pool doubles until `SMB_IDPOOL_MAX_SIZE`; ID 0 and 0xffff are reserved.
- `smb_avl_iterate` terminates early if AVL sequence changes during iteration.
- `smb_time_nt_to_unix` preserves SMB sentinel values 0, -1, and -2.
- `smb_time_nt_to_unix` truncates seconds into a `uint32_t`, so very large NT times are constrained by Unix time representation here.
- Threshold wake-all sets threshold to zero, causing waiters to return `ECANCELED`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_kutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_lock.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_lock.c

This file implements SMB byte-range locking. It maintains granted and waiting lock lists on `smb_node_t`, enforces SMB lock compatibility rules, mirrors locks into filesystem/POSIX record locks, handles blocking waits and cancellation, and translates vnode/NBL conflicts to SMB status codes.

Key responsibilities:
- Counts locks held by an open file.
- Grants and releases SMB byte-range locks.
- Checks read/write access against existing SMB range locks.
- Cancels waiting locks.
- Destroys all locks associated with an ofile on close.
- Mirrors successful locks/unlocks through `smb_fsop_frlock`.
- Handles waiting lock wakeup ordering.
- Checks share/byte-range conflicts through illumos NBML interfaces.

Important functions:
- `smb_lock_range` creates a desired lock, applies lock rules, waits if allowed, mirrors to the filesystem, inserts into `node->n_lock_list`, and breaks read-cache delegations on success.
- `smb_unlock_range` finds an exact lock match, removes it, unlocks POSIX-visible ranges not still covered by same-ofile locks, and destroys the SMB lock.
- `smb_lock_range_access` denies reads/writes that conflict with SMB locks from other file/PID contexts.
- `smb_node_destroy_lock_by_ofile` cancels waiters and moves matching granted locks to a temporary list before destroying them.
- `smb_lock_range_cancel` marks a matching waiting lock cancelled.
- `smb_nbl_conflict` maps NBL share and lock conflicts to SMB status values.
- `smb_lock_wait` records dependency on a conflicting lock, moves request state to `SMB_REQ_STATE_WAITING_LOCK`, waits with timeout/cancel support, and restores state.
- `smb_lock_destroy` wakes waiting locks blocked by the destroyed lock.
- `smb_is_range_unlocked` determines subranges that can be released from POSIX locks without releasing overlapping SMB locks.

Lock semantics:
- Exact unlock match requires same start, length, ofile, and PID.
- Read-only locks can overlap other read-only locks.
- A read-only lock may overlap a write lock held by the same file and PID.
- Write locks conflict with overlapping locks unless compatible by the above rules.
- Zero-length ranges have special overlap semantics: they affect no bytes but can conflict with positive-length ranges containing their offset.
- SMB1 compatibility affects error mapping for some lock failures.

Concurrency and lifetime:
- Granted locks live on `node->n_lock_list`; waiting locks live on `node->n_wlock_list`.
- List locks are held through `smb_llist_enter/exit`.
- `smb_lock_wait` deliberately drops `n_lock_list` while sleeping and reacquires it before returning.
- Waiting locks use `l_mutex`, `l_cv`, `l_blocked_by`, `l_flags`, and `l_conflicts`.
- Close/cancel paths broadcast on waiting lock CVs.
- Destruction wakes waiters one at a time with a small delay to preserve FIFO-ish behavior.

Filesystem relevance:
- Locks are mirrored into filesystem byte-range locks through `smb_fsop_frlock`.
- `smb_lock_posix_unlock` avoids dropping POSIX locks for ranges still covered by other SMB locks on the same ofile.
- `smb_nbl_conflict` participates in remove/rename/read/write conflict checks against vnode NBML state.

Edge cases and risks:
- Range overflow is rejected when `start + length` wraps.
- `NT_STATUS_FILE_CLOSED` is translated to `NT_STATUS_RANGE_NOT_LOCKED` in some lock failure paths.
- The code carefully avoids lock-order inversion with vnode `vnbllock` by not walking ofiles inside `smb_nbl_conflict`.
- Unlock POSIX subrange logic depends on lock list consistency while caller holds `n_lock_list`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_lock_byte_range.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_lock_byte_range.c

This file implements the legacy SMB1 `SMB_COM_LOCK_BYTE_RANGE` command. It is a thin request decoder and protocol wrapper around the core byte-range locking logic in `smb_lock.c`.

Key responsibilities:
- Emits DTrace start/done probes for `op__LockByteRange`.
- Decodes the SMB1 fixed parameter words: FID, byte count, and 32-bit offset.
- Looks up the target open file.
- Applies an exclusive byte-range lock with no wait.
- Encodes an empty SMB result on success.

Important functions:
- `smb_pre_lock_byte_range` and `smb_post_lock_byte_range` provide tracing hooks.
- `smb_com_lock_byte_range` performs decode, file lookup, lock call, error mapping, and response encoding.

Protocol behavior:
- This command only supports 32-bit offsets, so it is unsuitable for general locking in very large files.
- Lock type is always `SMB_LOCK_TYPE_READWRITE`.
- SMB1 lock PID uses the low 16 bits of `sr->smb_pid`.
- Timeout is zero, so conflicts fail immediately.

Dependencies:
- Uses `smbsr_decode_vwv`, `smbsr_lookup_file`, `smb_lock_range`, `smb_lock_range_error`, and `smbsr_encode_empty_result`.

Edge cases:
- Invalid FID returns `NT_STATUS_INVALID_HANDLE` / `ERRbadfid`.
- Any lock failure is delegated to `smb_lock_range_error`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_lock_byte_range.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_locking_andx.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_locking_andx.c

This file implements SMB1 `SMB_COM_LOCKING_ANDX`, which can acknowledge oplock breaks, cancel pending locks, unlock ranges, and lock ranges in one request.

Key responsibilities:
- Emits DTrace start/done probes for `op__LockingX`.
- Decodes lock type, oplock level, timeout, unlock count, and lock count.
- Validates target file and element counts.
- Handles oplock release acknowledgements.
- Rejects atomic lock-type conversion as unsupported.
- Supports normal and large-file lock element formats.
- Performs unlocks first, then locks.
- Rolls back already granted locks if a later lock in the same request fails.
- Encodes the AndX response.

Important functions:
- `smb_com_locking_andx` is the command implementation.
- Local `struct lreq` normalizes 32-bit and 64-bit lock/unlock elements into offset, length, and 16-bit PID.

Protocol behavior:
- `LOCKING_ANDX_SHARED_LOCK` maps to `SMB_LOCK_TYPE_READONLY`; absence maps to exclusive/read-write lock.
- `LOCKING_ANDX_OPLOCK_RELEASE` calls `smb1_oplock_ack_break`; if no lock/unlock elements are present, no reply is sent.
- `LOCKING_ANDX_CHANGE_LOCK_TYPE` returns `ERROR_ATOMIC_LOCKS_NOT_SUPPORTED`.
- `LOCKING_ANDX_LARGE_FILES` requires dialect `NT_LM_0_12` or later.
- `LOCKING_ANDX_CANCEL_LOCK` cancels one matching pending lock using the first lock vector entry.

Dependencies:
- Lock operations are delegated to `smb_unlock_range`, `smb_lock_range`, and `smb_lock_range_cancel`.
- Element parsing uses `smb_mbc_decodef`.
- Response uses `smbsr_encode_result`.

Edge cases and protections:
- `smb_lock_max_elem` limits each vector to 1024 elements to bound allocation.
- Decode failure returns the Windows-compatible `ERRSRV/ERRerror`.
- Failed unlock returns `NT_STATUS_RANGE_NOT_LOCKED` / `ERROR_NOT_LOCKED`.
- Failed lock rolls back locks already acquired in the same request.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_locking_andx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_logoff_andx.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_logoff_andx.c

This file implements SMB1 `SMB_COM_LOGOFF_ANDX`, the inverse of session setup. It logs off the SMB user referenced by the request UID.

Key responsibilities:
- Emits DTrace start/done probes for `op__LogoffX`.
- Validates that `sr->uid_user` exists.
- Calls `smb_user_logoff` to close user-owned state and invalidate the user session.
- Encodes a minimal AndX response.

Important functions:
- `smb_pre_logoff_andx` and `smb_post_logoff_andx` provide tracing hooks.
- `smb_com_logoff_andx` performs validation, user logoff, and response encoding.

Protocol behavior:
- Invalid or missing UID returns `ERRSRV/ERRbaduid`.
- Success response has WordCount 2, passes through `sr->andx_com`, and uses `-1` for the next offset.

Dependencies:
- Depends on higher-level user/session cleanup in `smb_user_logoff`.
- Response formatting is via `smbsr_encode_result`.

Edge cases:
- The file intentionally does not decode request body fields beyond relying on common SMB dispatch state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_logoff_andx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_mangle_name.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_mangle_name.c

This file implements DOS/8.3 filename validation, short-name mangling, mangled-name detection, and unmangling by directory scan.

Key responsibilities:
- Detects invalid SMB/DOS filenames and reserved DOS device names.
- Determines whether a filename needs 8.3 mangling.
- Generates deterministic mangled names using a base-36 encoding of inode/FID.
- Detects whether an incoming name looks like a mangled 8.3 name.
- Resolves a mangled name back to the real directory entry by scanning the directory and remangling each candidate.

Important functions:
- `smb_is_invalid_filename` rejects control/special invalid characters except spaces and checks reserved DOS names.
- `smb_is_reserved_dos_name` recognizes `CON`, `PRN`, `AUX`, `NUL`, `CLOCK$`, `COM1`-`COM9`, and `LPT1`-`LPT9`, including extension forms like `NUL.txt`.
- `smb_needs_mangled` applies 8.3 naming rules, dot counts, invalid/special character checks, and leading-dot handling.
- `smb_generate_mangle` produces a `~` plus base-36 suffix.
- `smb_maybe_mangled` checks validity, tilde placement, dot count, and 8.3 length.
- `smb_mangle` constructs uppercase DOS-compatible base and extension portions.
- `smb_unmangle` scans directory entries, validates UTF-8, remangles each name with its inode, and compares case-insensitively.

Filesystem relevance:
- `smb_unmangle` uses `smb_vop_readdir` against the directory vnode.
- It uses directory entry inode numbers as the unique input to `smb_mangle`.
- Returned names are real filesystem names copied into caller-provided buffers.

Edge cases and protections:
- `.` and `..` are never mangled.
- Leading dots force mangling except for `.` and `..`.
- Invalid DOS characters are dropped during mangling; selected special characters are converted to `_`.
- Non-UTF-8 directory names are skipped during unmangling.
- Partial directory records are defensively skipped by restarting at the current offset.
- `flags` in `smb_unmangle` is retained only for caller compatibility and is unused.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_mangle_name.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_mbuf_marshaling.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_mbuf_marshaling.c

This file provides SMB mbuf-chain marshaling and unmarshaling. It is the format-string engine used to encode and decode SMB protocol fields, strings, vardata blocks, UIOs, mbufs, and time formats.

Key responsibilities:
- Decodes data from `mbuf_chain_t` using SMB-specific format strings.
- Encodes data into `mbuf_chain_t` with dynamic mbuf growth.
- Supports SMB1 and SMB2 signatures.
- Handles little-endian 8/16/32/64-bit scalar access across mbuf boundaries.
- Handles special “odd” 64-bit field layout used by SMB lock large-file records.
- Converts OEM and UTF-16 strings to/from internal UTF-8.
- Supports alignment, skip, peek, poke, copy, and append operations.
- Exposes direct UIO/vardata views over mbuf data.

Important public functions:
- `smb_mbc_vdecodef`, `smb_mbc_decodef`, `smb_mbc_peek`.
- `smb_mbc_vencodef`, `smb_mbc_encodef`, `smb_mbc_poke`.
- `smb_mbc_copy`.
- `smb_mbc_put_mem`.
- `smb_mbc_put_align`.

Format-string highlights:
- `%` supplies `smb_request_t` and determines Unicode mode.
- `M` and `N` validate/emit SMB1 and SMB2 signatures.
- `b/c/w/l/q/Q` handle scalar and byte-buffer fields.
- `u/s/U/L/A/S/P` handle OEM/Unicode/tagged strings.
- `B/D/V` handle vardata blocks and UIO setup.
- `Y/y` convert DOS date/time ordering variants.
- `.` skips or emits zero padding; `,` is Unicode-aware padding/skipping.
- `C/m` represent mbuf-chain and mbuf transfer paths, though mbuf decode is not implemented.

Memory and lifetime:
- Encode paths allocate mbufs as needed up to `mbc->max_bytes`.
- Decoded strings are allocated from the request storage arena with `smb_srm_zalloc`.
- Temporary conversion buffers are allocated with `smb_mem_alloc/zalloc/realloc` and freed before return.
- `mbc_marshal_put_mbufs` always consumes or frees the mbuf chain passed to it.
- `mbc_marshal_put_uio` wraps existing UIO buffers as external mbufs with a no-op free callback.

Edge cases and protections:
- `MBC_ROOM_FOR` and `mbc_marshal_make_room` enforce chain bounds.
- Unicode strings align to a 16-bit boundary before reading/writing.
- OEM string decode caps unspecified strings at 0xffff bytes.
- `smb_mbc_poke` and `smb_mbc_peek` use shadow chains so original offsets are unchanged.
- `mbc_marshal_get_mbufs` is explicitly not implemented, so decode formats requiring raw mbuf extraction fail.
- `smb_mbc_copy` validates source offset and length before copying.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_mbuf_marshaling.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_mbuf_util.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_mbuf_util.c

This file implements SMB server mbuf and mbuf-chain allocation/manipulation. It adapts BSD-style mbuf operations to illumos SMB server needs and backs protocol marshaling and network I/O.

Key responsibilities:
- Creates and destroys kmem caches for `mbuf_chain_t`, `mbuf_t`, and mbuf clusters.
- Allocates/frees `mbuf_chain_t`.
- Allocates mbufs from memory buffers, external buffers, kmem-backed buffers, or chains sized for large I/O.
- Builds UIO/iovec views over mbuf chains.
- Trims, attaches, appends, shadows, prepends, adjusts, and frees mbufs.
- Provides cluster allocation/free/reference callbacks used by mbuf macros and network wrapping.

Important functions:
- `smb_mbc_init`, `smb_mbc_fini`.
- `smb_mbc_alloc`, `smb_mbc_free`.
- `smb_mbuf_get`, `smb_mbuf_alloc_ext`, `smb_mbuf_alloc_kmem`, `smb_mbuf_alloc_chain`.
- `smb_get_vdb`.
- `smb_mbuf_allocate`.
- `smb_mbuf_mkuio_cont`, `smb_mbuf_mkuio`.
- `smb_mbuf_trim`.
- `MBC_LENGTH`, `MBC_MAXBYTES`, `MBC_SETUP`, `MBC_INIT`, `MBC_FLUSH`.
- `MBC_ATTACH_MBUF`, `MBC_APPEND_MBUF`, `MBC_ATTACH_BUF`, `MBC_SHADOW_CHAIN`.
- `m_adjust`, `m_prepend`, `m_free`, `m_freem`.
- `smb_mbuf_alloc`, `smb_mbuf_free`, `smb_mbufcl_alloc`, `smb_mbufcl_free`, `smb_mbufcl_ref`.

Performance and allocation behavior:
- `smb_mbuf_alloc_chain` avoids overusing oversized kmem allocations by splitting at `kmem_max_cached`.
- Large kmem-backed mbufs are prepended so shorter front segments are more likely available for copy-heavy protocol headers.
- `smb_mbuf_mkuio_cont` can append mbuf segments after prefilled iovec entries, used by SMB2 signing paths.

Edge cases and protections:
- `MBC_SHADOW_CHAIN` rejects negative offsets/lengths and integer wraparound.
- `smb_mbuf_mkuio_cont` returns `E2BIG` when iovec space is insufficient and `EFAULT` when the mbuf chain is too short.
- `m_adjust` supports only head trimming; tail trimming is handled by `smb_mbuf_trim`.
- `m_prepend` allocates a new mbuf if leading space is insufficient.
- External-buffer free callbacks are responsible for freeing backing storage; no-op callbacks are used for borrowed buffers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_mbuf_util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_negotiate.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_negotiate.c

This file implements SMB1 negotiate handling, including dialect selection, SMB2 upgrade negotiation, SMB1 capability advertisement, security mode setup, and dialect-specific response encoding.

Key responsibilities:
- Maintains SMB dialect string-to-code mapping.
- Parses client dialect proposals from an SMB1 negotiate request.
- Chooses the highest supported dialect allowed by server min/max protocol configuration.
- Handles SMB2 negotiation through an SMB1 negotiate request when SMB2 dialects are selected.
- Encodes SMB1 negotiate responses for core, LanMan, NT LM 0.12, and NT LM 0.12 extended-security variants.
- Sets session receive buffer sizes for old DOS/LanMan vs NT dialect behavior.
- Updates session state from established to negotiated.

Important functions:
- `smb1_newrq_negotiate` is called directly by the reader thread for the initial SMB1 negotiate and manually decodes enough request framing to dispatch negotiation.
- `smb_pre_negotiate` parses dialect strings, filters by configured protocol min/max, and stores selected dialect/index in `sr->sr_negprot`.
- `smb_com_negotiate` validates session state, handles unsupported dialects, negotiates SMB2 when appropriate, and emits dialect-specific SMB1 responses.
- `smb_post_negotiate` clears negotiation scratch storage.
- `smb_xlate_dialect` maps dialect strings to internal constants.

Negotiation behavior:
- SMB2 dialect proposals (`SMB 2.002`, `SMB 2.???`) are recognized only if max protocol allows SMB2.
- SMB1 dialects are skipped if min protocol is above SMB1.
- `NT_LM_0_12` advertises capabilities from `smb1srv_capabilities`.
- Extended security is used only when the client requests it and the server capability includes it.
- If extended security is not used, the NetBIOS domain is encoded as Unicode into a temporary message buffer.
- After successful SMB1 negotiation, `session->newrq_func` switches to `smb1sr_newrq`.

Dependencies:
- Uses mbuf marshaling for header/request decode.
- Uses `smbsr_encode_result` for response construction.
- Uses `ksocket_setsockopt` to tune receive buffer sizes.
- Calls `smb1_negotiate_smb2` for SMB2 upgrade path.

Edge cases and protections:
- Re-negotiation after session leaves `SMB_SESSION_STATE_ESTABLISHED` is rejected.
- No supported dialect logs a note and drops the virtual circuit.
- Older dialects advertise conservative max buffer/MPX/raw values.
- SMB signing bits are set only if encrypted passwords and server signing config allow them.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_negotiate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_net.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_net.c

This file implements SMB server socket I/O wrappers and mbuf-based send/receive paths over illumos `ksocket`.

Key responsibilities:
- Creates, shuts down, and closes kernel sockets.
- Receives fixed-size buffers and mbuf chains.
- Serializes sends per SMB session through `smb_txlst_t`.
- Sends mbuf chains either by wrapping mbufs in STREAMS mblks for zero-copy or by scatter/gather UIO copying.
- Converts mbuf chains into iovec arrays using helpers from `smb_mbuf_util.c`.

Important functions:
- `smb_socreate`, `smb_soshutdown`, `smb_sodestroy`.
- `smb_sorecv` receives exactly the requested byte count using `MSG_WAITALL`.
- `smb_net_recv_mbufs` allocates an mbuf chain, builds a UIO over it, and receives into it.
- `smb_net_txl_constructor`, `smb_net_txl_destructor` initialize/destroy transmit serialization state.
- `smb_net_wrap_mbuf` wraps one mbuf as an `mblk_t` with a `frtn_t` callback.
- `smb_net_send_mblks` sends mblk chains with `ksocket_sendmblk`.
- `smb_net_send_uio` sends mbuf chains through `ksocket_sendmsg`.
- `smb_net_send_mbufs` selects mblk or UIO send path based on `smb_send_mblks`.

Concurrency and lifetime:
- `s->s_txlst.tl_active` serializes sends so only one thread writes a session socket at a time.
- Send waiters sleep on `tl_wait_cv`.
- UIO send path always frees the mbuf chain before returning.
- Mblk send path transfers mbuf ownership to STREAMS free callbacks; cleanup handles partial wrap failures.
- `smb_soshutdown` is used to interrupt blocked receive/send paths before socket close.

Performance behavior:
- Default send path is UIO scatter/gather copying.
- `smb_send_mblks` enables optional zero-copy mblk wrapping for configurations where `ksocket_sendmblk` performs better.
- Local stack iovec capacity is 16; larger sends allocate an `smb_vdb_t`-sized buffer.

Edge cases and protections:
- `smb_sorecv` returns error if `ksocket_recv` fails or returns short.
- `smb_net_recv_mbufs` frees allocated mbufs on receive/setup errors.
- `smb_net_wrap_mbuf` converts non-external mbufs to external storage when there is not enough trailing space to store `frtn_t`.
- `smb_net_send_mblks` carefully detaches/frees unwrapped remainder mbufs on wrap failure.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_net.c -->