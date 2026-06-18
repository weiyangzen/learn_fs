# Group Research: group_545_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_d_cba942812279

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All six requested source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/devid_cache.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/devid_cache.c

## Purpose

`devid_cache.c` implements the kernel-side device-id cache for illumos. It maintains the in-memory mapping between persistent physical device paths and DDI device identifiers, serializes that mapping to `/etc/devices/devid_cache` through the `nvf` cache-file framework, and provides lookup paths used by layered device consumers that need stable device identity even after hardware has moved.

The file is also responsible for controlled "discovery": expensive device-tree probing used when a requested devid is not currently reachable through cached paths.

## Main Interfaces

- `devid_cache_init()` registers the nvf backing file, initializes the cache list, and sets up discovery synchronization.
- `devid_cache_read()` loads persisted cache contents unless disabled by `devid_cache_read_disable`.
- `e_ddi_devid_discovery()` serializes full-tree or driver-targeted discovery attempts using `devid_discovery_mutex` and `devid_discovery_cv`.
- `e_devid_cache_register()`, `e_devid_cache_pathinfo()`, and `e_devid_cache_unregister()` add, refresh, or detach devinfo references for path/devid mappings.
- `devid_cache_cleanup()` removes cache entries that never registered in the current boot.
- `e_devid_cache_to_devt_list()` returns sorted, duplicate-collapsed `dev_t` lists for a devid and minor name.
- `e_devid_cache_free_devt_list()` frees lists returned by `e_devid_cache_to_devt_list()`.
- `e_devid_cache_path_to_devid()` performs reverse lookup from a full path, or from parent path plus unit address, to a duplicated devid.

## Cache Format And State

The cache file stores an nvlist keyed by device path. Each child nvlist has a byte-array `DP_DEVID_ID` value containing the packed `ddi_devid_t`. `devid_cache_unpack_nvlist()` validates each decoded devid before inserting an `nvp_devid_t` into the cache list. `devid_cache_pack_list()` walks the list and rebuilds the nvlist for persistence.

Each in-memory entry tracks:

- `nvp_devpath`: persistent path string.
- `nvp_devid`: kernel copy of the device id.
- `nvp_flags`: whether the entry has a current devinfo pointer and whether it registered this boot.
- `nvp_dip`: current devinfo pointer when available.

The list is protected by `nvf_lock(dcfd_handle)`, with writers used for mutation and readers for lookup.

## Registration Behavior

`e_devid_cache_register_cmn()` accepts either a `dip` or an explicit path. It duplicates the path and devid, then searches for an existing path match:

- If the existing path has no devid or an invalid devid, it replaces the devid.
- If the path already maps to the same devid, it marks the entry registered and associates the `dip`.
- If the path maps to a different valid devid, it logs both encoded devids, removes the stale entry, and inserts the new mapping.
- New or replaced mappings mark the nvf cache dirty and wake the nvf daemon unless writes are disabled.

This enforces the invariant that one path maps to one devid, while allowing one devid to map to multiple paths.

## Discovery Model

Discovery is intentionally rate-limited and serialized. Before root I/O is initialized, `e_devid_do_discovery()` consumes `devid_discovery_boot`. After boot, it honors `devid_discovery_postboot_always`, then `devid_discovery_postboot`, then the `devid_discovery_secs` minimum interval.

Pre-root discovery holds likely installed drivers using the devid's driver hint, drivers marked `DN_DEVID_REGISTRANT`, and a legacy list containing `sd` and `ssd`. Post-root discovery invokes `ndi_devi_config()` on the root node with persistent config flags and optionally `NDI_DRV_CONF_REPROBE`.

## Lookup Flow

`e_devid_cache_to_devt_list()` first calls `e_devid_cache_devi_path_lists()` under the cache read lock. That helper returns held devinfo nodes for attached devices and path strings for stale or unattached entries. Path strings are duplicated before releasing the cache lock.

The function then:

1. Enumerates matching minor nodes from held devinfo nodes.
2. Resolves cached paths with `e_ddi_hold_devi_by_path()`.
3. Verifies newly attached devices still register the requested devid.
4. Builds a `dev_t` array, retrying with a larger allocation when necessary.
5. Bubble-sorts the result and collapses duplicates before returning it.

