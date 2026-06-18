# Research: subset-b-003568

Grouped research for DRM files under `sources/distributed-fs/ceph-client/drivers/gpu/drm`. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_pagemap.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_pagemap.c

## Purpose

`drm_pagemap.c` implements the DRM-side wrapper around Linux `dev_pagemap` for GPU shared virtual memory. It lets DRM drivers populate an `mm_struct` range with device-private pages, migrate anonymous memory between system RAM, local device memory, and peer device memory, and evict device allocations back to RAM during CPU faults, reclaim, or device teardown. The file is meant for best-effort heterogeneous memory population where hardware unbind must reject new population and eventually return resident pages to system memory.

## Important APIs, Types, and Functions

- `struct drm_pagemap_zdd` is the per-zone-device-data wrapper stored in folio zone-device data. It holds a kref, the `drm_pagemap_devmem` allocation, and a referenced `struct drm_pagemap`.
- `drm_pagemap_migrate_to_devmem()` is the main exported migration-to-device entry. It validates an anonymous VMA, uses `migrate_vma_setup()`, asks the driver to populate destination device PFNs, copies data through driver ops, finalizes migration, and consumes the caller's devmem allocation reference.
- `drm_pagemap_evict_to_ram()` migrates an entire `drm_pagemap_devmem` allocation back to RAM without requiring the caller to hold `mmap_lock`, using `migrate_device_pfns/pages/finalize`.
- `drm_pagemap_populate_mm()` is the exported wrapper around a driver's `dpagemap->ops->populate_mm`, taking an `mm` reference and `mmap_read_lock`.
- `drm_pagemap_pagemap_ops_get()` returns `dev_pagemap_ops` with `folio_free`, `migrate_to_ram`, and `folio_split` callbacks.
- `drm_pagemap_init()`, `drm_pagemap_reinit()`, `drm_pagemap_put()`, and `drm_pagemap_destroy()` manage pagemap lifetime and cached reactivation.
- `drm_pagemap_devmem_init()` initializes allocation state: device, mm, ops, owning pagemap, size, completion, and optional pre-migration fence.
- Internal helpers such as `drm_pagemap_migrate_map_pages()`, `drm_pagemap_migrate_unmap_pages()`, `drm_pagemap_migrate_range()`, and `drm_pagemap_migrate_populate_ram_pfn()` abstract DMA mapping, peer-device mapping, batch-copy segmentation, and RAM page allocation.

## Control Flow

Migration to device starts by asserting `mmap_lock`, validating the VMA covers the requested range and is anonymous, allocating contiguous scratch arrays for source PFNs, destination PFNs, DMA addresses, and page pointers, and allocating a `drm_pagemap_zdd`. `migrate_vma_setup()` collects movable pages. The code rejects partial collection unless compound-page accounting proves the full requested range is present. It counts pages already owned by the target pagemap, optionally rejects same-pagemap fragmentation, asks the driver to populate device PFNs, then walks the range by folio order.

For each destination device page, the code initializes zone-device folio metadata and records whether the source is system RAM, local device memory, or peer device memory. `drm_pagemap_migrate_range()` flushes contiguous subranges whenever the source pagemap or ops changes. System-to-device copies call the target allocation's `copy_to_devmem`; peer/local device copies map pages through the source pagemap's `device_map` and call the source allocation's `copy_to_ram` into destination pages. After data transfer, `migrate_vma_pages()` and `migrate_vma_finalize()` install successful migrations and release unsuccessful pages.

CPU fault migration calls `drm_pagemap_migrate_to_ram()` via `dev_pagemap_ops`. It checks the allocation's `timeslice_expiration`, computes an aligned allocation-sized range clipped to the VMA, allocates RAM folios matching source folio order, maps them for DMA from device, calls `copy_to_ram`, then finalizes. Explicit eviction uses a similar path over `migrate_device_*` APIs and retries twice unless the allocation's `detached` completion indicates release already happened.

## State and Persistence

State is in memory only. `drm_pagemap_zdd` binds device pages to the devmem allocation and pagemap until folio free, at which point `drm_pagemap_folio_free()` drops the kref. `drm_pagemap_zdd_destroy()` completes `devmem->detached`, calls optional `devmem_release`, frees the wrapper, and puts the pagemap. `drm_pagemap` itself holds references to the DRM device and owning module through `struct drm_pagemap_dev_hold`; final release queues deferred work that later drops those references from process context. Device page split preserves `pgmap` and increments zdd references for the new folio.

`drm_pagemap_devmem` stores migration ops, mm, size, pre-migration fence, and a jiffies-based timeslice. On successful device migration the pre-migration fence is dropped and `timeslice_expiration` is set to delay immediate CPU-fault migration back to RAM.

## Dependencies and Integration Points

