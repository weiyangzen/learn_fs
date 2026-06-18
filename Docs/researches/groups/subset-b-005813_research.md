# subset-b-005813 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_pagemap.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_pagemap.h

## Purpose
`drm_pagemap.h` declares DRM's device-private pagemap interface for GPU shared virtual memory, peer-to-peer handshaking, and migration between system RAM and device memory. It wraps Linux `dev_pagemap` / `ZONE_DEVICE` pages with DRM-specific ownership, mapping, migration, and lifetime callbacks.

## Important APIs, types, and functions
Core types are `struct drm_pagemap`, `struct drm_pagemap_ops`, `struct drm_pagemap_addr`, `struct drm_pagemap_devmem`, `struct drm_pagemap_devmem_ops`, and `struct drm_pagemap_migrate_details`. `drm_pagemap_addr_encode()` packs an address, interconnect protocol, page order, and DMA direction. `drm_pagemap_ops` supplies `device_map`, `device_unmap`, `populate_mm`, and `destroy`. Public ZONE_DEVICE-gated functions include `drm_pagemap_init`, `drm_pagemap_create`, `drm_pagemap_page_to_dpagemap`, `drm_pagemap_put`, `drm_pagemap_migrate_to_devmem`, `drm_pagemap_evict_to_ram`, `drm_pagemap_populate_mm`, `drm_pagemap_destroy`, and `drm_pagemap_reinit`.

## Control flow
Drivers create or initialize a `drm_pagemap` for a `dev_pagemap`, map pages for DMA or driver-defined interconnects through `device_map`, and populate user address ranges through `populate_mm`. Migration uses device-memory allocations plus `copy_to_devmem` / `copy_to_ram`, optionally waiting on a pre-migration fence and respecting migration timeslice details. Teardown eventually calls `destroy`, which may run in atomic or reclaim context.

## State and persistence
State is runtime-only: kref lifetime, owning `drm_device`, underlying `dev_pagemap`, optional device-hold/cache/shrinker links, device memory allocation metadata, `mm_struct` association, detach completion, size, timeslice expiration, and pre-migration fence. No persistent storage exists. The CONFIG_ZONE_DEVICE stubs make calls harmless no-ops or NULL returns when device pages are unavailable.

## Dependencies and integration points
The header depends on `linux/hmm.h`, `memremap.h`, DMA direction definitions, `dev_pagemap`, page/folio zone-device data, DRM device ownership, and dma-fence synchronization. It integrates with GPU SVM, HMM migration, device-private memory providers, shrinker/cache helpers, peer interconnect mapping, and driver unbind/runtime power handling.

## Risks and test signals
Risks include stale device references after unbind, migration while hardware is removed, incorrect DMA direction/order encoding, copying ranges where only the head entry carries a higher order mapping, destroy callbacks called from reclaim context, and same-pagemap peer migration policy mistakes. Test signals include CONFIG_ZONE_DEVICE on/off builds, migrate-to-device and evict-to-RAM paths, device-unbind migration fallback, fence-delayed migration, higher-order mappings, NULL/stub behavior, and lockdep/reclaim-context teardown coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_pagemap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_pagemap_util.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_pagemap_util.h

## Purpose
`drm_pagemap_util.h` declares helper infrastructure around DRM pagemaps: peer-owner discovery, pagemap caches, shrinker integration, and lookup locking for active device memory mappings.

## Important APIs, types, and functions
The main types are `struct drm_pagemap_peer`, which embeds into driver peer objects, and `struct drm_pagemap_owner_list`, which groups peers sharing fast interconnect ownership. `DRM_PAGEMAP_OWNER_LIST_DEFINE()` statically initializes an owner list. APIs include `drm_pagemap_shrinker_add`, `drm_pagemap_shrinker_create_devm`, `drm_pagemap_cache_create_devm`, `drm_pagemap_get_from_cache`, `drm_pagemap_cache_set_pagemap`, `drm_pagemap_get_from_cache_if_active`, `drm_pagemap_cache_lock_lookup`, `drm_pagemap_cache_unlock_lookup`, `drm_pagemap_release_owner`, and `drm_pagemap_acquire_owner`. Under `CONFIG_PROVE_LOCKING`, `drm_pagemap_shrinker_might_lock()` exposes lock-order checking.

## Control flow
Drivers register peers in a shared owner list and provide a `has_interconnect()` predicate to group compatible peers under a common owner. Pagemap caches expose lookup locking so callers can safely acquire an active pagemap reference while excluding cache replacement. Shrinker-created pagemaps are added to shrinker lists for reclaim pressure handling.

## State and persistence
State is in in-memory lists, mutexes, cache references, and shrinker links. `drm_pagemap_peer.private` allows embedding drivers to connect back to their own structures. There is no persistence across driver lifetime.

## Dependencies and integration points
The header depends on list and mutex primitives plus the pagemap core. It is intended for GPU SVM drivers that need common owner tracking for fast peer paths and reclaim-aware pagemap caches.

## Risks and test signals
Risks include lock inversion between owner-list mutexes and shrinker/cache locks, stale peer links during driver removal, cache lookup races with deactivation, and incorrect interconnect grouping causing unsafe peer copies. Test signals include lockdep with `CONFIG_PROVE_LOCKING`, peer add/remove under concurrent migration, cache active/inactive lookup tests, shrinker reclaim under memory pressure, and driver unload while peers or cached pagemaps are still referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_pagemap_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_panel.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_panel.h

## Purpose
`drm_panel.h` defines the DRM panel abstraction used by display drivers to model fixed display panels, their power sequencing, mode discovery, optional backlight integration, orientation, timings, debugfs hooks, and dependent follower devices.

## Important APIs, types, and functions
Important types are `struct drm_panel`, `struct drm_panel_funcs`, `struct drm_panel_follower`, and `struct drm_panel_follower_funcs`. Panel callbacks include `prepare`, `enable`, `disable`, `unprepare`, mandatory `get_modes`, optional `get_orientation`, `get_timings`, and `debugfs_init`. The public API includes `drm_panel_init`, `drm_panel_get`, `drm_panel_put`, `drm_panel_add`, `drm_panel_remove`, `drm_panel_prepare`, `drm_panel_unprepare`, `drm_panel_enable`, `drm_panel_disable`, `drm_panel_get_modes`, and `devm_drm_panel_alloc`. OF helpers and follower helpers are conditionally compiled.

## Control flow
A panel driver initializes or devm-allocates an embedded `drm_panel`, provides callback operations, registers it, and supplies display modes to a connector. Display pipelines call prepare before video transmission, enable after scanout is active, disable before stopping scanout, and unprepare for power-down. Backlight can be controlled automatically when panel backlight helpers attach it. Followers receive notifications around prepared/enabled and disabling/unpreparing transitions.

## State and persistence
Runtime state includes parent device, optional backlight, connector type, registry/follower list links, follower mutex, `prepare_prev_first`, `prepared`, `enabled`, container pointer, and kref. The state is not persistent; it tracks object lifetime and current power/visibility sequencing.

## Dependencies and integration points
This header integrates with device tree, DRM connectors, backlight class devices, display timings, panel orientation properties, debugfs, DSI/bridge pipelines, and the DRM panel registry. Config stubs return `-ENODEV`, false, or no-op values when panel support is absent.

