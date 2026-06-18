# Group Research: group_523_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_25188c85ff72

Read completely under `Docs/research_subset_a.md` scope:
- `rrwlock.c` 396 lines
- `sa.c` 2194 lines
- `sha256.c` 91 lines
- `skein_zfs.c` 101 lines

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/rrwlock.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/rrwlock.c

This file implements ZFS re-entrant reader/writer locks (`rrwlock_t`) and reader-mostly locks (`rrmlock_t`). The core `rrwlock_t` behaves like a reader/writer lock, but permits a thread that already holds a read lock to acquire another read hold even when writers are waiting.

Core responsibilities:
- Maintains per-thread read-lock tracking with TSD nodes (`rrw_node_t`) only when needed for re-entrant detection or when `track_all` is enabled.
- Tracks anonymous readers with `rr_anon_rcount` on the normal fast path, and linked readers with `rr_linked_rcount` when writers are pending or all readers must be tracked.
- Provides initialization, teardown, generic enter, read enter, priority read enter, write enter, exit, and held-state queries for `rrwlock_t`.
- Gives waiting writers priority over new non-reentrant readers once anonymous readers have drained.
- Allows explicit priority read acquisition through `rrw_enter_read_prio()` for cross-thread cases where normal per-thread reentrancy detection cannot prove the relationship.
- Uses `rrw_tsd_destroy()` to panic if a thread exits while still carrying rrw TSD state.
- Implements `rrmlock_t` as an array of `rrwlock_t` instances to reduce read-side contention by hashing readers across locks while making writers acquire every underlying lock.

Important control-flow notes:
- `rrw_enter_read_impl()` is the central read acquisition path. It has a kernel non-debug fast path that increments `rr_anon_rcount` directly when no writer is active/wanted and `track_all` is false.
- If a writer is waiting while anonymous readers still exist, new readers are allowed because they might be re-entrant readers that cannot yet be identified. Once anonymous readers drain, only tracked re-entrant readers or priority readers may bypass a waiting writer.
- `rrw_enter_write()` sets `rr_writer_wanted` while waiting for anonymous readers, linked readers, and any current writer to clear, then records `curthread` as the owner.
- `rrw_exit()` removes linked TSD state when present, otherwise drops anonymous reader state, or clears the writer owner. It broadcasts waiters when the relevant count reaches zero or a writer exits.
- `rrw_held(RW_READER)` is exact only when `track_all` is enabled; otherwise anonymous readers mean it may return true because some thread holds a read lock.
- `rrm_enter_read()` hashes `curthread` to one underlying lock, while `rrm_enter_write()` serially acquires all underlying locks. `rrm_exit()` releases all locks for a writer or the hashed lock for a reader.

Key dependencies:
- ZFS refcount helpers for reader accounting and tagged debug tracking.
- Illumos mutexes, condition variables, TSD APIs, and `curthread`.
- `rrwlock.h` / `rrmlock_t` definitions, including `RRM_NUM_LOCKS`.

Risk-sensitive invariants:
- Writers are not re-entrant and cannot be acquired while the current thread already owns the writer side.
- Read-to-write or write-to-read lock upgrades are not supported by this implementation.
- TSD nodes must be added and removed in balance with linked reader refcounts; a leaked node causes thread-exit panic.
- `rrmlock_t` read locks must be released by the same thread that acquired them because the hash is based on `curthread`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/rrwlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sa.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sa.c

This file implements ZFS System Attributes (SA): a generic per-objset mechanism for storing typed attributes in dnode bonus buffers and, when needed, spill blocks. It manages persistent attribute registration, compact layout tables, in-memory lookup indexes, byteswapping, handle lifetime, and the public lookup/update/remove APIs used by ZPL and other DMU consumers.