This design avoids returning transient implementation duplicates to consumers such as SVM namespace code.

## Reverse Path Lookup

`e_devid_cache_path_to_devid()` supports two modes:

- Full path exact match when `ua == NULL`.
- Parent-path plus unit-address match when `ua != NULL`, treating the node name between the final slash and `@` as unknown.

On match it duplicates the cached devid for the caller and optionally returns the node name in `nodenamebuf`.

## Dependencies

This file depends on DDI/NDI device tree APIs, MDI pathinfo support, `nvf` cache-file management, nvlist packing, devinfo hold/release helpers, and devid encode/compare/validate routines. It also depends on the wider device configuration system through `devnamesp`, `devcnt`, `ddi_hold_installed_driver()`, and `ndi_devi_config()`.

## Notable Invariants And Audit Notes

- `nvf_lock(dcfd_handle)` protects the cache list and must be held according to read/write intent.
- Registered `nvp_dip` pointers are only used after parent `ndi_devi_tryenter()` succeeds and the devinfo node is held.
- Discovery is single-flight; waiters block until the active discovery completes.
- Returned devinfo holds from cache scans are released after devt enumeration.
- `devid_cache_cleanup()` marks stale removals dirty but sets `is_dirty = 0` in that branch, so the final `nvf_wake_daemon()` path is not reached for cleanup removals. That is a focused audit point because it may affect persistence timing.
- `e_devid_cache_free_devt_list()` frees with `ndevts * sizeof (dev_t *)` while allocation uses `sizeof (dev_t)`. This is harmless only if those sizes match on the target ABI.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/devid_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/devpolicy.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/devpolicy.c

## Purpose

`devpolicy.c` implements illumos device privilege policy lookup and replacement. It keeps a generation-counted table of privilege requirements indexed by major number and minor selector, and returns held `devplcy_t` objects for device vnode access checks.

The policy system is fail-safe at boot: the initial default policy requires all privileges until userland loads a real policy table.

## Main Interfaces

- `devpolicy_init()` initializes locks and creates `nullpolicy`, `dfltpolicy`, and `netpolicy`.
- `dpget()`, `dphold()`, and `dpfree()` allocate and reference-count `devplcy_t`.
- `devpolicy_find()` returns a held policy for a device vnode.
- `devpolicy_load()` validates, parses, and atomically installs a new policy table from userland.
- `devpolicy_get()` copies the current table to userland.
- `devpolicy_getbyname()` resolves a device pathname and returns its effective read/write privilege sets.
- `devpolicy_priv_by_name()` builds an ad hoc policy from privilege-name strings for private minor-node creation.

## Data Model

The global policy table is an array of `tableent_t`, sorted by major number. Each table entry points to a linked list of `devplcyent_t` records. A policy entry can select minors by:

- explicit minor-number range plus block/char type,
- exact minor name,
- simple wildcard minor name with a single `*`,
- all minors via the special `*` expression.

Each policy entry references a `devplcy_t` containing read and write privilege sets and a generation number. `nullpolicy` represents no privilege checks beyond DAC; `dfltpolicy` applies when no specific rule matches; `netpolicy` defaults network drivers to `PRIV_NET_RAWACCESS`.

## Lookup Behavior

`devpolicy_find()` maps clone devices by using the minor as the effective major when `maj == clone_major`. It acquires `policyrw` as reader, binary-searches the major table, and calls `match_policy()` on the matching bucket. If there is no table entry, it asks `devfs_devpolicy()` and then falls back to `netpolicy` or `dfltpolicy`.

`match_policy()` walks the minor list in order. Already-expanded numeric rules compare minor number and vnode type directly. String rules lazily obtain the minor name through `ddi_lyr_get_minor_name()`. Exact string rules may be upgraded in place to numeric minor ranges via `rw_tryupgrade(&policyrw)`, avoiding future string expansion. Wildcard rules are simple single-star prefix/suffix matches.

## Loading And Validation

`devpolicy_load()` requires userland to pass an array of `devplcysys_t` entries with the kernel's exact structure size, at least one entry, and no more than `maxdevpolicy`. Entry zero must be the default policy marker `DEVPOLICY_DFLT_MAJ`.