The file integrates Linux memory migration (`migrate_vma`, `migrate_device_*`), device-private page infrastructure (`dev_pagemap_ops`, `zone_device_folio_init`), DMA mapping, folios, completions, krefs, workqueues, and DRM device/module lifetime. Driver-specific behavior is supplied through `struct drm_pagemap_ops` and `struct drm_pagemap_devmem_ops` callbacks such as `populate_mm`, `populate_devmem_pfn`, `copy_to_devmem`, `copy_to_ram`, `devmem_release`, `device_map`, and `device_unmap`. It also calls utility-layer hooks from `drm_pagemap_util.c` for shrinker insertion and lockdep checks.

## Risks and Edge Cases

- `drm_pagemap_migrate_to_devmem()` consumes the devmem allocation reference on all paths; callers must not reuse it after failure.
- Partial migration, races with CPU faults, unknown device pages, VMA clipping, compound folio order, and same-pagemap fragmentation all have explicit rejection or retry paths.
- DMA mapping failures return `-EFAULT`; already mapped pages are unmapped only when the cleanup path has enough recorded state.
- The code assumes driver copy callbacks handle fences and peer/local interconnect semantics correctly.
- Fault-time migration must avoid returning pages to RAM during the protected timeslice.
- Deferred device/module release depends on `module_exit()` flushing `drm_pagemap_work`; leaked list entries trigger warnings.
- `drm_pagemap_page_to_dpagemap()` is unsafe for pages not created by this pagemap infrastructure.

## Test Signals

Useful tests include migration of anonymous pages to device memory and back, compound-page migration, same-pagemap migration allowed and denied, peer-device migration with `source_peer_migrates`, CPU fault before and after `timeslice_expiration`, explicit eviction during mm teardown, driver unbind with pending page references, DMA-map failure injection, and lockdep/KASAN/KCSAN coverage around zdd lifetime and deferred device release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_pagemap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_pagemap_util.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_pagemap_util.c

## Purpose

`drm_pagemap_util.c` provides utility infrastructure around DRM pagemaps: a single-entry cache for inactive pagemaps, a DRM-managed shrinker that frees unused cached pagemaps, and an owner grouping API for devices connected by a fast peer interconnect. It complements `drm_pagemap.c` by deciding whether released pagemaps can be cached and revived or must be destroyed.

## Important APIs, Types, and Functions

- `struct drm_pagemap_cache` stores one non-refcounted `dpagemap` pointer, a lookup mutex, a spinlock, its shrinker, and a `queued` completion used when an inactive pagemap has reached the shrinker list.
- `struct drm_pagemap_shrinker` wraps a kernel `struct shrinker`, an unused pagemap list, a spinlock, an atomic count, and the DRM device.
- `drm_pagemap_cache_create_devm()` and `drm_pagemap_shrinker_create_devm()` allocate device-managed cache and shrinker objects.
- `drm_pagemap_cache_lock_lookup()` and `drm_pagemap_cache_unlock_lookup()` serialize lookup plus create/insert sequences.
- `drm_pagemap_get_from_cache()` returns an active pagemap reference, waits for inactive pagemaps to be queued, cancels shrinker ownership, reinitializes released pagemaps, or returns `NULL` when the caller must create a new pagemap.
- `drm_pagemap_cache_set_pagemap()` installs a newly created or revived pagemap into the cache.
- `drm_pagemap_shrinker_add()` either moves a released pagemap to the shrinker list or destroys it directly when cache/device state is unavailable.
- `drm_pagemap_acquire_owner()` and `drm_pagemap_release_owner()` maintain shared `drm_pagemap_owner` objects for peers that have fast interconnects.

## Control Flow

Pagemap lookup is intended to run under `lookup_mutex`. The caller tries `drm_pagemap_get_from_cache()`. If the cached object has a nonzero kref, it returns immediately. If the pointer is absent, lookup returns `NULL`. If a pointer exists but has been released, lookup waits until `drm_pagemap_shrinker_add()` signals `queued`, then attempts to remove the object from the shrinker list. A successful cancel clears the cache pointer, calls `drm_pagemap_reinit()`, and reinserts the revived object; a failed cancel means the shrinker already took ownership, so lookup returns `NULL`.

When the last pagemap reference is dropped in `drm_pagemap.c`, `drm_pagemap_shrinker_add()` is called. It first checks device liveness with `drm_dev_enter()`. If the pagemap has a cache and the DRM device is live, it is linked onto the shrinker list, counted, and its cache completion is signaled. Otherwise it is immediately destroyed, with the `is_atomic_or_reclaim` flag set. Shrinker scans remove list entries, clear the cache's pointer under the cache lock, and call `drm_pagemap_destroy()`.