## Risks and test signals
Risks include unbalanced prepare/enable transitions, backlight control duplicated by drivers and helpers, follower lifetime races, missing `get_modes`, incorrect connector type, module/refcount leaks, and OF lookup behavior when CONFIG_OF or CONFIG_DRM_PANEL is disabled. Test signals include panel probe/remove, repeated DPMS cycles, automatic backlight sequencing, follower add/remove and callback ordering, orientation/timing retrieval, DSI `prepare_prev_first`, and config-off stub builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_panel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_panic.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_panic.h

## Purpose
`drm_panic.h` exposes the minimal DRM interfaces needed to draw a panic screen into a scanout buffer from panic context. It describes the scanout buffer layout and locking rules for state that panic printing may safely touch.

## Important APIs, types, and functions
`struct drm_scanout_buffer` carries format, `iosys_map` mappings, optional page array, dimensions, per-plane pitch, optional `set_pixel` callback for special layouts, and private callback data. With `CONFIG_DRM_PANIC`, `drm_panic_trylock`, `drm_panic_lock`, and `drm_panic_unlock` map to raw spinlock irqsave operations on `drm_device.mode_config.panic_lock`. Optional QR helpers are declared under `CONFIG_DRM_PANIC_SCREEN_QR_CODE`.

## Control flow
Panic code tries to acquire the panic lock and aborts drawing if it cannot. While held, it may access software state protected by the lock and invariant state between DRM device register/unregister boundaries. Pixel writing uses either the driver `set_pixel` hook, linear mappings, or per-page panic-safe kmap. Unlock restores IRQ flags.

## State and persistence
The header itself stores no state beyond the scanout buffer descriptor supplied by a driver. Persistent assumptions are deliberately narrow: plane lists and invariant plane state are considered stable only within device registration, while dynamic hardware access must be explicitly protected.

## Dependencies and integration points
It depends on DRM device/mode config locking, fourcc format metadata, `iosys_map`, kmsg/panic infrastructure, and optional QR code panic-screen code. It integrates with atomic helper state swapping, framebuffer pinning from plane helper callbacks, and drivers that can expose a linear panic scanout path.

## Risks and test signals
Risks include taking non-panic-safe locks, assuming hardware state without panic-lock protection, dereferencing state set up only by begin/end framebuffer access, invalid linear pitch/format metadata, and fallback stubs that silently disable real locking when panic support is off. Test signals include CONFIG_DRM_PANIC on/off builds, forced panic screen rendering, non-linear `set_pixel` paths, page-array scanout without preallocated maps, QR-code builds, and lockdep or panic-notifier review for atomic-context safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_panic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_pciids.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_pciids.h

## Purpose
`drm_pciids.h` provides a large macro, `radeon_PCI_IDS`, containing legacy AMD/ATI Radeon PCI device IDs and associated driver chip-family flags. It is a data include used to build Radeon PCI ID tables.

## Important APIs, types, and functions
There are no functions or structs. The file defines `radeon_PCI_IDS` as a comma-separated list of PCI table initializer rows ending in `{0, 0, 0}`. Each row supplies vendor ID `0x1002`, device ID, wildcard subsystem IDs, class fields, and flag combinations such as `CHIP_R100`, `CHIP_RV380`, `CHIP_KAVERI`, `RADEON_IS_MOBILITY`, `RADEON_IS_IGP`, `RADEON_NEW_MEMMAP`, `RADEON_SINGLE_CRTC`, and `RADEON_IS_IGPGART`.

## Control flow
At compile time, Radeon driver code includes this macro inside a PCI device table definition. Runtime probe matching is then handled by the PCI core. Matching entries communicate chip family and quirks through the `driver_data` flag field used by the Radeon driver after probe.

## State and persistence
State is static build-time table data. It persists only as compiled module/kernel PCI match metadata and has no mutable runtime state in this header.

## Dependencies and integration points
The including source must define or include `PCI_ANY_ID`, chip-family constants, and Radeon flag constants. The resulting table integrates with PCI module aliases, device probing, and Radeon family-specific initialization paths.

## Risks and test signals
Risks include wrong chip family flags, missing mobile/IGP/new-memmap quirks, duplicate or stale IDs, macro syntax errors from trailing commas or line continuations, and table drift against upstream PCI IDs. Test signals include Radeon module alias generation, builds of the including driver, representative probe on old desktop/mobile/IGP families, comparison against known PCI ID databases, and regression checks that sentinel termination remains intact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_pciids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_plane.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_plane.h

## Purpose
`drm_plane.h` declares the central KMS plane object and its mutable state. Planes represent scanout hardware that samples a framebuffer, applies positioning, scaling, blending, color conversion, and damage tracking, then feeds pixels to a CRTC.

## Important APIs, types, and functions
Key types are `struct drm_plane_state`, `struct drm_plane_funcs`, `enum drm_plane_type`, and `struct drm_plane`. State fields include CRTC/framebuffer/fence links, source and destination rectangles, cursor hotspot, alpha, blend mode, rotation, zpos, color encoding/range, damage clips, scaling filter, color pipeline, commit, and color-management change flags. Driver hooks cover legacy update/disable, cleanup/reset, legacy and atomic properties, atomic state duplication/destruction/printing, late/early userspace registration, and format/modifier support. APIs include `drm_universal_plane_init`, `drmm_universal_plane_alloc`, `drm_universal_plane_alloc`, `drm_plane_cleanup`, `drm_plane_find`, `drm_plane_has_format`, damage helpers, scaling filter property creation, size hints, and color pipeline property creation.

## Control flow
Drivers create planes with supported formats/modifiers and possible CRTC masks. Legacy paths use `update_plane` and `disable_plane`; atomic drivers duplicate state, set properties into the pending state, validate in atomic check, and commit prepared state to hardware. Iteration macros traverse all planes, legacy overlay-only planes, or masked plane sets. Damage blobs and derived `src` / `dst` rectangles are consumed by atomic helpers and drivers.

## State and persistence
Plane objects are registered for the DRM device lifetime; mutable atomic state is protected by the plane modeset lock and commit ordering. Non-atomic `crtc`, `fb`, and `old_fb` fields remain only for legacy drivers. Property pointers persist after creation. There is no storage persistence.

## Dependencies and integration points
The header depends on DRM mode objects, rectangles, color management, modeset locks, framebuffers, dma-fence, kmsg panic dump registration, atomic state, and CRTC/connector integration. It is used by virtually all KMS display drivers and helpers.

## Risks and test signals
Risks include direct mutation of state fields instead of atomic setters, stale fence/framebuffer references during nonblocking commits, incorrect format/modifier filtering, bad zpos normalization, damage clip coordinate mistakes, cursor hotspot property mishandling, panic dumper lifetime issues, and legacy/atomic semantic mismatches. Test signals include atomic plane update/disable, universal plane enumeration, modifier validation, damage tracking, zpos conflicts, color properties, cursor planes, nonblocking commit teardown, and KMS plane selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_plane_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_plane_helper.h

## Purpose
`drm_plane_helper.h` declares legacy helper callbacks for simple non-atomic primary plane handling. The header explicitly marks non-atomic interfaces as deprecated for new drivers.