The remaining entries must be sorted by major number, with explicit rules before wildcard rules, and wildcard rules ordered longest first. The loader rejects duplicate default markers, overlong minor names, and expressions with more than one `*`.

The new table is fully allocated and parsed before it is published. `policymutex` serializes concurrent loads and `policyrw` writer mode performs the atomic swap. `devplcy_gen` is incremented so cached snode policies can detect stale generations.

## Export Behavior

`devpolicy_get()` first copies out the total item count, then fails with `ENOMEM` if the caller's provided item count is too small. Otherwise it serializes `dfltpolicy` and all table entries back into `devplcysys_t` form, preserving wildcard and numeric range forms.

`devpolicy_getbyname()` resolves a user pathname with `lookupname()`, requires a block or character vnode, gets the effective policy via `devpolicy_find()`, and copies only the read/write privilege sets to userland.

## Dependencies

The file depends on kernel privilege set operations, vnode/spec vnode state, devfs policy hooks, layered minor-name lookup, auditing through `audit_devpolicy()`, and DV node policy integration via `devfs_devpolicy()`.

## Notable Invariants And Audit Notes

- `policyrw` protects the active table and default/null policy pointers.
- `policymutex` protects allocation of next-generation policies and serializes table replacement.
- `devpolicy_find()` returns a held policy; callers must release it with `dpfree()`.
- Userland sorting is part of the ABI contract and is revalidated in-kernel before install.
- `match_policy()` can return `dfltpolicy` early if minor-name lookup fails; the nearby comment says `mname` may be set on failure, making this a small leak candidate worth checking against `ddi_lyr_get_minor_name()` semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/devpolicy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dkioc_free_util.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dkioc_free_util.c

## Purpose

`dkioc_free_util.c` provides shared helpers for the `DKIOCFREE` ioctl, which lets callers tell block devices that byte ranges are no longer needed. It is built for both kernel use and `libzpool` builds, and focuses on safe copyin, variable-length list lifetime, extent alignment, validation, and segmentation for devices with trim/free constraints.

## Main Interfaces

- `dfl_copyin()` copies a variable-length `dkioc_free_list_t` from user or kernel space and validates the extent count.
- `dfl_free()` releases a list allocated or consumed by these helpers.
- `dfl_iter()` consumes a free-list request, validates and adjusts it to `dkioc_free_info_t` device limits, and invokes a caller callback with one or more conforming lists.

Private helpers are:

- `adjust_exts()` to align starts and lengths and validate device bounds.
- `process_range()` to build a new list from a contiguous subset of extents while dropping zero-length entries.
- `split_extent()` to split one oversized extent into callback-sized single-extent requests.

## Copyin And Lifetime

`dfl_copyin()` handles two caller models. With `FKIOCTL`, the input pointer is already in kernel space and the function copies from it directly. Otherwise it first copies only `dfl_num_exts`, validates it against `DFL_COPYIN_MAX_EXTS`, allocates the precise `DFL_SZ(num_exts)` buffer, and copies the full list. It also rechecks that the copied structure still has the expected `dfl_num_exts`.

`dfl_iter()` is explicitly consuming: after successful callback transfer of an unmodified list, the callback owns it; otherwise `dfl_iter()` frees the original list before returning. Newly allocated sublists are owned by the callback.

## Validation And Alignment

`dfl_iter()` validates device constraints before touching extents:

- `dfi_bshift` must represent a block size from 512 bytes through `1 << 30`.
- `dfi_max_bytes`, `dfi_align`, and `dfi_max_ext_bytes` must be block-size aligned when nonzero.
- `dfi_align` must be nonzero.
- A single-extent maximum cannot exceed the total-request maximum.

`adjust_exts()` applies `dfl_offset` before alignment, detects overflow in start and end calculations, rejects extents beyond `max_off`, rounds starts up to `dfi_align`, rounds ends down to the device block size, then stores adjusted starts relative to `dfl_offset`. Extents that become too small are converted to zero length rather than failing the whole ioctl.

## Segmentation Behavior

After adjustment, `dfl_iter()` walks original extent order while accumulating a request window. It emits callback batches when:

- one extent exceeds `dfi_max_ext_bytes`,
- adding an extent would exceed `dfi_max_bytes`,
- adding an extent would exceed `dfi_max_ext`.

Large extents are handled by `split_extent()`, which uses `dfi_max_ext_bytes` first, then `dfi_max_bytes`, then `UINT64_MAX` as the segment length. It aligns split points so subsequent chunks start on acceptable boundaries.

`process_range()` removes zero-length extents from emitted sublists. If all extents in the range are zero length, no callback is made and success is returned.

## Error Semantics

The helper follows the coarse `DKIOCFREE` model: malformed or out-of-device input fails the whole request, but ranges narrowed away by alignment are silently ignored. Callback errors abort iteration and are returned to the caller. Allocation failures return `ENOMEM`; invalid geometry or extents return `EINVAL`; arithmetic overflow returns `EOVERFLOW`.

## Dependencies

This file depends on `sys/dkio.h` and `sys/dkioc_free_util.h` for structures and macros, DDI copyin flags, kernel memory allocation, power-of-two alignment macros, and `SET_ERROR()` conventions. It includes SDT support but the file itself does not define probes.

## Notable Invariants And Audit Notes

- `dfl_num_exts` must be nonzero and bounded before `DFL_SZ()` allocation.
- All callback lists emitted by `dfl_iter()` conform to the caller-provided `dkioc_free_info_t`.
- The original request is freed by `dfl_iter()` except for the fast path where it is handed directly to the callback.
- `process_range()` assumes the callback takes ownership of each allocated `new_dfl`.
- The utility intentionally cannot report partial completion; callers should treat success as "all valid, processable ranges were submitted."
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dkioc_free_util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/driver.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/driver.c

## Purpose

`driver.c` contains core illumos driver entry-point dispatch helpers. It wraps nexus and leaf driver callbacks for identify/probe/attach/detach/reset/quiesce, basic block/character device operations, layered open/close through specfs, size-property queries, and property operations.

The file is intentionally thin: it centralizes common DDI/DKI dispatch mechanics and auxiliary integration with power management, MDI, DTrace I/O probes, and specfs open/close semantics.

## Configuration Entry Points

- `devi_identify()` calls `devo_identify` if present.
- `devi_probe()` calls `devo_probe`, defaulting to `DDI_PROBE_DONTCARE` for self-identifying devices without a probe routine, and wraps probe with PM pre/post hooks.
- `devi_attach()` runs MDI pre/post attach, PM attach hooks, parental resume shortcuts, parent attach ctlops, and the driver's `devo_attach`.
- `devi_detach()` validates detach command shape, supports parental suspend shortcuts, runs MDI/PM hooks, parent detach ctlops, and the driver's `devo_detach`.
- `devi_reset()` and `devi_quiesce()` call optional reset/quiesce entry points.

`i_attach_ctlop()` and `i_detach_ctlop()` package attach/detach state into `attachspec` or `detachspec` and send `DDI_CTLOPS_ATTACH` or `DDI_CTLOPS_DETACH` to the parent.

## Leaf Device Open And Close

`dev_open()` and `dev_close()` directly dispatch to `cb_open` and `cb_close`; comments direct newer code to use the LDI interfaces instead.

`dev_lopen()` and `dev_lclose()` are the layered open/close helpers. They create a specfs vnode with `makespecvp()`, call `VOP_OPEN` or `VOP_CLOSE` with `FKLYR`, and rely on specfs for open/close exclusion and last-close behavior. `dev_lopen()` places an extra hold on the common vnode containing the open count. `dev_lclose()` releases that hold carefully and diagnoses extra closes without necessarily panicking on production kernels.

The `dev_lclose_ce` tunable controls the severity of extra-close diagnostics: panic in debug kernels by default, warning otherwise.

## Device Operations

Block-device wrappers:

- `bdev_strategy()` fills `bp->b_dip`, fires `io:::start`, marks `B_STARTED`, and calls `cb_strategy`.
- `bdev_print()` dispatches `cb_print`.
- `bdev_size()` reads 32-bit `nblocks` and block-size properties and returns DEV_BSIZE block count.
- `bdev_Size()` does the same for 64-bit `Nblocks`.
- `bdev_dump()` dispatches `cb_dump`.