Interconnect ownership acquisition scans existing peers in list order. If all peers in a candidate owner group satisfy the `has_interconnect()` callback, the new peer shares that owner; otherwise a new owner is allocated. Release unlinks the peer and drops the owner's kref.

## State and Persistence

All state is transient kernel memory and device-managed. Cache and shrinker cleanup are registered through `devm_add_action_or_reset()`, so teardown runs when the DRM device is removed. The cache stores a non-refcounted pointer, which is safe only under the documented lock and completion protocol. The shrinker list is the owner of inactive cached pagemaps pending reuse or reclaim. Owner groups persist until all participating peers call `drm_pagemap_release_owner()`.

## Dependencies and Integration Points

This file depends on DRM managed resources, `drm_dev_enter/exit`, kernel shrinkers, spinlocks, mutexes, completions, krefs, and list primitives. It is called from `drm_pagemap_put()` and `drm_pagemap_release()` paths in `drm_pagemap.c`, and it exports helpers for GPU drivers that cache pagemaps or reason about fast peer interconnects.

## Risks and Edge Cases

- The cache stores only one pagemap; drivers expecting multi-entry caching must layer their own structure above it.
- Correctness depends on using `drm_pagemap_cache_lock_lookup()` around get/create/set. Skipping it can create duplicate pagemaps.
- A lookup may block interruptibly waiting for the released pagemap to reach the shrinker list.
- The shrinker can race with reactivation; `drm_pagemap_shrinker_cancel()` is the arbitration point.
- `drm_pagemap_cache_fini()` only destroys inactive pagemaps it can cancel; active pagemaps remain governed by normal references.
- Interconnect grouping assumes the callback is symmetric and that sharing a single owner correctly models peer accessibility.

## Test Signals

Exercise cache hit on active pagemap, cache miss and insert, inactive revive before shrinker scan, shrinker scan before revive, device teardown with inactive and active cached objects, interruptible lookup wait, owner grouping with connected and disconnected peers, and lockdep with `CONFIG_PROVE_LOCKING`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_pagemap_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panel.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panel.c

## Purpose

`drm_panel.c` implements the central DRM panel registry and panel lifecycle helpers. It lets panel drivers initialize, register, expose modes, attach optional backlights, and coordinate follower devices such as touchscreens that need to power sequence with the panel.

## Important APIs, Types, and Functions

- Global `panel_list` plus `panel_lock` form the registry used by firmware/device-tree lookup.
- `drm_panel_init()`, `drm_panel_add()`, and `drm_panel_remove()` initialize and register panel objects.
- `drm_panel_prepare()`, `drm_panel_unprepare()`, `drm_panel_enable()`, and `drm_panel_disable()` implement the standard power and visible-output lifecycle.
- `drm_panel_get_modes()` delegates mode discovery to panel ops.
- `drm_panel_get()` and `drm_panel_put()` kref device-managed panel allocations created by `__devm_drm_panel_alloc()`.
- `of_drm_find_panel()` and `of_drm_get_panel_orientation()` support Open Firmware lookup and rotation parsing.
- `drm_is_panel_follower()`, `drm_panel_add_follower()`, `drm_panel_remove_follower()`, and `devm_drm_panel_add_follower()` coordinate follower callbacks.
- `drm_panel_of_backlight()` resolves and stores a DT backlight phandle.

## Control Flow

Panel initialization sets list heads, follower lock, parent device, funcs, and connector type. Registration adds the panel to the global list under `panel_lock`. Prepare and enable are guarded by `panel->prepared` and `panel->enabled` flags. Prepare calls the panel's `prepare` op first, marks the panel prepared, then notifies followers via `panel_prepared`. Enable calls the panel's `enable` op, marks enabled, enables any associated backlight, then notifies followers via `panel_enabled`.

Disable and unprepare run the reverse order for follower notifications. Disable calls followers' `panel_disabling`, disables the backlight, calls panel `disable`, then clears `enabled`. Unprepare calls followers' `panel_unpreparing`, calls panel `unprepare`, then clears `prepared`. Warnings catch duplicate operations, especially shutdown-order bugs.

Follower registration resolves a `panel` firmware reference from the follower device. It gets a reference to the panel's device, links the follower under `follower_lock`, and immediately catches the follower up if the panel is already prepared or enabled. Removal calls disabling/unpreparing callbacks when needed, unlinks the follower, and drops the panel device reference.

## State and Persistence

State is in kernel memory: global registry membership, `prepared` and `enabled` booleans, a `backlight` pointer, panel reference count, and follower list. Device-managed panel allocations store the allocated container pointer and are freed through a devm action that calls `drm_panel_put()`. Backlight ownership is resolved through devm OF lookup and stored on the panel for lifecycle calls.

## Dependencies and Integration Points