## Important APIs, types, and functions
Exports are `drm_plane_helper_update_primary`, `drm_plane_helper_disable_primary`, and `drm_plane_helper_destroy`. `DRM_PLANE_NON_ATOMIC_FUNCS` initializes a `drm_plane_funcs` table with those helpers as update, disable, and destroy operations.

## Control flow
Non-atomic drivers can wire the macro into their plane functions. Legacy `SETPLANE` or primary plane update paths call the helper update path with CRTC, framebuffer, destination rectangle, and 16.16 source rectangle parameters. Disabling calls the helper disable path, and unload calls destroy cleanup.

## State and persistence
The header owns no state. It manipulates the legacy plane state stored in `struct drm_plane` and related CRTC/framebuffer objects via the implementation in the helper source.

## Dependencies and integration points
It depends only on forward declarations for CRTC, framebuffer, modeset acquire context, and plane. It integrates with older KMS drivers that still expose non-atomic plane operations.

## Risks and test signals
Risks include new drivers depending on deprecated non-atomic behavior, helper use on hardware needing full atomic validation, source/destination scaling mismatches, and modeset locking errors through the acquire context. Test signals include legacy primary update and disable ioctls, driver unload cleanup, lock backoff/retry behavior, and migration tests from `DRM_PLANE_NON_ATOMIC_FUNCS` to atomic helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_plane_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_prime.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_prime.h

## Purpose
`drm_prime.h` declares DRM PRIME helpers for exporting and importing GEM buffer objects through dma-buf file descriptors. It provides per-file caches, dma-buf operations, scatter-gather conversion, mmap/vmap helpers, and handle/fd translation.

## Important APIs, types, and functions
`struct drm_prime_file_private` contains private rb-tree caches for dma-bufs and handles protected by a mutex. Core APIs include `drm_gem_prime_fd_to_handle`, `drm_gem_prime_handle_to_dmabuf`, `drm_gem_prime_handle_to_fd`, `drm_gem_dmabuf_export`, and `drm_gem_dmabuf_release`. Export helpers include `drm_gem_map_attach`, `drm_gem_map_detach`, `drm_gem_map_dma_buf`, `drm_gem_unmap_dma_buf`, `drm_gem_dmabuf_vmap`, `drm_gem_dmabuf_vunmap`, `drm_gem_prime_mmap`, `drm_gem_dmabuf_mmap`, `drm_prime_pages_to_sg`, and `drm_gem_prime_export`. Import helpers include `drm_gem_is_prime_exported_dma_buf`, `drm_gem_prime_import_dev`, `drm_gem_prime_import`, `drm_prime_gem_destroy`, and SG extraction helpers.

## Control flow
Export converts a GEM handle to a dma-buf and then to an fd while caching associations per file. Import converts a PRIME fd to a dma-buf, attaches/maps as needed, and returns a GEM handle or object. DMA mappings use sg-tables and direction-specific map/unmap operations. Mmap/vmap helpers bridge GEM memory into userspace or kernel mappings.

## State and persistence
State is per-open-file cache data plus dma-buf/GEM reference counts and attachment mappings. The data is runtime-only and ends when file handles and objects are closed/released.

## Dependencies and integration points
This header integrates GEM, dma-buf, scatterlist/sg_table, devices, iosys maps, vm areas, and DRM file-private handle namespaces. It is the main cross-driver buffer sharing interface.

## Risks and test signals
Risks include fd/handle cache races, reference leaks, mapping direction mismatches, importing one's own exported dma-buf incorrectly, SG table size assumptions, mmap permission issues, and stale attachments after device removal. Test signals include PRIME export/import round trips, self-import, cross-device sharing, mmap/vmap, SG conversion, fd close and handle close ordering, and IGT PRIME tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_prime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_print.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_print.h

## Purpose
`drm_print.h` centralizes DRM logging and printable output streams. It provides `drm_printer` abstractions for debugfs, devcoredump, device logs, debug logs, error logs, line-numbered dumps, and DRM-specific printk/dev_printk wrappers.

## Important APIs, types, and functions
Important types are `enum drm_debug_category`, `struct drm_printer`, and `struct drm_print_iterator`. Categories map to `drm.debug` bits such as CORE, DRIVER, KMS, PRIME, ATOMIC, VBL, STATE, LEASE, DP, and DRMRES. Printer constructors include `drm_coredump_printer`, `drm_seq_file_printer`, `drm_info_printer`, `drm_dbg_printer`, `drm_err_printer`, and `drm_line_printer`. Output APIs include `drm_printf`, `drm_puts`, `drm_vprintf`, `drm_print_regset32`, `drm_print_bits`, and `drm_print_hex_dump`. Logging macros cover `drm_info`, `drm_warn`, `drm_err`, category-specific `drm_dbg_*`, ratelimited debug/error variants, deprecated `DRM_*` and `DRM_DEV_*` macros, and device-aware `drm_WARN*`.

## Control flow
Callers construct a printer for the target sink, then pass it to shared dump functions. Debug logging first checks either `__drm_debug` bits or dynamic-debug class callsites depending on configuration. Coredump printing uses an iterator offset/remain model for read callbacks or two-pass buffered generation.

## State and persistence
Global debug state is `__drm_debug`, typically controlled by the `drm.debug` module parameter/sysfs. Printer state is stack/local and records sink callback pointers, argument, origin, prefix, line counter, and category. Static ratelimit and once flags persist for each callsite.

## Dependencies and integration points
The header depends on printk, dev_printk, dynamic debug, debugfs regsets, seq_file, devcoredump-style iterators, DRM device metadata, and WARN infrastructure. It is used throughout DRM diagnostics.

## Risks and test signals
Risks include using deprecated printk-style macros in new code, expensive formatting when debug is disabled, missing device context in logs, coredump O(N^2) generation for large dumps, incorrect format attributes, and ratelimit hiding important errors. Test signals include dynamic debug on/off builds, `drm.debug` runtime toggling, debugfs printer output, devcoredump reads at offsets, line printer numbering, ratelimited logs, and compile-time format checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_print.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_privacy_screen_consumer.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_privacy_screen_consumer.h

## Purpose
`drm_privacy_screen_consumer.h` declares the consumer-facing API for display drivers or connectors that use a privacy-screen provider, such as laptop display privacy filters.

## Important APIs, types, and functions
When `CONFIG_DRM_PRIVACY_SCREEN` is enabled, consumers can call `drm_privacy_screen_get`, `drm_privacy_screen_put`, `drm_privacy_screen_set_sw_state`, `drm_privacy_screen_get_state`, `drm_privacy_screen_register_notifier`, and `drm_privacy_screen_unregister_notifier`. Disabled stubs return `ERR_PTR(-ENODEV)`, `-ENODEV`, no-op, or disabled software/hardware status values.

## Control flow
A consumer resolves a provider by device and connector ID, reads current software and hardware states, requests software state changes, and optionally registers a notifier for provider state updates. Reference release uses `drm_privacy_screen_put`.

## State and persistence
The header stores no state. State lives in the provider object and includes software and hardware privacy status. Stub behavior reports privacy disabled when the subsystem is not compiled.

## Dependencies and integration points
It depends on `linux/device.h` and DRM connector privacy-screen status enums. It integrates with connector properties and provider drivers registered through the driver-facing privacy-screen API.