Character-device wrappers:

- `cdev_read()`, `cdev_write()`, `cdev_ioctl()`, `cdev_devmap()`, `cdev_segmap()`, and `cdev_poll()` dispatch through `cb_ops`.
- `cdev_mmap()` calls a supplied mmap function pointer.
- `cdev_size()` and `cdev_Size()` query `size` or `Size` properties for non-STREAMS character drivers without forcing unused drivers into memory.
- `cdev_prop_op()` dispatches `cb_prop_op`.

## Instance Lookup

`dev_to_instance()` loads the driver for a major number with `mod_hold_dev_by_major()`, requires `devo_getinfo`, asks the driver to translate `DDI_INFO_DEVT2INSTANCE`, releases the module hold, and returns `-1` on failure.

## Dependencies

This file depends on `devopsp`, `devnamesp`, specfs snodes, DDI/NDI driver structures, PM hooks, MDI hooks, DTrace I/O probes, property helpers, and module hold/release routines.

## Notable Invariants And Audit Notes

- `devi_attach()` and `devi_detach()` pair MDI/PM pre and post notifications around driver entry points.
- `dev_lopen()` deliberately drops `OTYP_LYR` and uses `FKLYR` through specfs.
- `dev_lclose()` must preserve common-vnode accounting even when callers over-close; this path is intentionally defensive because double close indicates a driver bug.
- `bdev_size()` and `bdev_Size()` assume block-size properties are meaningful divisors/multipliers of `DEV_BSIZE`; callers needing byte sizes should prefer higher-level size helpers when available.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/driver.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/driver_lyr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/driver_lyr.c

## Purpose

`driver_lyr.c` implements illumos Layered Driver Interface support. It lets kernel consumers open lower devices by dev_t, path, or devid; tracks who opened what; exposes read/write/ioctl/strategy/property/event APIs through `ldi_handle_t`; records STREAMS multiplexing relationships; and propagates device events through LDI callbacks and device contracts.

This is the central file for safe kernel-to-kernel device stacking.

## Core Data Structures

The LDI keeps two reference-counted hash tables:

- `ldi_ident_hash`: maps caller identity to `struct ldi_ident`, keyed by module id plus optional dip, dev_t, or major.
- `ldi_handle_hash`: maps target vnode plus identity to `struct ldi_handle`.

`ldi_init()` initializes both hash tables and the event callback list. Handles hold both the identity and target vnode. The handle type records whether the target is a STREAMS vnode or a character/block callback device.

## Identity And Handle Lifetime

Identities can be created from:

- module linkage: `ldi_ident_from_mod()`,
- anonymous genunix identity: `ldi_ident_from_anon()`,
- STREAMS queue: `ldi_ident_from_stream()`,
- dev_t: `ldi_ident_from_dev()`,
- devinfo pointer: `ldi_ident_from_dip()`,
- major number: `ldi_ident_from_major()`.

All identities are released with `ldi_ident_release()`. Internally, `ident_alloc()`, `ident_hold()`, and `ident_release()` preserve one shared identity per key.

Handles are allocated by `handle_alloc()` after a successful specfs open. Duplicate opens of the same vnode by the same identity share a handle and increment its reference count. `handle_release()` removes the handle from the hash on the last reference, releases the vnode and identity, and updates `ldi_handle_hash_count`.

## Opening Devices

Target vnodes are resolved by:

- `ldi_vp_from_dev()` using `e_ddi_hold_devi_by_dev()` and `makespecvp()`.
- `ldi_vp_from_name()` using global-zone pathname lookup when root is mounted, or `resolve_pathname()` before root or for OBP/devfs paths.
- `ldi_vp_from_devid()` using `ddi_lyr_devid_to_devlist()`, then revalidating the devid against the held devinfo node to avoid races with replaced devices.

Public opens are `ldi_open_by_dev()`, `ldi_open_by_name()`, and `ldi_open_by_devid()`. All flow through `ldi_open_by_vp()`, which requires a specfs block/char vnode, rejects missing `cb_ops`, performs `VOP_OPEN(..., FKLYR, ...)`, handles clone-open vnode replacement, and creates the LDI handle.