The file integrates with panel driver `struct drm_panel_funcs`, `struct drm_connector` mode probing, backlight class devices, OF/fwnode firmware references, device properties, devm resource cleanup, and DRM bridge users indirectly through panel lookup APIs. Follower APIs are intended for devices whose power state must mirror panel state.

## Risks and Edge Cases

- `drm_panel_prepare()`, `enable()`, `disable()`, and `unprepare()` cannot report errors to callers; callback failures are logged and state changes may be skipped depending on where the failure occurs.
- Duplicate lifecycle calls are treated as warnings and no-ops.
- `of_drm_find_panel()` returns `-EPROBE_DEFER` when a device tree panel exists but is not registered yet.
- `drm_panel_remove_follower()` assumes `follower->panel` is valid and should only be used after successful add.
- Follower callbacks run under `follower_lock`, so they must avoid lock cycles with panel or device teardown paths.
- A missing or invalid connector type only warns in `drm_panel_init()`.

## Test Signals

Tests should cover add/remove lookup, deferred OF lookup, prepare/enable/disable/unprepare sequencing, duplicate lifecycle warnings, backlight enable/disable failure handling, follower add while panel is already active, follower removal while active, devm allocation/free, and OF rotation parsing for 0/90/180/270 plus invalid values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panel_backlight_quirks.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panel_backlight_quirks.c

## Purpose

`drm_panel_backlight_quirks.c` provides a small platform quirk table for panels whose minimum brightness or brightness encoding cannot be reliably inferred from firmware or EDID alone. It currently covers Framework laptops, Steam Deck variants, and several handheld/OLED systems.

## Important APIs, Types, and Functions

- `struct drm_panel_match` stores one DMI field/value match.
- `struct drm_get_panel_backlight_quirk` combines up to two DMI matches, an optional `drm_edid_ident`, and the returned `drm_panel_backlight_quirk`.
- `drm_panel_min_backlight_quirks[]` is the static quirk database. Entries use `min_brightness = 1` or `brightness_mask = 3`.
- `drm_panel_min_backlight_quirk_matches()` checks required DMI fields and optional EDID identity.
- `drm_get_panel_backlight_quirk()` is the exported lookup function.

## Control Flow

Lookup first returns `-ENODATA` when DMI support is not enabled and `-EINVAL` for a missing EDID pointer. It then scans `drm_panel_min_backlight_quirks[]` in order. Each candidate rejects if the primary DMI match fails, the secondary DMI match fails, or an EDID identity is present and `drm_edid_match()` fails. The first matching entry returns a pointer to the embedded quirk. No match returns `ERR_PTR(-ENODATA)`.

## State and Persistence

The file is read-only after module load. The returned quirk points into static const table storage and must not be modified or freed.

## Dependencies and Integration Points

It depends on DMI matching, DRM EDID helpers, and the public `drm_panel_backlight_quirk` type. Display/backlight code can call the exported function after reading EDID to clamp minimum brightness or mask brightness values for known broken systems.

## Risks and Edge Cases

- Table ordering matters because lookup returns the first match.
- Some entries are DMI-only and ignore EDID, which is intentional for systems where panel identity is not needed but increases false-positive risk.
- `brightness_mask = 3` encodes a hardware-specific workaround; callers must know how to apply it.
- Systems without `CONFIG_DMI` never match even if EDID matches.
- New quirks must use sufficiently specific DMI fields to avoid changing brightness behavior on unrelated hardware.

## Test Signals

Useful tests include DMI/EDID match and mismatch cases, DMI-only Steam Deck entries, Framework EDID-specific entries, `NULL` EDID rejection, `CONFIG_DMI=n` fallback, and caller behavior for both `min_brightness` and `brightness_mask`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panel_backlight_quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panel_orientation_quirks.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panel_orientation_quirks.c

## Purpose

`drm_panel_orientation_quirks.c` is a DMI-based quirk database for x86 devices whose built-in portrait panels need a default framebuffer rotation but cannot expose reliable orientation metadata. The file is intentionally independent of broader DRM internals because fbdev/efifb also uses it.

## Important APIs, Types, and Functions

- `struct drm_dmi_panel_orientation_data` stores expected panel width, height, optional BIOS date allow-list, and a `DRM_MODE_PANEL_ORIENTATION_*` value.
- Static data objects define common resolution/orientation pairs and special GPD/OneGX entries with BIOS date filters.
- `orientation_data[]` is the DMI system table covering Acer, Anbernic, ASUS, AYANEO, GPD, Lenovo, Valve, ZOTAC, and other handheld/tablet devices.
- `drm_get_panel_orientation_quirk(width, height)` is the exported lookup API. With `CONFIG_DMI=n`, it always returns `DRM_MODE_PANEL_ORIENTATION_UNKNOWN`.

## Control Flow