## Risks and test signals
Risks include treating `-ENODEV` as fatal when privacy support is optional, missing notifier unregister on connector teardown, mismatched connector IDs, and stale references after provider unregister. Test signals include config-enabled and config-disabled builds, connector property updates, notifier delivery, get/put lifetime, provider removal while a consumer exists, and locked hardware-state behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_privacy_screen_consumer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_privacy_screen_driver.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_privacy_screen_driver.h

## Purpose
`drm_privacy_screen_driver.h` declares the provider-side privacy-screen class interface. It lets hardware-specific drivers register privacy-screen devices, expose state through sysfs/DRM connector integration, and notify consumers of changes.

## Important APIs, types, and functions
`struct drm_privacy_screen_ops` provides `set_sw_state` and `get_hw_state`. `struct drm_privacy_screen` embeds a `struct device`, mutex, global list link, blocking notifier head, ops pointer, software and hardware state, and provider `drvdata`. APIs are `drm_privacy_screen_register`, `drm_privacy_screen_unregister`, `drm_privacy_screen_call_notifier_chain`, and `drm_privacy_screen_get_drvdata`.

## Control flow
A provider registers with parent device, ops, and private data. The core calls `get_hw_state` before sysfs registration and calls `set_sw_state` under the privacy-screen mutex when a consumer requests a change and the hardware state is not locked. Providers update both sw and hw state and invoke the notifier chain when state changes.

## State and persistence
Runtime state is in the privacy-screen object: device registration, locking, list membership, notifier subscribers, ops validity, software/hardware status, and private data. `ops` becomes NULL after unregister to prevent calls into a removed driver. Hardware privacy state may persist outside the kernel, but this header only models the runtime view.

## Dependencies and integration points
It depends on the Linux device model, mutex/list/notifier infrastructure, and DRM connector privacy status enums. It integrates with sysfs, machine lookup tables, and consumer APIs used by DRM connectors.

## Risks and test signals
Risks include provider unregister racing with consumer calls, failing to update both state fields, notifier callbacks under locks causing deadlocks, incorrect handling of locked hardware state, and sysfs lifetime mistakes. Test signals include provider register/unregister, sysfs state read/write, locked-state refusal, notifier ordering, consumer get during unregister, and driver-private data access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_privacy_screen_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_privacy_screen_machine.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_privacy_screen_machine.h

## Purpose
`drm_privacy_screen_machine.h` declares static machine lookup support that maps consumer device/connector pairs to privacy-screen providers when firmware topology is not discoverable generically.

## Important APIs, types, and functions
`struct drm_privacy_screen_lookup` records a list link, optional consumer `dev_id`, optional connector `con_id`, and provider `dev_name()`. APIs are `drm_privacy_screen_lookup_add`, `drm_privacy_screen_lookup_remove`, and x86/config-gated `drm_privacy_screen_lookup_init` / `drm_privacy_screen_lookup_exit`.

## Control flow
Platform code or module init installs lookup entries. Consumer lookup can then match by device name and connector name, with NULL fields acting as wildcards, and resolve the named provider. Lookup entries are removed during platform or module teardown.

## State and persistence
State is an in-memory static lookup list. It persists only for the loaded kernel/module lifetime and is empty/no-op when privacy screen support or x86 machine lookup is unavailable.

## Dependencies and integration points
The header depends on list handling and integrates with privacy-screen consumer/provider resolution, especially on x86 laptops requiring DMI or machine-specific mapping.

## Risks and test signals
Risks include too-broad wildcard matches, stale provider device names, missing removal of static entries, x86-only assumptions, and matching connector names that change across drivers. Test signals include lookup add/remove, wildcard and exact matching, config-disabled stubs, machine-specific DMI initialization, and consumer resolution on systems with multiple panels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_privacy_screen_machine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_probe_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_probe_helper.h

## Purpose
`drm_probe_helper.h` declares KMS helper functions for connector probing, hotplug detection, polling, fixed-mode connectors, TV mode enumeration, and DDC-based detection.

## Important APIs, types, and functions
Probe APIs include `drm_helper_probe_single_connector_modes` and `drm_helper_probe_detect`. Polling/hotplug APIs include `drmm_kms_helper_poll_init`, `drm_kms_helper_poll_init`, `drm_kms_helper_poll_fini`, `drm_helper_hpd_irq_event`, `drm_connector_helper_hpd_irq_event`, `drm_kms_helper_hotplug_event`, `drm_kms_helper_connector_hotplug_event`, `drm_kms_helper_poll_disable`, `drm_kms_helper_poll_enable`, `drm_kms_helper_poll_reschedule`, and `drm_kms_helper_is_poll_worker`. Fixed-mode helpers include `drm_crtc_helper_mode_valid_fixed`, `drm_connector_helper_get_modes_fixed`, `drm_connector_helper_get_modes`, `drm_connector_helper_tv_get_modes`, and `drm_connector_helper_detect_from_ddc`.

## Control flow
Drivers initialize polling, connector probes call detect and get-modes helpers, hotplug IRQs call device or connector event helpers, and polling can be disabled during sensitive modeset phases then rescheduled. Fixed-panel helpers validate and expose a fixed display mode.

## State and persistence
The header owns no state. Implementation state lives in DRM mode config polling infrastructure, connectors, and mode lists. Hotplug and polling state is runtime-only.

## Dependencies and integration points
It depends on DRM modes, connectors, CRTCs, devices, modeset acquire contexts, DDC/I2C helpers through implementations, and sysfs/uevent hotplug reporting.

## Risks and test signals
Risks include polling races with HPD IRQs, connector locks acquired through the modeset context, missing hotplug events after state changes, invalid fixed-mode filtering, and DDC failures misclassified as disconnects. Test signals include HPD IRQ storms, poll enable/disable cycles, forced detection, fixed-panel mode enumeration, TV connector modes, DDC failure injection, and KMS hotplug uevents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_probe_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_property.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_property.h

## Purpose
`drm_property.h` defines KMS object properties and blob properties. Properties are the generic metadata and atomic state transport used by connectors, CRTCs, planes, framebuffers, and userspace IOCTLs.

## Important APIs, types, and functions
Important types are `struct drm_property_enum`, `struct drm_property`, `struct drm_property_blob`, and `struct drm_prop_enum_list`. `drm_property_type_is()` handles legacy and extended type encodings. Creation APIs include `drm_property_create`, `_enum`, `_bitmask`, `_range`, `_signed_range`, `_object`, and `_bool`, plus `drm_property_add_enum` and `drm_property_destroy`. Blob APIs include `drm_property_create_blob`, `drm_property_lookup_blob`, `drm_property_replace_blob_from_id`, `drm_property_replace_global_blob`, `drm_property_replace_blob`, `drm_property_blob_get`, and `drm_property_blob_put`. `drm_property_find()` wraps mode-object lookup.

## Control flow
Drivers create property definitions, populate enum/bitmask values, attach properties to mode objects, and let the core validate user-provided values against ranges, object types, or blob IDs. Atomic IOCTL state is expressed by setting properties, while immutable properties can still be updated by the kernel.

## State and persistence
Property definitions live on the DRM device property list. Blobs are refcounted mode objects on global and per-file lists, with immutable data length and embedded data. State is runtime-only and tied to device/file/object lifetimes.