`ldi_close()` performs `VOP_CLOSE(..., FKLYR, ...)`, nulls matching event callback handle references, and releases the handle even if close fails.

## I/O And Device Operations

The file exposes LDI wrappers for common lower-device operations:

- `ldi_read()` and `ldi_write()` dispatch to `cdev_*` for cb devices or `strread`/`strwrite` for STREAMS.
- `ldi_ioctl()` normalizes kernel ioctl mode to `FNATIVE | FKIOCTL`, supplies a temporary `rvalp` when callers pass NULL, and translates kernel `I_PLINK` into `_I_PLINK_LH` for STREAMS layered-handle linking.
- `ldi_poll()` dispatches to character-device or STREAMS polling.
- `ldi_strategy()`, `ldi_dump()`, `ldi_devmap()`, `ldi_aread()`, and `ldi_awrite()` support cb devices, with async I/O restricted to devices that have block-style strategy support.
- `ldi_putmsg()` and `ldi_getmsg()` provide STREAMS message send/receive helpers.
- `ldi_get_dev()`, `ldi_get_otyp()`, `ldi_get_devid()`, and `ldi_get_minor_name()` expose handle metadata.

`ldi_get_size()` derives byte size from block `Nblocks`/`nblocks` plus `blksize` or `device-blksize`, then falls back to `Size`/`size` properties.

## Property Support

`ldi_prop_op()` and the typed lookup/get helpers locate the associated dip through the common snode or by dev_t. They first allow the driver's dynamic `prop_op()` to override values and then fall back to normal DDI property interfaces.

Typed property wrappers include:

- `ldi_prop_lookup_int_array()`
- `ldi_prop_lookup_int64_array()`
- `ldi_prop_lookup_string_array()`
- `ldi_prop_lookup_string()`
- `ldi_prop_lookup_byte_array()`
- `ldi_prop_get_int()`
- `ldi_prop_get_int64()`
- `ldi_prop_exists()`

`i_ldi_prop_op_typed()` rejects zero-length properties and properties whose length is not a multiple of the element size. String helpers validate null termination and repack concatenated string arrays into the pointer-array format expected by callers.

## Usage Walker

`ldi_usage_count()` returns the number of open handle records. `ldi_usage_walker()` walks handle buckets and reports target/source relationships via a callback. It resolves target dips from snodes or dev_t, and source dips from identity state. When an identity only names a driver or major, it conservatively reports all current instances of that source driver as possible users of the lower device.

This is used for device usage observability and devinfo snapshot-style consumers.

## STREAMS Link Tracking

`ldi_mlink_lh()` creates a temporary `file_t` for a lower vnode so STREAMS persistent linking can operate on an LDI handle.

`ldi_mlink_fp()` records successful STREAMS links as LDI handle relationships. Normal links identify the upper side from the STREAMS queue and dev_t; persistent links identify only the upper major. For layered-handle persistent links, it adjusts common snode and file reference counts so the lower stream remains open while linked.

`ldi_munlink_fp()` reverses this state, clears `SMUXED`, finds the matching handle, releases it, and releases the temporary identity.

## Event Framework

The file supports two event families:

- native LDI events such as `LDI_EV_OFFLINE`, `LDI_EV_DEGRADE`, and `LDI_EV_DEVICE_REMOVE`,
- NDI event-service callbacks passed through `ddi_add_event_handler()`.

`ldi_ev_get_cookie()` returns native cookies from a static table or asks NDI for a cookie. `ldi_ev_register_callbacks()` validates callback versions, registers NDI handlers when needed, and adds callback records to the protected callback list. `ldi_ev_remove_callbacks()` removes records safely even during callback-list walks.

The event lock is recursive by design because layered drivers may call back into LDI, including `ldi_close()`, from notify/finalize callbacks.

Native event propagation uses:

- `ldi_invoke_notify()` to negotiate synchronous events with registered layered drivers and roll back earlier notifies with finalize callbacks if a later callback vetoes.
- `ldi_ev_notify()` to combine device-contract negotiation with LDI notify propagation.
- `ldi_invoke_finalize()` to deliver final event disposition.
- `ldi_ev_finalize()` to finalize both device contracts and LDI callbacks.

## Dependencies