When DMI is enabled, lookup iterates every matching DMI entry by repeatedly calling `dmi_first_match()`. For each matched system, it reads the attached orientation data, verifies the caller-provided width and height exactly match the expected panel resolution, and then either returns the orientation directly or checks the current BIOS date against the entry's allow-list. If resolution or BIOS date does not match, lookup continues to later DMI matches. If nothing qualifies, it returns `UNKNOWN`.

## State and Persistence

All state is static const data. There are no allocations, no locks, and no runtime mutation. The result is computed from current system DMI strings and caller-provided panel dimensions.

## Dependencies and Integration Points

The file depends on Linux DMI helpers, `drm_connector.h` orientation enum definitions, and `drm_utils.h` for matching helpers. It is consumed by DRM and framebuffer boot paths that need a safe default orientation before full userspace display configuration.

## Risks and Edge Cases

- False positives are a major concern; many entries add exact DMI strings, resolution checks, and sometimes BIOS dates to avoid matching generic tablet platforms.
- Two devices can share DMI identity but use different panel resolutions; the width/height filter is mandatory to select the right orientation.
- Entries with `DMI_MATCH` are broader than `DMI_EXACT_MATCH` and need careful review.
- `CONFIG_DMI=n` means no quirks are available on non-DMI platforms.
- Adding a new DMI quirk can affect early framebuffer console orientation before userspace starts.

## Test Signals

Tests should cover exact DMI plus resolution matches, generic DMI plus BIOS date filters, resolution mismatch returning `UNKNOWN`, multiple matching DMI rows selecting the row whose resolution matches, `CONFIG_DMI=n` behavior, and representative devices for each orientation value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panel_orientation_quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panic.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panic.c

## Purpose

`drm_panic.c` implements DRM's panic-screen renderer. Drivers that expose a panic-safe scanout buffer through `drm_plane_helper_funcs.get_scanout_buffer` can register their planes as `kmsg_dumper`s. On kernel panic, this file draws either a user-friendly panic message, recent kmsg text, or a QR code carrying panic logs, then optionally flushes the plane to hardware.

## Important APIs, Types, and Functions

- `struct drm_panic_line` stores text and length for the user message and ASCII logo.
- Blit/fill helpers include `drm_panic_blit()`, `drm_panic_fill()`, page-backed variants, direct-map variants, and `set_pixel` variants.
- Renderers are `draw_panic_screen_user()`, `draw_panic_screen_kmsg()`, and, when enabled, `draw_panic_screen_qr_code()`.
- QR support uses preallocated `qrbuf1`, `qrbuf2`, and a zlib workspace initialized by `drm_panic_qr_init()` and freed by `drm_panic_qr_exit()`.
- `draw_panic_plane()` obtains the scanout buffer, validates format support, sets the panic description, dispatches rendering, calls optional `panic_flush`, and releases the panic lock.
- `drm_panic_register()` and `drm_panic_unregister()` attach/detach per-plane `kmsg_dumper`s.
- `drm_panic_is_enabled()` reports whether a DRM device has any compatible plane.
- Module parameters select panic screen type and QR version.

## Control Flow

At init, `drm_panic_init()` parses `CONFIG_DRM_PANIC_SCREEN`, falls back to user mode on invalid configuration, and preallocates QR resources when configured. Registration walks all planes and registers only those with `helper_private->get_scanout_buffer`.

On a `KMSG_DUMP_PANIC` event, `drm_panic()` resolves the containing plane and calls `draw_panic_plane()`. That function uses `drm_panic_trylock()` to avoid unsafe concurrent drawing, calls the driver's panic buffer callback, rejects unsupported multi-plane or non-convertible formats, and requires one drawing path: `set_pixel`, `pages`, or an `iosys_map`. Drawing converts configured XRGB8888 foreground/background colors to the target format. Page-backed drawing maps pages with `kmap_local_page_try_from_panic()` and handles 24-bit pixels crossing page boundaries.

The user renderer centers the message and draws either a copied mono Linux logo or ASCII logo if it does not overlap. The kmsg renderer fills the screen and writes recent kmsg lines bottom-up with wrapping. The QR renderer gathers kmsg data, optionally zlib-compresses it into a configured URL parameter, calls the Rust QR encoder, scales the QR image to at least 2x, lays it out above the message, and falls back to the user renderer on failure.

## State and Persistence

Persistent runtime state includes the selected `drm_panic_type`, optional copied mono logo, static panic message array with a temporarily substituted description line, and QR buffers/workspace. Per-plane state is stored in each `drm_plane`'s `kmsg_panic` dumper. No panic-time dynamic allocation is intended except debugfs test paths; QR buffers are allocated before panic.

## Dependencies and Integration Points