## Dependencies and integration points
The header depends on mode object lookup, UAPI property flags, DRM file leasing checks, and KMS object property attachment. It underpins standard and driver-private KMS properties such as EDID blobs, rotation, zpos, CRTC links, framebuffer links, and damage clips.

## Risks and test signals
Risks include incorrect property type flags, signed/unsigned range confusion, enum value drift with UAPI, blob refcount leaks, accepting blobs with wrong size, exposing duplicate property names with incompatible ranges, and lease visibility mistakes. Test signals include atomic property set/get, blob create/replace/free, enum/bitmask validation, immutable property updates, lease-filtered lookup, and KMS property IOCTL fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_property.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_ras.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_ras.h

## Purpose
`drm_ras.h` declares DRM reliability/availability/serviceability node registration for exposing driver error counters through the DRM RAS netlink/UAPI layer.

## Important APIs, types, and functions
`struct drm_ras_node` contains dynamically assigned `id`, driver-provided `device_name` and `node_name`, a UAPI `enum drm_ras_node_type`, an inclusive `error_counter_range`, a mandatory `query_error_counter` callback for error-counter nodes, and driver-private `priv`. APIs are `drm_ras_node_register` and `drm_ras_node_unregister`, with no-op success stubs when `CONFIG_DRM_RAS` is disabled.

## Control flow
A driver fills a node, including supported error ID range and query callback, then registers it. Netlink queries iterate IDs from `first` to `last`; `-ENOENT` means skip an unsupported non-contiguous ID, while other errors terminate the query. Unregister removes the node from the RAS service.

## State and persistence
State is runtime node registration and counter values queried live from the driver. Error counts may be hardware-maintained, but this header only describes access and registration state.

## Dependencies and integration points
It depends on `uapi/drm/drm_ras.h` and integrates with the DRM RAS generic netlink family plus driver error counter providers.

## Risks and test signals
Risks include registering nodes with invalid ranges, callbacks returning inconsistent names/values, failure to unregister before driver data is freed, treating `-ENOENT` as fatal, and config-disabled stubs hiding missing runtime support. Test signals include CONFIG_DRM_RAS on/off builds, node register/unregister, contiguous and sparse error ranges, netlink query error handling, device removal during query, and UAPI enum compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_ras.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_ras_genl_family.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_ras_genl_family.h

## Purpose
`drm_ras_genl_family.h` declares lifecycle hooks for the DRM RAS generic netlink family.

## Important APIs, types, and functions
The only APIs are `drm_ras_genl_family_register` and `drm_ras_genl_family_unregister`. They are real declarations when `CONFIG_DRM_RAS` is enabled and inline no-op success/empty stubs otherwise.

## Control flow
DRM RAS subsystem initialization registers the generic netlink family before serving RAS queries. Cleanup unregisters it so userspace can no longer issue family commands.

## State and persistence
The header stores no state. Netlink family registration is global runtime state managed by the implementation and removed on subsystem exit.

## Dependencies and integration points
It integrates the DRM RAS node layer with Linux generic netlink registration. It is intentionally small to separate family lifecycle from node provider declarations.

## Risks and test signals
Risks include register/unregister ordering relative to node registration, double unregister, config-disabled code assuming a userspace API exists, and family registration failure propagation. Test signals include CONFIG_DRM_RAS on/off builds, module init failure injection, generic netlink family visibility, and cleanup after registered nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_ras_genl_family.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_rect.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_rect.h

## Purpose
`drm_rect.h` provides rectangle utilities for DRM clipping, scaling, rotation, damage, and plane source/destination calculations. It uses inclusive start and exclusive end coordinates.

## Important APIs, types, and functions
`struct drm_rect` stores `x1`, `y1`, `x2`, and `y2` and must match `struct drm_mode_rect` layout. Macros include `DRM_RECT_INIT`, `DRM_RECT_FMT`, `DRM_RECT_ARG`, `DRM_RECT_FP_FMT`, and `DRM_RECT_FP_ARG`. Inline helpers initialize, resize, translate, downscale, compute width/height, check visibility/equality/overlap, and convert 16.16 fixed-point rectangles to integer rectangles. External helpers include `drm_rect_intersect`, `drm_rect_clip_scaled`, `drm_rect_calc_hscale`, `drm_rect_calc_vscale`, `drm_rect_debug_print`, `drm_rect_rotate`, and `drm_rect_rotate_inv`.

## Control flow
Plane and damage helpers construct rectangles from user input, clip destination rectangles to CRTC bounds, adjust corresponding source rectangles, validate scaling ratios against hardware limits, rotate coordinates for transformed scanout, and print diagnostics in integer or fixed-point form.

## State and persistence
All state is caller-owned rectangle values. The helpers are pure transformations or predicates and have no persistent state.

## Dependencies and integration points
The header depends only on basic Linux types. It integrates with KMS plane state, damage clips, atomic check helpers, rotation properties, and debug output.

## Risks and test signals
Risks include fixed-point truncation, negative or zero-sized rectangles, overflow in `x + width`, off-by-one errors from exclusive end coordinates, division by zero in downscale/scaling calculations, and layout drift from `drm_mode_rect`. Test signals include clipping partially/off-screen planes, rotation/inverse rotation matrices, min/max scaling boundaries, fixed-point print conversion, overlap/equality edge cases, and damage helper compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_rect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_self_refresh_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_self_refresh_helper.h

## Purpose
`drm_self_refresh_helper.h` declares helpers for panel self-refresh / display self-refresh support in atomic KMS drivers.

## Important APIs, types, and functions
APIs are `drm_self_refresh_helper_alter_state`, `drm_self_refresh_helper_update_avg_times`, `drm_self_refresh_helper_init`, and `drm_self_refresh_helper_cleanup`. They operate on `struct drm_atomic_state` and `struct drm_crtc`.

## Control flow
Drivers initialize helper state for a CRTC, then atomic commit paths call `alter_state` to adjust commits for self-refresh transitions and `update_avg_times` with commit duration and the new self-refresh mask. Cleanup removes helper state on CRTC teardown.

## State and persistence
The header owns no direct fields, but the implementation maintains runtime helper state associated with the CRTC, including timing averages used to decide self-refresh behavior. No persistent storage is involved.

## Dependencies and integration points
It integrates with atomic state management, CRTC power sequencing, panels that support self-refresh, and commit timing heuristics.

## Risks and test signals
Risks include entering self-refresh while updates are pending, stale timing averages, missing cleanup, incorrect mask handling across multiple CRTCs, and power-saving transitions that break visible updates. Test signals include PSR/self-refresh entry and exit, atomic commits with and without damage, multi-CRTC commits, suspend/resume, commit-time accounting, and helper cleanup during driver unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_self_refresh_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_simple_kms_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_simple_kms_helper.h

## Purpose
`drm_simple_kms_helper.h` declares the deprecated simple display pipe helpers that combine a CRTC, primary plane, encoder, and optional connector for very simple KMS drivers.