Core responsibilities:
- Defines the SA storage model where attributes are packed into a bonus buffer and optionally moved into a spill block when the bonus area cannot contain both data and the spill block pointer.
- Maintains per-objset `sa_os_t` state attached to `objset_t`, including attribute registration tables, layout AVL trees by number and hash, cached index tables, update callback, and master ZAP object IDs.
- Supports legacy ZPL objects through fixed `sa_legacy_attrs` and `sa_legacy_zpl_layout`, allowing old `DMU_OT_ZNODE` bonus formats to coexist with newer `DMU_OT_SA` layouts.
- Registers and reconstructs persistent attribute metadata from ZAP objects (`SA_REGISTRY`, `SA_LAYOUTS`) in `sa_setup()`, and tears it all down in `sa_tear_down()`.
- Builds compact layouts from ordered attribute lists, assigns persistent layout numbers, and caches layout-index tables that map attribute IDs to offsets and variable-length indexes.
- Handles SA bonus/spill indexing, lazy spill buffer holding, spill resizing, spill removal when no longer needed, and bonus length/bonus type updates.
- Provides bulk and single-attribute lookup/update/remove APIs: `sa_lookup()`, `sa_bulk_lookup()`, `sa_update()`, `sa_bulk_update()`, `sa_update_from_cb()`, `sa_remove()`, `sa_size()`, and template replacement helpers.
- Performs SA byteswapping on first access when on-disk SA data is from the opposite endian order, using registered byteswap functions for each attribute.
- Provides handle lifecycle APIs over DMU bonus buffers, including shared handle lookup/installation through dbuf user data and destruction that releases index table holds and dbuf holds.
- Includes kernel-only ZPL upgrade helper `sa_add_projid()` to rewrite old objects with a project ID attribute at a layout suitable for quota accounting.

Important control-flow notes:
- `sa_setup()` is the objset-level constructor. It creates `sa_os_t`, discovers registry/layout ZAP objects, builds the attribute table from caller registration plus legacy/foreign persisted registrations, loads layout entries, and installs legacy ZPL layouts for filesystem objsets.
- `sa_attr_table_setup()` assigns stable attribute IDs. Legacy ZPL names keep their fixed historical IDs; persisted registry entries keep their encoded IDs; new caller-provided attributes get new IDs and are later persisted by `sa_attr_register_sync()`.
- `sa_attr_op()` is the central lookup/update dispatcher. It checks the bonus index first, lazily opens the spill block if needed, copies data for lookups, updates in-place when size is unchanged, and delegates add/remove/size-changing replacement to `sa_modify_attrs()`.
- `sa_build_layouts()` rewrites the entire packed attribute set. It computes header/data sizes, decides where spill begins, sizes bonus and spill storage, copies attribute data, creates or reuses layout numbers, updates SA headers, rebuilds index tables, and removes an obsolete spill block if all data fits in bonus again.
- `sa_find_sizes()` determines packed data size, header size, variable-length header overhead, and the first attribute that would spill from the bonus buffer.
- `sa_modify_attrs()` snapshots existing bonus/spill bytes, reconstructs a complete attribute descriptor list with one attribute added, removed, or replaced, then calls `sa_build_layouts()` to rewrite both buffers consistently.
- `sa_find_idx_tab()` reuses cached index tables when the layout and variable-length sizes match; otherwise it iterates attributes with `sa_attr_iter()` and builds a new offset table.
- `sa_build_index()` is called when a handle is created or buffers are rewritten. It performs delayed byteswap if needed and attaches the correct index table to the handle for bonus or spill.
- `sa_byteswap()` swaps the SA header, variable-length array, and each attribute payload according to the per-attribute byteswap class. Spill buffers are thawed/re-frozen around mutation.
- `sa_replace_all_by_template_locked()` registers unregistered attributes if needed, then performs full-layout construction. It is the intended fast path for new object creation or full legacy-to-SA conversion.

Key dependencies:
- DMU/dbuf/dnode APIs for bonus holds, spill holds, dirty marking, bonus sizing, bonus type conversion, spill block sizing/removal, object info, and object size.
- ZAP APIs for persistent attribute registry and layout tables.
- AVL trees and lists for layout lookup/caching, plus ZFS refcounts for index table lifetime.
- ARC buffer freeze/thaw/release behavior for safely byteswapping spill buffers.
- ZPL/znode/ACL code under `_KERNEL` for legacy object conversion and project quota layout upgrades.