The file integrates with DRM plane helpers, DRM draw conversion helpers, framebuffer format metadata, kmsg dumpers, fonts, Linux logo, zlib, debugfs, module parameters, and Rust FFI functions from `drm_panic_qr.rs`. Driver integration requires `get_scanout_buffer`, optional `panic_flush`, and a linear or panic-addressable scanout buffer.

## Risks and Edge Cases

- Panic context cannot sleep, allocate, take regular locks, or rely on IRQ/task progress. Driver callbacks must honor that contract.
- Only single-plane formats convertible from XRGB8888 are supported.
- Page-backed 24-bit drawing has special cross-page handling; invalid page arrays can still prevent pixels from being written.
- QR mode depends on preallocated buffers and zlib workspace; failure falls back to user message.
- `drm_panic_type_get()` indexes `drm_panic_type_map`; init must set a valid type before user reads.
- Debugfs trigger is explicitly marked unsafe and only for testing.
- Multiple registered planes may all draw during panic; each uses the device panic lock.

## Test Signals

KUnit coverage is included through `tests/drm_panic_test.c` when enabled. Additional test signals include supported and unsupported formats, `set_pixel` versus mapped versus page-backed buffers, QR buffer allocation failure, QR too-large fallback, kmsg wrapping, panic description trimming, panic flush callback invocation, registration/unregistration counts, and debugfs trigger behavior outside real panic context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panic_qr.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panic_qr.rs

## Purpose

`drm_panic_qr.rs` is a no-allocation QR encoder used by DRM panic QR mode. It generates QR-L images into caller-provided buffers, supporting raw binary payloads and a URL-plus-compressed-log mode that encodes binary data efficiently as numeric QR data.

## Important APIs, Types, and Functions

- `Version` encapsulates QR versions 1 through 40 and exposes width, capacity, block counts, ECC size, alignment pattern, polynomial, and version info.
- `VPARAM`, generator polynomial constants, alignment tables, version info, format info, Galois field tables, and padding constants define the QR-L encoding parameters.
- `Segment` represents binary and numeric segments; numeric mode converts every 7 bytes into 17 decimal digits to minimize URL-safe overhead.
- `DecFifo` and `SegmentIterator` stream decimal triples for numeric QR encoding without heap allocation. `div10()` avoids unavailable ARM 32-bit division helpers.
- `EncodedMsg` writes segment headers, data bits, padding, Reed-Solomon error correction, and exposes interleaved byte iteration.
- `QrImage` draws finder, alignment, timing, format, version, data, and mask modules into a 1-bit-per-module image.
- `drm_panic_qr_generate()` is the exported C ABI encoder.
- `drm_panic_qr_max_data_size()` reports the maximum payload size for a configured version and URL length.

## Control Flow

The C entry validates buffer sizes (`data_size >= 4071`, `tmp_size >= 3706`) and payload length. Without a URL, it builds one binary segment from `data[0..data_len]`. With a URL, it parses the nul-terminated URL as a C string, builds a binary URL segment and a numeric data segment, then asks `EncodedMsg::new()` for the smallest QR version that fits. Encoding clears the temp buffer, emits segment headers/length/data, writes stop bits and alternating padding bytes, computes Reed-Solomon ECC per QR block, and returns an interleaved data iterator.

`QrImage::new()` clears the output data buffer, draws reserved QR patterns, streams encoded bytes through the QR zig-zag placement order while skipping reserved modules, fills remaining modules, writes format info for low error correction and mask 0, then applies a checkerboard mask to non-reserved modules. The output buffer is overwritten with a packed 1-bit QR image, and the function returns the QR width in modules.

## State and Persistence

The Rust code keeps no global mutable state. All work uses static tables, stack arrays bounded by `MAX_BLK_SIZE + MAX_EC_SIZE`, and caller-provided mutable slices. The C caller owns and reuses the data and temporary buffers.

## Dependencies and Integration Points

It uses Rust-for-Linux `kernel::prelude`, `CStr`, and `#[export]` for C ABI exports consumed by `drm_panic.c`. The implementation is intentionally limited to QR low error correction and fixed mask 0 to keep panic-time code small and deterministic.

## Risks and Edge Cases

- Safety relies on C callers passing valid pointers and buffer lengths for the whole call.
- The encoder returns `0` on invalid size, invalid version, or data that cannot fit; `drm_panic.c` treats this as QR failure.
- Only low ECC and mask 0 are supported, so generated codes may be less robust than a fully optimized QR encoder.
- Numeric data conversion must match the decoder used by the configured QR URL endpoint.
- `drm_panic_qr_max_data_size()` is approximate for URL mode because it reserves headers and applies a 39/40 ratio for numeric conversion.
- ARM-specific division avoidance is important for kernel linkability on 32-bit ARM.

## Test Signals