## Important APIs, types, and functions
`struct drm_simple_display_pipe_funcs` supplies callbacks for mode validation, enable/disable, atomic check/update, framebuffer prepare/cleanup/access, vblank enable/disable, and optional CRTC/plane state reset/duplicate/destroy hooks. `struct drm_simple_display_pipe` embeds `drm_crtc`, `drm_plane`, `drm_encoder`, connector pointer, and funcs pointer. APIs include `drm_simple_display_pipe_attach_bridge`, `drm_simple_display_pipe_init`, `drm_simple_encoder_init`, `__drmm_simple_encoder_alloc`, and `drmm_simple_encoder_alloc`.

## Control flow
A simple driver initializes the pipe with formats, modifiers, connector, and callbacks. Atomic helper paths call pipe callbacks to validate modes, prepare framebuffer access, enable or update scanout, and clean up. Bridge attachment wires the simple encoder path into bridge chains.

## State and persistence
State is embedded in the DRM objects that make up the pipe plus driver-private container data. It persists for the DRM device lifetime but does not survive unload/reprobe.

## Dependencies and integration points
It depends on DRM CRTC, encoder, and plane definitions. It integrates with atomic helpers, bridges, connectors, vblank helpers, and managed DRM allocation for simple encoders.

## Risks and test signals
Risks include using a deprecated helper for new complex hardware, insufficient atomic validation, framebuffer access callbacks mismatched with panic or dynamic buffer management, missing vblank hooks, and bridge/connector ownership confusion. Test signals include simple pipe init, bridge attach, enable/update/disable commits, framebuffer prepare/cleanup balance, vblank enable/disable, and managed encoder cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_simple_kms_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_suballoc.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_suballoc.h

## Purpose
`drm_suballoc.h` declares a fenced range suballocator for DRM memory regions, useful for temporary or reusable suballocations whose reuse is delayed by dma-fence completion.

## Important APIs, types, and functions
`struct drm_suballoc_manager` stores a wait queue, hole pointer, ordered allocation list, hash-bucketed fenced lists, total size, and default alignment. `struct drm_suballoc` stores list links, manager pointer, start/end offsets, and a protecting fence. APIs include `drm_suballoc_manager_init`, `drm_suballoc_manager_fini`, `drm_suballoc_alloc`, `drm_suballoc_insert`, `drm_suballoc_new`, `drm_suballoc_free`, accessors for start/end/size, and optional `drm_suballoc_dump_debug_info` under `CONFIG_DEBUG_FS`.

## Control flow
Drivers initialize a manager for a range, allocate or provide `drm_suballoc` nodes, insert them with requested size/alignment and optional interruptible waiting, then free ranges with an optional fence. Fenced frees defer actual reuse until the fence signals, while waiters sleep on the manager waitqueue during contention.

## State and persistence
State is in memory: allocation lists, fence queues, waiters, offsets, and fence references. It does not persist across manager teardown.

## Dependencies and integration points
It depends on `drm_mm`, dma-fence, wait queues, debugfs printers, and kernel allocation flags. It can back GPU-visible scratch, descriptor, or address-space subranges where fence-ordered reuse matters.

## Risks and test signals
Risks include alignment fragmentation, fence reference leaks, waking waiters too early or too late, hash bucket collisions hiding completion, freeing nodes still in use by hardware, and teardown with outstanding allocations. Test signals include allocation/free/reuse under fences, interruptible allocation paths, no-space contention, alignment boundaries, debugfs dump output, and manager fini with active or fenced allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_suballoc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_syncobj.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_syncobj.h

## Purpose
`drm_syncobj.h` declares DRM synchronization objects, which wrap dma-fences and expose handle/fd-based synchronization primitives to userspace and scheduler code.

## Important APIs, types, and functions
`struct drm_syncobj` contains a kref, RCU-protected fence pointer, replacement callback list, eventfd list, spinlock, and optional file backing. Inline helpers are `drm_syncobj_get`, `drm_syncobj_put`, and `drm_syncobj_fence_get`. APIs include `drm_syncobj_find`, `drm_syncobj_add_point`, `drm_syncobj_replace_fence`, `drm_syncobj_find_fence`, `drm_syncobj_create`, `drm_syncobj_get_handle`, `drm_syncobj_get_fd`, and `drm_syncobj_free`.

## Control flow
Userspace or drivers create a syncobj with an optional initial fence, obtain handles/fds, replace the contained fence, add timeline points through fence chains, and look up fences by handle/point/flags. Fence reads are RCU-safe and return a referenced dma-fence. Replacement notifies callbacks and eventfds.

## State and persistence
State is per-object runtime synchronization state: reference count, current fence/timeline chain, callback and eventfd registrations, lock, and file backing. It persists only while references, handles, or fds remain.

## Dependencies and integration points
It depends on dma-fence, dma-fence-chain, RCU, kref, DRM file handle namespaces, eventfd integration in the implementation, and GPU scheduler dependency APIs.

## Risks and test signals
Risks include RCU misuse around fence replacement, callback list races, timeline point ordering errors, handle lifetime leaks, eventfd notification duplication, and failing to signal waits during object destruction. Test signals include binary and timeline syncobj creation, fence replacement under concurrent wait, fd export/import, handle lookup failure cases, eventfd signaling, scheduler syncobj dependencies, and refcount teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_syncobj.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_sysfs.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_sysfs.h

## Purpose
`drm_sysfs.h` declares DRM sysfs registration and event helpers for DRM class devices, connector hotplug, and connector property notifications.

## Important APIs, types, and functions
APIs are `drm_class_device_register`, `drm_class_device_unregister`, `drm_sysfs_hotplug_event`, `drm_sysfs_connector_hotplug_event`, and `drm_sysfs_connector_property_event`. The header forward-declares `drm_device`, `device`, `drm_connector`, and `drm_property`.

## Control flow
DRM devices register class devices with sysfs, unregister them during teardown, and emit uevents when global hotplug, connector hotplug, or connector property changes need to be visible to userspace.

## State and persistence
State lives in the Linux device model and connector objects. The header itself has no storage. Sysfs entries persist only while devices are registered.

## Dependencies and integration points
It integrates DRM device registration with sysfs, udev/hotplug userspace, connector property changes, and the Linux class device model.

## Risks and test signals
Risks include missing unregister calls, emitting uevents after connector removal, property event storms, userspace relying on event ordering, and null/stale connector or property pointers. Test signals include DRM device register/unregister, hotplug uevent observation, connector-specific hotplug, property change uevents, suspend/resume hotplug, and teardown race tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_util.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_util.h

## Purpose
`drm_util.h` contains small DRM-internal utility macros and helpers that do not fit naturally elsewhere.

## Important APIs, types, and functions
`EXPORT_SYMBOL_FOR_TESTS_ONLY(x)` exports a symbol only when `CONFIG_DRM_EXPORT_FOR_TESTS` is enabled; otherwise it expands to nothing. `drm_can_sleep()` returns false when in atomic context, kgdb master context, or with IRQs disabled, and true otherwise.

## Control flow
DRM selftest-only functions use the export macro to avoid making test hooks visible in production builds. Existing legacy code can call `drm_can_sleep()` before choosing a sleeping versus non-sleeping path, though the header explicitly says not to use it in new code.

## State and persistence
There is no persistent state. `drm_can_sleep()` samples current task/interrupt/debugger context.

## Dependencies and integration points
The header depends on interrupt state, kgdb, preemption/atomic context checks, SMP, and generic utility macros. It integrates with DRM selftests and legacy paths that still branch on sleepability.