Risk-sensitive invariants:
- Layout numbers and attribute IDs are persistent on-disk metadata; legacy ZPL layout number 0 and dummy empty layout 1 have special meaning.
- Attribute payloads are 8-byte aligned while packed, and header size must match the number of variable-length attributes in the selected layout.
- Duplicate attributes are not allowed in a layout; adding, removing, or changing the length of a variable-size attribute rewrites the whole attribute set.
- Spill placement must preserve room for the spill block pointer in the bonus buffer.
- `sa_handle_t` index table holds must be released exactly once on handle destruction or rebuild.
- Byteswapping depends on the objset SA registry and layout table being available; SA data is not self-describing enough for generic ZFS byteswap handling.
- `sa_add_projid()` must coordinate znode locks, cached ACL state, and object bonus type conversion so project quota accounting can use fixed expected offsets after upgrade.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sha256.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sha256.c

This file provides ABD-backed SHA checksum routines for ZFS block checksums. It adapts the system SHA-2 implementation to ZFS `abd_t` buffers and writes results into `zio_cksum_t`.

Core responsibilities:
- Defines `sha_incremental()` as an `abd_iterate_func()` callback that feeds each contiguous ABD segment into `SHA2Update()`.
- Implements `abd_checksum_SHA256()` for the historical ZFS SHA-256 checksum.
- Implements `abd_checksum_SHA512_native()` using SHA-512/256.
- Implements `abd_checksum_SHA512_byteswap()` by computing the native SHA-512/256 checksum and byte-swapping each 64-bit checksum word.

Important control-flow notes:
- All checksum functions iterate the ABD from offset 0 for the requested size; they ignore `ctx_template`.
- `abd_checksum_SHA256()` initializes `SHA2_CTX` for SHA-256, finalizes into a temporary `zio_cksum_t`, then forces each output word to big endian with `BE_64()`.
- The explicit big-endian conversion in `abd_checksum_SHA256()` preserves compatibility with an older private ZFS SHA-256 implementation that always emitted big-endian words and had no byteswap variant.
- `abd_checksum_SHA512_native()` initializes `SHA2_CTX` for `SHA512_256` and finalizes directly into the caller's checksum.

Key dependencies:
- ABD iteration API for walking possibly scattered block buffers.
- Illumos SHA-2 implementation and `SHA2_CTX`.
- ZFS checksum word representation in `zio_cksum_t`.

Risk-sensitive invariants:
- SHA-256 output endian behavior is on-disk compatibility behavior and must not be "normalized" to host-endian output.
- The byteswap variant swaps only after computing the native SHA-512/256 digest.
- `abd_iterate_func()` callback failures are not expected here; the callback always returns 0.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sha256.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/skein_zfs.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/skein_zfs.c

This file provides ABD-backed Skein MAC checksum support for ZFS. It computes 256-bit outputs from a Skein-512 context template seeded with ZFS checksum salt.

Core responsibilities:
- Defines `skein_incremental()` as an ABD iteration callback that feeds each contiguous buffer segment to `Skein_512_Update()`.
- Implements `abd_checksum_skein_native()` by copying a preinitialized Skein context template, iterating the ABD contents through it, finalizing into `zio_cksum_t`, and zeroing the working context.
- Implements `abd_checksum_skein_byteswap()` by computing the native Skein checksum and byte-swapping the four 64-bit checksum words.
- Provides `abd_checksum_skein_tmpl_init()` to allocate and initialize a keyed Skein-512 context template from `zio_cksum_salt_t`.
- Provides `abd_checksum_skein_tmpl_free()` to zero and free a previously allocated template.

Important control-flow notes:
- `abd_checksum_skein_native()` requires a non-NULL `ctx_template` and asserts that requirement.
- The template is copied per checksum operation so callers can reuse the initialized keyed state without mutation.
- `Skein_512_InitExt()` is configured for `sizeof (zio_cksum_t) * 8` output bits and uses the salt bytes as key material.
- The byteswap implementation relies on Skein being internally endian-insensitive, so only the final `zio_cksum_t` words are swapped.

Key dependencies:
- ABD iteration API for block-buffer traversal.
- Skein-512 implementation and context structures.
- ZFS checksum salt and checksum word types.
- Kernel memory allocation and zeroing helpers.

Risk-sensitive invariants:
- The context template must remain valid for the duration of checksum calls and must be freed through `abd_checksum_skein_tmpl_free()`.
- Working and template contexts contain keyed material and are explicitly zeroed before release.
- Output width must remain 256 bits to match `zio_cksum_t` and ZFS on-disk checksum expectations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/skein_zfs.c -->