Tests should validate generated widths for known payload sizes, raw binary and URL/numeric paths, max data size calculations for versions 1, 7, 40 and invalid versions, buffer-size rejection, Reed-Solomon/interleaving against known QR vectors, reserved module placement, and scanner readability for panic-generated images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panic_qr.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_pci.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_pci.c

## Purpose

`drm_pci.c` contains the PCI bus-id helper for DRM masters. It formats a unique legacy DRM device identifier from PCI domain, bus, slot, and function values.

## Important APIs, Types, and Functions

- `drm_get_pci_domain()` returns the PCI domain, except on most non-alpha architectures it preserves historical pre-1.4 DRM interface behavior by returning 0 when `dev->if_version < 0x10004`.
- `drm_pci_set_busid()` allocates and stores `master->unique` as `pci:%04x:%02x:%02x.%d` and fills `master->unique_len`.

## Control Flow

`drm_pci_set_busid()` casts `dev->dev` to `struct pci_dev`, calls `drm_get_pci_domain()`, formats the string with `kasprintf(GFP_KERNEL)`, returns `-ENOMEM` on allocation failure, and records the string length on success.

## State and Persistence

The only state mutation is `master->unique` and `master->unique_len`. The allocated string is owned by the DRM master lifecycle and must be freed by the existing DRM core cleanup path.

## Dependencies and Integration Points

It depends on Linux PCI helpers, DRM auth/master state, and the DRM interface-version compatibility contract. It is used by legacy userspace identity paths that query the DRM master unique string.

## Risks and Edge Cases

- The helper assumes the DRM device is backed by a PCI device; calling it for non-PCI devices would make `to_pci_dev()` invalid.
- The domain compatibility branch is a user ABI constraint and should not be simplified without considering old userspace.
- Allocation failure is the only expected runtime error.

## Test Signals

Test interface versions below and above `0x10004`, alpha versus non-alpha builds if practical, correct formatting for domain/bus/slot/function, and `kasprintf` failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_plane.c

## Purpose

`drm_plane.c` is the DRM core implementation for KMS plane objects. It registers universal planes, exposes plane resources and state through legacy ioctls, handles legacy setplane/cursor/page-flip operations, validates format/modifier support, and attaches standard plane properties such as `IN_FORMATS`, damage clips, scaling filters, size hints, hotspots, and color pipelines.

## Important APIs, Types, and Functions

- `__drm_universal_plane_init()`, `drm_universal_plane_init()`, `__drmm_universal_plane_alloc()`, and `__drm_universal_plane_alloc()` create and register plane objects.
- `create_in_format_blob()` builds the `drm_format_modifier_blob` for `IN_FORMATS` and `IN_FORMATS_ASYNC`.
- `drm_plane_cleanup()`, `drm_plane_register_all()`, and `drm_plane_unregister_all()` manage plane lifecycle and driver callbacks.
- `drm_mode_getplane_res()` and `drm_mode_getplane()` implement legacy resource query ioctls with lease and capability filtering.
- `drm_plane_has_format()` and `drm_any_plane_has_format()` validate format/modifier support.
- `drm_mode_setplane()`, `setplane_internal()`, `__setplane_internal()`, and `__setplane_atomic()` implement legacy plane updates for non-atomic and atomic drivers.
- `drm_mode_cursor_ioctl()` and `drm_mode_cursor2_ioctl()` implement legacy cursor updates, using universal cursor planes when available.
- `drm_mode_page_flip_ioctl()` implements legacy page flip and page flip target behavior.
- Property helpers include `drm_plane_enable_fb_damage_clips()`, damage clip accessors, `drm_plane_create_scaling_filter_property()`, `drm_plane_add_size_hints_property()`, and `drm_plane_create_color_pipeline_property()`.

## Control Flow

Plane initialization validates total plane and format-count limits, checks atomic state callback requirements, registers a mode object, initializes the modeset lock, allocates and copies format/modifier arrays, creates a name, links the plane into `mode_config.plane_list`, assigns an index, attaches immutable type and atomic properties, optionally creates cursor hotspot properties, and attaches format/modifier blobs. Managed allocation variants add DRM-managed cleanup actions; unmanaged allocation leaves freeing to the driver destroy hook.

Legacy `SETPLANE` lookup resolves plane, framebuffer, and CRTC IDs, then takes all modeset locks. Non-atomic updates call driver `update_plane` or `disable_plane` and update `plane->crtc`, `plane->fb`, and framebuffer references. Atomic drivers still route through plane funcs but use atomic-aware hooks. Common validation checks CRTC compatibility, framebuffer format/modifier support, coordinate overflow, and source bounds.