## Risks and test signals
Risks include relying on an imperfect atomic-context check, adding new callers despite deprecation, accidental production exports when test config is enabled, and behavior differences under kgdb. Test signals include CONFIG_DRM_EXPORT_FOR_TESTS builds, atomic/IRQ-off calls to `drm_can_sleep`, kgdb active checks, and audits that new code does not depend on this helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_utils.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_utils.h

## Purpose
`drm_utils.h` declares miscellaneous DRM utility functions intended for use both inside DRM and by adjacent code such as fbdev drivers.

## Important APIs, types, and functions
APIs are `drm_get_panel_orientation_quirk`, `drm_get_panel_backlight_quirk`, and `drm_timeout_abs_to_jiffies`. `struct drm_panel_backlight_quirk` carries `min_brightness` and `brightness_mask`. `drm_get_panel_backlight_quirk` consumes a `struct drm_edid`.

## Control flow
Display code can query panel orientation quirks by physical width/height, query EDID-based panel backlight quirks, or convert absolute nanosecond timeouts to signed jiffies for wait APIs.

## State and persistence
The header owns no state. Quirk state is implemented elsewhere, likely as static tables, and timeout conversion is derived from current time/jiffies.

## Dependencies and integration points
It depends on basic Linux types and forward-declared DRM EDID data. It integrates with panel orientation handling, backlight drivers/helpers, EDID parsing, and timeout-based synchronization paths.

## Risks and test signals
Risks include overmatching physical-size quirks, stale EDID quirk tables, brightness masks that hide valid levels, timeout overflow or negative conversion errors, and external users depending on DRM internals. Test signals include known quirky panels, EDID-based backlight quirk lookup, timeout conversion for past/present/future deadlines, and fbdev/DRM cross-subsystem builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_vblank.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_vblank.h

## Purpose
`drm_vblank.h` declares DRM vertical blanking tracking, event delivery, timestamping, interrupt reference counting, vblank timers, and delayed vblank work infrastructure per CRTC.

## Important APIs, types, and functions
Key types are `struct drm_pending_vblank_event`, `struct drm_vblank_crtc_config`, `struct drm_vblank_crtc_timer`, and `struct drm_vblank_crtc`. Runtime fields track wait queues, disable timer, seqlock-protected count/time, refcount, wraparound data, max counter, modeset state, pipe, timing constants, cached hardware mode, config, enabled state, kthread worker, pending vblank work, and high-resolution timer. APIs include `drm_vblank_init`, `drm_dev_has_vblank`, `drm_crtc_vblank_count`, `drm_crtc_vblank_count_and_time`, event send/arm/set helpers, `drm_handle_vblank`, `drm_crtc_handle_vblank`, get/put/wait/off/on/reset/restore helpers, timestamping constants, waitqueue access, max counter setup, timer start/cancel/timeout, and helper timestamp functions.

## Control flow
Drivers initialize vblank tracking for CRTCs, enable vblank interrupts when users/events need them, call handle-vblank from IRQs, and release references after waits/events. Counts and timestamps are updated under seqlock with ordering guarantees. Off/on paths preserve counts across modesets. Timer paths can emulate or predict vblank timing where appropriate.

## State and persistence
All state is runtime per-CRTC tracking. Counters and timestamps persist while the DRM device is active but reset across driver unload. Refcounts govern whether hardware vblank interrupts remain enabled.

## Dependencies and integration points
It depends on seqlocks, hrtimers, IDR/poll/kthreads, DRM files/events, display modes, CRTC funcs, and vblank work. It integrates with page flips, atomic commits, legacy wait-vblank IOCTLs, event delivery, timestamp helpers, and hot modesets.

## Risks and test signals
Risks include refcount leaks disabling or keeping IRQs on, counter wraparound errors, timestamp inaccuracies, event sequence races, modeset off/on count loss, missing barriers around count/time, and timer interval drift. Test signals include vblank IRQ handling, page-flip event sequences, wait-vblank IOCTLs, counter wraparound, modeset disable/enable, timer-backed vblank, timestamp max-error validation, and vblank reference leak tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_vblank.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_vblank_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_vblank_helper.h

## Purpose
`drm_vblank_helper.h` declares helper callbacks for atomic vblank handling and hrtimer-backed vblank emulation.

## Important APIs, types, and functions
Atomic helper APIs are `drm_crtc_vblank_atomic_flush`, `drm_crtc_vblank_atomic_enable`, and `drm_crtc_vblank_atomic_disable`. `DRM_CRTC_HELPER_VBLANK_FUNCS` initializes helper function table entries for atomic flush/enable/disable. Timer APIs are `drm_crtc_vblank_helper_enable_vblank_timer`, `drm_crtc_vblank_helper_disable_vblank_timer`, and `drm_crtc_vblank_helper_get_vblank_timestamp_from_timer`; `DRM_CRTC_VBLANK_TIMER_FUNCS` maps them to CRTC funcs.

## Control flow
Atomic drivers can use the macro so atomic enable/disable/flush paths maintain vblank state. Drivers without hardware vblank IRQs or counters can use timer funcs to synthesize vblank timing and timestamps.

## State and persistence
The header stores no state. It manipulates `drm_vblank_crtc` state declared in `drm_vblank.h` and CRTC atomic state at runtime.

## Dependencies and integration points
It depends on hrtimer types, DRM atomic state, and CRTC objects. It integrates with `struct drm_crtc_helper_funcs`, `struct drm_crtc_funcs`, and vblank core state.

## Risks and test signals
Risks include enabling timer vblank on hardware that also generates IRQs, atomic disable ordering that drops pending events, timestamp inaccuracy from timer-only mode, and macro misuse in drivers with custom vblank sequencing. Test signals include atomic enable/disable, page flip event delivery through flush, timer-only vblank intervals, suspend/resume, and CRTC helper function table audits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_vblank_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_vblank_work.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_vblank_work.h

## Purpose
`drm_vblank_work.h` declares a delayed work abstraction that runs a `kthread_work` item after a target vblank at realtime priority, outside IRQ context.

## Important APIs, types, and functions
`struct drm_vblank_work` embeds a `kthread_work`, points to its `drm_vblank_crtc`, records target vblank count, tracks active cancel calls, and links into the per-CRTC pending work list. `to_drm_vblank_work()` converts from embedded work. APIs are `drm_vblank_work_schedule`, `drm_vblank_work_init`, `drm_vblank_work_cancel_sync`, `drm_vblank_work_flush`, and `drm_vblank_work_flush_all`.

## Control flow
Drivers initialize a vblank work item for a CRTC and callback, schedule it for a target count, and optionally request next-vblank execution if the target was missed. The vblank core queues it to the CRTC worker when the count is reached. Cancellation and flush APIs synchronize with pending or running work.

## State and persistence
State is runtime per work item plus per-CRTC pending lists and worker. Work items persist while owned by their driver and must not be rescheduled during active synchronous cancellation.

## Dependencies and integration points
It depends on kthread work and the vblank core. It integrates with `drm_vblank_crtc.worker`, `pending_work`, and `work_wait_queue` fields from `drm_vblank.h`.