This file depends on specfs, devinfo hold/release APIs, DDI property APIs, STREAMS internals, vnode operations, kernel file allocation, device contracts, NDI event services, module name/major translation, and devid conversion helpers in the devid cache path.

## Notable Invariants And Audit Notes

- LDI handles require a valid specfs block or character vnode and valid target `cb_ops`.
- Handle lifetime is independent of close success; after `ldi_close()` the handle is no longer usable.
- Event callback records can survive handle close with `lec_lhp == NULL` so finalize can still inform consumers after notify-triggered close.
- Callback-list walkers use `le_walker_next` and `le_walker_prev` so callbacks can unregister themselves or others safely.
- Property helpers must release any dip hold on all success and fallback paths; this is a repeated pattern worth preserving in edits.
- `ldi_get_size()` relies on block-size properties being powers of two and asserts that invariant before shifting.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/driver_lyr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dtrace_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dtrace_subr.c

## Purpose

`dtrace_subr.c` contains small genunix-side DTrace integration hooks. It declares function pointers populated by DTrace-related modules, maintains high-resolution time snapshots safe for probe context, tracks DTrace virtual time state, and forwards fasttrap fork handling.

## Main Interfaces And Globals

Module hook pointers include:

- `dtrace_cpu_init`
- `dtrace_modload`
- `dtrace_modunload`
- `dtrace_helpers_cleanup`
- `dtrace_helpers_fork`
- `dtrace_cpustart_init`
- `dtrace_cpustart_fini`
- `dtrace_cpc_fire`
- `dtrace_closef`
- debugger init/fini hooks

Global state includes `dtrace_vtime_active`, `dtrace_predcache_id`, and `dtrace_cpc_in_use`. The CPC usage counter is documented as being coordinated by DTrace, CPC framework, CPU management, and `kcpc_cpuctx_lock`.

## High-Resolution Time Snapshots

DTrace probe context cannot safely acquire `hres_lock`, because probes may fire while that lock is already held. The file solves this by maintaining two `dtrace_hrestime_t` snapshots, each protected by a low-level lock word.

`dtrace_hres_tick()` runs from the same high-level cyclic context as `hres_tick()`. It updates both snapshots in succession:

1. Acquire the real high-resolution clock lock.
2. Copy `hrestime`, `hrestime_adj`, and current hrtime.
3. Release the clock lock.
4. Lock one DTrace snapshot, publish the copied values, issue a producer barrier, and unlock by incrementing the lock word.

Because one thread updates the two snapshots sequentially, at least one snapshot should be stable for probe readers.

`dtrace_gethrestime()` reads snapshot zero or one using lock-word parity and memory barriers. Once it has a stable snapshot, it computes nanoseconds from the copied `timestruc_t`, adds elapsed hrtime since the snapshot, and applies bounded `hrestime_adj` correction.

## Virtual Time

`dtrace_vtime_enable()` atomically transitions `dtrace_vtime_active` from inactive to active and panics if already active. `dtrace_vtime_disable()` performs the reverse and panics if already inactive.

`dtrace_vtime_switch()` disables interrupts, accounts elapsed virtual time to the outgoing current thread if it had a nonzero DTrace start timestamp, assigns the same timestamp to the incoming thread, and restores interrupts.

## Fasttrap Integration

`dtrace_fasttrap_fork()` is called from process fork handling when the parent appears to have active user-space DTrace tracepoints. It asserts the process lock and positive tracepoint count, then calls the loaded fasttrap module through `dtrace_fasttrap_fork_ptr`.

## Dependencies

This file depends on DTrace core headers, atomic operations, process structures, module-control structures, high-resolution clock globals, and fasttrap module hooks. SPARC builds include privileged-register definitions.

## Notable Invariants And Audit Notes

- `dtrace_gethrestime()` depends on the two-snapshot update protocol; both snapshot locks must not be held simultaneously by different writers.
- Memory barriers around snapshot publication and consumption are essential for probe-context readers.
- Virtual time enable/disable is single-owner state and intentionally panics on double enable or double disable.
- Fasttrap fork forwarding assumes the fasttrap module remains loaded when `p_dtrace_count > 0` under `P_PR_LOCK`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dtrace_subr.c -->