Cursor ioctls lock the CRTC and cursor plane. If a universal cursor plane exists, buffer-object updates wrap the GEM handle in an internal ARGB8888 framebuffer, optionally update hotspot state, and call the setplane path. Without a universal plane, the code calls legacy CRTC cursor callbacks. Page flips validate flags, target vblank semantics, async support, lease access, old framebuffer presence, new framebuffer source compatibility, and format stability. Optional events are reserved before invoking driver page-flip callbacks and canceled on failure.

## State and Persistence

Each plane stores its mode object, lock, name, index, possible CRTCs, type, format arrays, modifier arrays, property pointers, current state or legacy `fb/crtc`, and old framebuffer during transitions. Properties are persistent DRM objects attached to the plane. Blob properties store immutable format/modifier tables, damage clip arrays, and size hints.

## Dependencies and Integration Points

The file depends on DRM mode object/property infrastructure, framebuffer lifetime, CRTC/plane locks, leases, atomic and legacy modeset callbacks, vblank/event handling, userspace copy helpers, and driver-provided `drm_plane_funcs`. It is central to both old KMS ioctls and modern atomic property exposure.

## Risks and Edge Cases

- Plane indices are limited to 32-bit masks and format blobs currently encode formats in a 64-bit bitset.
- Mixing planes with and without zpos is warned as invalid.
- Legacy and atomic paths share some callbacks; comments note redundant validation for async/cursor tricks until all drivers call atomic checks.
- Cursor hotspot exposure is filtered for virtualized drivers unless userspace declares support.
- Page flip target handling must balance vblank references on all failure paths.
- `drm_plane_cleanup()` assumes plane list membership and zeros the structure, so callers must not use it afterward.
- Damage clips are hints; drivers must still tolerate full updates or inaccurate userspace damage.

## Test Signals

Tests should cover plane initialization failure unwinding, modifier blob contents, capability-filtered plane enumeration, lease filtering, format/modifier validation, setplane enable/disable reference counts, cursor BO and move paths with hotspots, page flip target absolute/relative validation, event reservation/cancel paths, damage clip accessors, scaling filter property validation, cursor-only size hints, and color pipeline enum creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_plane_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_plane_helper.c

## Purpose

`drm_plane_helper.c` provides transitional helpers for primary planes on non-atomic KMS drivers. It validates primary-plane updates with atomic helper logic, maps those updates back to legacy CRTC `set_config`, refuses primary-plane disable by default, and supplies a simple destroy helper.

## Important APIs, Types, and Functions

- `get_connectors_for_crtc()` collects connectors currently routed to a CRTC.
- `drm_plane_helper_check_update()` builds temporary plane and CRTC states and calls `drm_atomic_helper_check_plane_state()`.
- `drm_plane_helper_update_primary()` validates a primary-plane update, disables the plane if it becomes invisible, otherwise calls the CRTC's `set_config()` with the current connector set.
- `drm_plane_helper_disable_primary()` returns `-EINVAL`, preserving legacy behavior that primary planes generally cannot be disabled independently.
- `drm_plane_helper_destroy()` calls `drm_plane_cleanup()` and frees the plane.

## Control Flow

Update starts by rejecting atomic modeset drivers. It converts 16.16 source coordinates and integer CRTC destination coordinates into `drm_rect`s, validates with no scaling and no positioning, and receives adjusted source/destination plus a visibility flag. Invisible primary planes call the driver's `disable_plane`. Visible updates count current connectors for the CRTC, allocate a connector array, fill it, construct a `drm_mode_set`, and call `crtc->funcs->set_config()` directly. Connector memory is freed afterward.

## State and Persistence

The helpers do not own persistent state. They operate on the existing plane, CRTC mode, current connector routing, and driver callbacks. Destroy frees the plane object after core cleanup.

## Dependencies and Integration Points

The file depends on DRM connector iteration, modeset locking, atomic helper plane-state validation, legacy CRTC `set_config`, framebuffer state, and plane helper function tables. It is intended for old non-atomic drivers and is explicitly not recommended for new drivers.

## Risks and Edge Cases

- `get_connectors_for_crtc()` expects `connection_mutex` to already be locked.
- `drm_plane_helper_update_primary()` uses `BUG_ON(num_connectors == 0)`, so it assumes active primary updates have at least one connector.
- The helper bypasses `drm_mode_set_config_internal()` because it reuses the current connector set; it relies on callers already handling framebuffer references.
- Atomic drivers should not use these helpers; warnings and `-EINVAL` guard that boundary.
- Default primary disable returns `-EINVAL`, which can surprise userspace trying to hide a primary plane.

## Test Signals

Tests should cover visible and invisible update paths, no-scaling validation, connector enumeration under lock, allocation failure, `set_config()` error propagation, primary disable returning `-EINVAL`, destroy cleanup, and rejection on atomic drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_plane_helper.c -->