## Risks and test signals
Risks include scheduling after CRTC teardown, target count races, missed-vblank policy mistakes, cancel/reschedule races, work running after resources are freed, and realtime worker starvation. Test signals include schedule for future/past vblanks, `nextonmiss` behavior, cancel while pending and running, flush all on CRTC shutdown, and concurrent scheduling from multiple contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_vblank_work.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_vma_manager.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_vma_manager.h

## Purpose
`drm_vma_manager.h` declares DRM's fake-offset manager for mapping buffer objects through userspace `mmap`. It allocates recognizable page offsets, tracks allowed DRM files, and provides unmap/access helpers.

## Important APIs, types, and functions
Constants `DRM_FILE_PAGE_OFFSET_START` and `DRM_FILE_PAGE_OFFSET_SIZE` define the fake offset range differently for 32-bit and 64-bit. Types include `struct drm_vma_offset_file`, `struct drm_vma_offset_node`, and `struct drm_vma_offset_manager`. APIs include manager init/destroy, locked lookup and exact lookup, add/remove, allow/allow-once/revoke/is-allowed, lookup lock/unlock, node reset/start/size/offset-address/unmap, and `drm_vma_node_verify_access`.

## Control flow
Drivers initialize a manager, reset a node embedded in a buffer object, add it with a page count to receive a fake offset, expose `drm_vma_node_offset_addr()` to userspace, and look up the node during mmap while holding the lookup read lock. Access control grants or revokes per-`drm_file` permission. Unmap invalidates existing userspace mappings for an object.

## State and persistence
Runtime state is the `drm_mm` fake address space, manager rwlock, per-node rb-tree of allowed files, per-node lock, and driver-private pointer. It persists only for object/manager lifetime.

## Dependencies and integration points
It depends on `drm_mm`, Linux mm/address_space APIs, rb-trees, rwlocks, `drm_file`, and buffer object mmap paths. TTM can use `drm_vma_node_verify_access` as a verify callback.

## Risks and test signals
Risks include fake offset overflow on 32-bit, lookup lock misuse in atomic context, forgetting node reset, removing nodes while unmapping concurrently, access-control leaks across DRM files, and allow-once semantics mishandled. Test signals include mmap of GEM/TTM buffers, unauthorized mmap denial, revoke after handle close, unmap on object eviction/free, exact versus range lookup, 32-bit builds, and concurrent lookup/remove stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_vma_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_writeback.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_writeback.h

## Purpose
`drm_writeback.h` declares the DRM writeback connector abstraction, which lets a display pipeline write composed output into a framebuffer and signal completion with a fence.

## Important APIs, types, and functions
`struct drm_writeback_connector` embeds a connector, an internal encoder for the standard init path, pixel-format blob pointer, job queue lock/list, fence context/lock/seqno, and timeline name. `struct drm_writeback_job` stores connector backpointer, prepared flag, cleanup work, queue link, destination framebuffer, output fence, and driver-private data. APIs include `drm_connector_to_writeback`, `drm_writeback_connector_init`, `drm_writeback_connector_init_with_encoder`, `drmm_writeback_connector_init`, `drm_writeback_set_fb`, `drm_writeback_prepare_job`, `drm_writeback_queue_job`, `drm_writeback_cleanup_job`, `drm_writeback_signal_completion`, and `drm_writeback_get_out_fence`.

## Control flow
Drivers initialize a writeback connector with supported pixel formats and CRTC mask. Atomic connector state sets the target framebuffer, prepares a job to hold references and create an out fence, queues it for hardware, and later signals completion status. Cleanup may defer dropping framebuffer references to a workqueue.

## State and persistence
Runtime state is connector/encoder registration, pixel-format blob, queued jobs, fence timeline counters, locks, framebuffer references, and output fences. Jobs are transient per writeback commit.

## Dependencies and integration points
It depends on DRM connectors, encoders, connector state, framebuffers, dma-fence, and workqueues. It integrates with atomic KMS writeback properties and userspace that captures display output.

## Risks and test signals
Risks include job queue ordering mistakes, failing to signal out fences on error, framebuffer reference leaks, encoder ownership confusion between init variants, pixel-format blob mismatch, and completion after connector teardown. Test signals include writeback connector init variants, atomic writeback commits, unsupported format rejection, out-fence signaling success/error, cleanup work execution, queued job ordering, and driver unload with pending jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_writeback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/gpu_scheduler.h -->
# sources/distributed-fs/ceph-client/include/drm/gpu_scheduler.h

## Purpose
`gpu_scheduler.h` declares the DRM GPU scheduler framework used by drivers to queue jobs from entities, resolve dma-fence dependencies, submit work to hardware rings, track completion fences, and recover from timeouts.

## Important APIs, types, and functions
Key types are `enum drm_sched_priority`, `struct drm_sched_entity`, `struct drm_sched_rq`, `struct drm_sched_fence`, `struct drm_sched_job`, `enum drm_gpu_sched_stat`, `struct drm_sched_backend_ops`, `struct drm_gpu_scheduler`, `struct drm_sched_init_args`, and pending-job iterator helpers. Backend ops are `prepare_job`, `run_job`, `timedout_job`, `free_job`, and `cancel_job`. Scheduler APIs include `drm_sched_init/fini`, timeout suspend/resume/queue, workqueue stop/start, scheduler stop/start/resubmit/fault/is_stopped, and `drm_sched_pick_best`. Job APIs include init/arm/push, dependency additions from fences/syncobjs/reservations/GEM objects, cleanup, karma, and signaled checks. Entity APIs include init/flush/fini/destroy, priority change, error query, and scheduler-list modification.

## Control flow
Drivers initialize one scheduler per hardware ring or queue, initialize entities for clients, initialize jobs with credits and owner/client ID, add explicit and implicit dependencies, arm scheduler fences, and push jobs to entity queues. The scheduler picks runnable entities by priority/policy, waits for dependencies, calls `prepare_job` until dependencies are clear, submits through `run_job`, links parent hardware fences to scheduled/finished fences, and calls `free_job` after completion. Timeout work invokes driver recovery through `timedout_job`; stopped schedulers can be inspected with the pending-job iterator.

## State and persistence
Runtime state includes entity queues, runqueue lists/rb-trees, scheduler fence contexts and deadlines, dependency xarrays, pending/done job lists, workqueues, timeout work, credit counters, hang karma, ready/stopped flags, client IDs, and guilty tracking. It is all in-memory scheduling state and is destroyed by entity/scheduler teardown.

## Dependencies and integration points
The header depends on dma-fence, dma-fence-chain via dependencies, xarray, completions, workqueues, reservation objects, GEM objects, DRM files/syncobjs, and the single-producer/single-consumer queue helper. It is a core integration point for GPU command submission drivers.

## Risks and test signals
Risks include unclear entity locking noted by FIXME comments, scheduler-list modification races, incorrect fence reference ownership from `run_job`, dependency cycles or missed implicit dependencies, credit accounting deadlocks, timeout recovery that violates dma-fence rules, resubmission after reset, job cancellation without signaling fences, and use-after-free during entity flush/fini. Test signals include priority scheduling, dependency ordering, syncobj and reservation dependencies, timeout/reset recovery, stop/start/resubmit paths, scheduler fini with queued jobs, pending iterator lock assertions, credit-limit saturation, fence deadline propagation, and multi-scheduler load balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/gpu_scheduler.h -->
