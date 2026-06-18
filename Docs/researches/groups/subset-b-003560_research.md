# Research: subset-b-003560

Grouped research report for DRM core/client/color helper files. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_bridge.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_bridge.c

## Purpose
`drm_bridge.c` implements the DRM bridge core: registration, dynamic lifetime, encoder-chain attachment, atomic bridge private state, bridge-chain modeset sequencing, bus-format negotiation, connector-facing helper calls, OF lookup, HPD callbacks, unplug protection, and debugfs inspection. A bridge models non-userspace-visible display hardware between an encoder and a sink or another bridge. The file is central to DRM display pipeline composition, especially for SoC panels, external HDMI/DP converters, and MIPI DSI host/peripheral chains.

## Important APIs, Types, And Functions
- Global state: `bridge_lock`, `bridge_list`, and `bridge_lingering_list` track registered and removed-but-still-referenced bridges. `drm_bridge_unplug_srcu` protects critical sections during physical unplug.
- Lifetime APIs: `drm_bridge_get()`, `drm_bridge_put()`, `drm_bridge_clear_and_put()`, `__devm_drm_bridge_alloc()`, `drm_bridge_add()`, `devm_drm_bridge_add()`, `drm_bridge_remove()`, `devm_drm_put_bridge()`.
- Unplug APIs: `drm_bridge_enter()`, `drm_bridge_exit()`, and `drm_bridge_unplug()` let callers reject new device-resource access once a bridge has been unplugged and wait for existing SRCU readers before removing it.
- Chain APIs: `drm_bridge_attach()` links a bridge into an encoder chain or after a previous bridge; `drm_bridge_detach()` removes it. `drm_bridge_chain_mode_valid()`, `drm_bridge_chain_mode_set()`, `drm_atomic_bridge_chain_disable()`, `drm_atomic_bridge_chain_post_disable()`, `drm_atomic_bridge_chain_pre_enable()`, `drm_atomic_bridge_chain_enable()`, and `drm_atomic_bridge_chain_check()` fan out bridge ops in the required order.
- Atomic private-state glue: `drm_bridge_atomic_create_priv_state()`, `drm_bridge_atomic_duplicate_priv_state()`, `drm_bridge_atomic_destroy_priv_state()`, and `drm_bridge_priv_state_funcs` wrap bridge `atomic_reset`, duplicate, and destroy callbacks in DRM private-object state.
- Bus negotiation: `drm_atomic_bridge_chain_select_bus_fmts()`, `select_bus_fmt_recursive()`, and `drm_atomic_bridge_propagate_bus_flags()` choose compatible input/output media-bus formats from the sink side backward toward the encoder and propagate bus flags.
- Connector-facing APIs: `drm_bridge_detect()`, `drm_bridge_get_modes()`, `drm_bridge_edid_read()`, `drm_bridge_hpd_enable()`, `drm_bridge_hpd_disable()`, and `drm_bridge_hpd_notify()` delegate connector behavior to bridges when `bridge->ops` advertises support.
- Lookup/debug APIs: `of_drm_find_and_get_bridge()`, deprecated `of_drm_find_bridge()`, `drm_bridge_debugfs_params()`, and `drm_bridge_debugfs_encoder_params()`.

## Control Flow
Registration starts with managed allocation through `__devm_drm_bridge_alloc()`, which embeds `struct drm_bridge` inside a driver container, initializes lists/refcount/function table, and registers a devm put action. `drm_bridge_add()` takes an extra reference, initializes HPD locking, sets HDMI YCbCr 4:2:0 allowance from supported formats, and appends the bridge to the global list. Removal moves the bridge to the lingering list, destroys the HPD mutex, and drops the registration reference; final freeing occurs only when the kref reaches zero.

Attachment validates the encoder/bridge pair, takes a bridge reference, checks previous-chain consistency, fills `bridge->dev` and `bridge->encoder`, splices `chain_node` into the encoder bridge chain, calls the optional driver attach callback, and initializes an atomic private object for atomic bridges. Error unwind removes the chain node, clears device/encoder fields, logs non-defer failures, and drops the reference.

Modeset operations walk the encoder chain with direction chosen by the semantic phase. Mode validation and mode set run encoder-to-sink. Disable runs sink-to-encoder before encoder disable. Enable runs encoder-to-sink after encoder enable. `pre_enable_prev_first` changes pre-enable and post-disable ordering for DSI-style dependencies where an upstream host must be powered before a downstream peripheral. The code groups adjacent bridges that requested this special order and skips already-called bridges to avoid duplicate callbacks.

Atomic checking first negotiates bus formats by asking the last bridge for possible output formats or falling back to connector display-info/fixed format. For each candidate output format, recursion asks each previous bridge for acceptable input formats until a full chain is found. It then walks the chain backward, propagating bus flags from connector or next-bridge state and invoking `atomic_check()` or legacy `mode_fixup()`.

## State And Persistence
State is in-memory kernel state only. Persistent objects include global bridge lists, bridge refcounts, encoder-chain links, optional bridge private atomic state, HPD callback/data fields, and the `unplugged` flag. The lingering list preserves removed bridges for debug visibility and list integrity until final kref release. There is no disk persistence.

## Dependencies And Integration Points
This file integrates with DRM encoders, connectors, atomic state, OF device-tree lookup, debugfs, SRCU, kref, Linux device-managed actions, EDID helpers, media-bus format definitions, and DRM bridge/panel drivers. Display drivers consume it through bridge attach and chain helper calls; bridge drivers implement `struct drm_bridge_funcs`; bridge connector helpers and KMS hotplug paths consume the connector-facing functions.

## Risks And Edge Cases
The highest-risk areas are bridge lifetime and chain ordering. Deprecated `of_drm_find_bridge()` intentionally returns an unrefcounted pointer and is unsafe for dynamic bridge lifetime. Bus-format negotiation depends on drivers returning allocated arrays, valid counts, and `-ENOTSUPP` correctly. `pre_enable_prev_first` logic is subtle and can regress DSI power sequencing. HPD callbacks require strict enable/disable pairing; duplicate enable is warned. Removal destroys `hpd_mutex`, so callers must not use HPD helpers after unregister. `drm_bridge_unplug()` relies on callers actually wrapping resource access in `drm_bridge_enter()/exit()`.

## Test Signals
Useful signals include bridge attach/detach tests with multi-bridge chains, DSI pre-enable/post-disable order tests, atomic-check tests covering mixed bus-format support and `MEDIA_BUS_FMT_FIXED` fallback, bridge lifetime/refcount tests for add/remove/lingering/unplug, HPD callback enable/disable/notify tests, OF lookup reference-balance tests, and debugfs smoke tests for registered and lingering bridges. Runtime signals are DRM error logs on attach failure, warnings for missing `drm_bridge_add()`, invalid atomic state, duplicate HPD enable, and debugfs bridge lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_bridge_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_bridge_helper.c

## Purpose
`drm_bridge_helper.c` provides a small helper for bridge drivers that need to reset the active CRTC pipeline feeding a bridge. It is a bridge-specific wrapper around the atomic reset helper.

## Important APIs, Types, And Functions
- `drm_bridge_helper_reset_crtc(struct drm_bridge *bridge, struct drm_modeset_acquire_ctx *ctx)` is the only exported function.
- It uses `bridge->encoder`, the encoder's `drm_device`, `drm_atomic_get_connector_for_encoder()`, `connector->state->crtc`, and `drm_atomic_helper_reset_crtc()`.

## Control Flow
The helper locks `dev->mode_config.connection_mutex` with the caller-provided acquire context, finds the connector currently associated with the bridge encoder, validates that the connector has state, extracts the active CRTC, and calls `drm_atomic_helper_reset_crtc()`. It always unlocks the connection mutex before returning. `-EDEADLK` is propagated so the caller can restart the wider atomic sequence.

## State And Persistence
The helper does not own persistent state. It temporarily holds `connection_mutex` and may trigger atomic helper behavior that power-cycles or resets state for the CRTC pipeline between CRTC and connector.

## Dependencies And Integration Points
It integrates with DRM bridge, atomic connector lookup, modeset locks, and atomic helper reset code. Callers are bridge or display pipeline code that need to recover or reinitialize the upstream CRTC path.

## Risks And Edge Cases
The function assumes `bridge->encoder` is valid and attached. If no connector can be found, the atomic connector lookup error is returned. A connector without state is treated as `-EINVAL`. Deadlock handling is delegated to the caller via `-EDEADLK`; callers that do not retry correctly can fail otherwise valid resets.

## Test Signals
Tests should cover attached bridge reset, missing connector, connector without state, lock contention returning `-EDEADLK`, and propagation of `drm_atomic_helper_reset_crtc()` errors. Runtime evidence is limited to return codes because the file does not log.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_bridge_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_buddy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_buddy.c

## Purpose
`drm_buddy.c` contains DRM-specific print helpers for the generic GPU buddy allocator. It does not implement allocation; it formats allocator blocks and free-list state for diagnostics.

## Important APIs, Types, And Functions
- `drm_buddy_block_print(struct gpu_buddy *mm, struct gpu_buddy_block *block, struct drm_printer *p)` prints a block's start, end, and size using `gpu_buddy_block_offset()` and `gpu_buddy_block_size()`.
- `drm_buddy_print(struct gpu_buddy *mm, struct drm_printer *p)` prints allocator chunk size, total size, available size, clear-free size, and per-order free block counts/sizes.
- It uses `for_each_free_tree()`, `rbtree_postorder_for_each_entry_safe()`, and `gpu_buddy_block_is_free()` over `mm->free_trees`.

## Control Flow
`drm_buddy_print()` emits a header line derived from `struct gpu_buddy`, then iterates orders from `max_order` down to zero. For each order, it walks every free-tree variant, counts free blocks, asserts each visited block is marked free, calculates aggregate free bytes for that order, and prints the amount in KiB or MiB.

## State And Persistence
The file reads allocator state but does not mutate allocator data. Output is transient through `struct drm_printer`, commonly debugfs, logs, or seq files.

## Dependencies And Integration Points
It depends on Linux `gpu_buddy`, DRM printer APIs, RB-tree iteration, and size constants. GPU memory managers call these helpers when exposing allocator diagnostics.

## Risks And Edge Cases
`BUG_ON(!gpu_buddy_block_is_free(block))` makes corruption visible but can crash the kernel in diagnostic paths. Callers must ensure the buddy allocator is locked or otherwise stable during printing; this file does not take allocator locks. Very large allocator sizes are printed with `u64` formatting.

## Test Signals
Signals include debugfs or log output matching known allocator states, per-order count correctness, and KUnit-style tests that create controlled buddy layouts. Corruption detection is visible through the `BUG_ON`, so production tests should avoid intentionally triggering it outside fault-injection environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_buddy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_cache.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_cache.c

## Purpose
`drm_cache.c` provides cache flushing, DMA bounce-buffer decision support, and write-combined memory copy helpers for DRM drivers. It hides architecture-specific details behind exported DRM APIs.

## Important APIs, Types, And Functions
- Cache flush APIs: `drm_clflush_pages()`, `drm_clflush_sg()`, and `drm_clflush_virt_range()` flush data cache lines for pages, scatter-gather tables, or virtual ranges.
- DMA helper: `drm_need_swiotlb(int dma_bits)` decides whether a driver should use swiotlb/coherent allocation due to Xen PV, memory encryption, or physical memory above the DMA mask.
- Copy APIs: `drm_memcpy_from_wc()` copies from sources that may be write-combined; `drm_memcpy_init_early()` enables the x86 static key for `movntdqa` when SSE4.1 is available and not running under a hypervisor.
- Internal helpers include x86 `drm_clflush_page()`, `drm_cache_flush_clflush()`, `memcpy_fallback()`, `__memcpy_ntdqa()`, and `__drm_memcpy_from_wc()`.

## Control Flow
On x86, flush helpers prefer CLFLUSH when supported, wrapping flush loops in memory barriers because `clflushopt` is unordered; otherwise they fall back to `wbinvd_on_all_cpus()`. On PowerPC, page flushing maps each page atomically and calls `flush_dcache_range()`. Unsupported architectures warn once.

`drm_need_swiotlb()` returns true for Xen paravirtual domains and memory encryption, then scans the top-level `iomem_resource` children to see whether installed memory exceeds `1 << dma_bits`.

`drm_memcpy_from_wc()` first warns and falls back if called in interrupt context. On x86, when `has_movntdqa` is enabled, it uses non-temporal SSE loads for aligned normal or I/O mappings; misaligned copies fall back to ordinary `memcpy`. `memcpy_fallback()` handles all combinations of system memory and I/O memory, using a small stack bounce buffer for I/O-to-I/O copies.

## State And Persistence
The file has one architecture-dependent static branch, `has_movntdqa`, initialized early and then used for fast-path selection. All other behavior is transient over pages, sg tables, iosys maps, and CPU cache state. There is no durable persistence.

## Dependencies And Integration Points
It integrates with Linux highmem mapping, scatter-gather iteration, `iosys_map`, Xen detection, confidential-computing memory-encryption attributes, x86 CPU feature detection, FPU sections, and DRM buffer/object code that needs explicit cache management.

## Risks And Edge Cases
Cache flushing is architecture-sensitive and ordering-sensitive; missing barriers can expose stale data to devices. The x86 optimized copy requires non-interrupt context because it enters an FPU section. The fallback I/O-to-I/O tail copies `MEMCPY_BOUNCE_SIZE` from source even when `len` is smaller, which relies on safe accessible ranges around the final chunk and is worth scrutiny. `1 << dma_bits` must be considered carefully for large or boundary `dma_bits` values. Unsupported architectures only warn, so drivers using these APIs need architecture coverage.

## Test Signals
Signals include architecture build coverage for x86, PowerPC, and fallback paths; boot-time verification that `drm_memcpy_init_early()` enables the static key only when expected; DMA-mask tests under memory encryption/Xen; copy tests for system, I/O, mixed, aligned, and misaligned maps; and device-visible cache coherency tests around framebuffer or GEM updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_client.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_client.c

## Purpose
`drm_client.c` implements common support for in-kernel DRM clients such as fbdev emulation and bootsplash. It initializes internal DRM files, registers clients with modeset state, and manages simple GEM-backed client framebuffers and mappings.

## Important APIs, Types, And Functions
- Client lifecycle: `drm_client_init()`, `drm_client_register()`, and `drm_client_release()`.
- Internal file handling: `drm_client_open()` allocates a `drm_file` on the primary node and links it into `dev->filelist_internal`; `drm_client_close()` removes and frees it.
- Buffer lifecycle: `drm_client_buffer_create_dumb()`, `drm_client_buffer_create()`, and `drm_client_buffer_delete()`.
- Mapping APIs: `drm_client_buffer_vmap_local()`, `drm_client_buffer_vunmap_local()`, `drm_client_buffer_vmap()`, and `drm_client_buffer_vunmap()`.
- Update API: `drm_client_buffer_flush()` invokes framebuffer `dirty` callbacks for a full buffer or a damage rectangle.

## Control Flow
`drm_client_init()` validates modeset and dumb-buffer support, stores client metadata, creates modeset storage through `drm_client_modeset_create()`, opens an internal DRM file, and takes a device reference. Registration appends the client to `dev->clientlist` under `clientlist_mutex` and immediately invokes its hotplug callback while still under the list lock so initial display setup cannot race with a concurrent hotplug.

Buffer creation starts by creating or receiving a dumb-buffer handle, looking up the GEM object in the client file, adding a framebuffer with `drm_mode_addfb2()`, looking up the framebuffer, storing the client name in `fb->comm`, and keeping GEM/framebuffer references. Dumb-buffer creation destroys the userspace-style handle after framebuffer creation to avoid circular handle lifetime while retaining object references. Deletion unmaps, removes the FB, drops GEM, and frees the wrapper.

Mapping local mode takes the GEM lock, calls `drm_gem_vmap_locked()`, returns a copy of the `iosys_map`, and requires a matching local unmap to release both mapping and lock. Long-term mapping uses unlocked `drm_gem_vmap()`/`drm_gem_vunmap()`.

## State And Persistence
Client state is in `struct drm_client_dev`: device pointer, name, function table, internal `drm_file`, modesets, and list node. Buffer state is in `struct drm_client_buffer`: client, GEM object, framebuffer, and current mapping. All state is in-memory and tied to DRM device lifetime.

## Dependencies And Integration Points
This code integrates with DRM device/file lifetime, client event dispatch, GEM objects, dumb-buffer ioctls, framebuffer helpers, format information, modeset helpers, and framebuffer dirty callbacks. Fbdev emulation is the primary consumer.

## Risks And Edge Cases
The initial hotplug callback runs while `clientlist_mutex` is held, so callbacks must avoid lock inversions with client-list operations. Mapping APIs are not refcounted; mismatched map/unmap calls can leak mappings or unlock incorrectly. `drm_client_buffer_delete()` assumes a valid `buffer->fb` and `obj[0]`. Error unwinds around framebuffer creation must maintain GEM and FB references exactly. Clients cannot generally self-release; release is driven by device unregister or the unregister callback.

## Test Signals
Useful tests include client init rejection without modeset/dumb-create support, register-triggered initial hotplug, unregister/release reference balance, dumb-buffer create/delete handle lifetime, GEM vmap/vunmap pairing, framebuffer dirty flush with and without damage rectangles, and failure injection for GEM lookup, addfb, framebuffer lookup, and vmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_client_event.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_client_event.c

## Purpose
`drm_client_event.c` dispatches device-level events to in-kernel DRM clients: unregister, hotplug, restore, suspend, resume, and debugfs listing. It coordinates the client callback model around `dev->clientlist`.

## Important APIs, Types, And Functions
- `drm_client_dev_unregister()` removes all clients and calls `client->funcs->unregister()` or `drm_client_release()`.
- `drm_client_dev_hotplug()` iterates clients and sends hotplug callbacks through `drm_client_hotplug()`.
- `drm_client_dev_restore()` asks clients to restore output state, stopping at the first callback that returns zero.
- `drm_client_dev_suspend()` and `drm_client_dev_resume()` drive suspend/resume callbacks and pending hotplug replay.
- Debugfs support adds `internal_clients` through `drm_client_debugfs_init()` when `CONFIG_DEBUG_FS` is enabled.

## Control Flow
Hotplug dispatch first rejects non-modeset devices and devices with no connectors. Under `clientlist_mutex`, each client is skipped if it has no hotplug function, has previously failed hotplug, or is suspended. Suspended clients record `hotplug_pending` instead of running callbacks. On resume, the client callback runs, `suspended` is cleared, and any pending hotplug is replayed.

Unregister walks the list with the safe iterator because callbacks consume and free clients. Restore walks clients in registration order and lets the first successful restore take ownership of restoring the console/display state.

## State And Persistence
State is per-client and in-memory: `suspended`, `hotplug_pending`, and `hotplug_failed` gate future callback dispatch. The device client list is modified during unregister. Debugfs output is transient.

## Dependencies And Integration Points
This file connects `drm_dev_unregister()`, KMS helper hotplug events, PM suspend/resume paths, fbdev/other internal clients, and debugfs. It depends on `DRIVER_MODESET` checks and `clientlist_mutex` for serialization.

## Risks And Edge Cases
Once `hotplug_failed` is set, future hotplug events are suppressed for that client, so transient failures can leave a client inactive until another recovery path resets state. Callbacks run under `clientlist_mutex`, so callback lock ordering matters. Suspend marks a client suspended even if its suspend callback fails. Restore stops on the first success, making client ordering significant.

## Test Signals
Tests should exercise hotplug success/failure, hotplug while suspended and replay on resume, unregister with callbacks that free clients, restore first-success semantics, no-connector hotplug suppression, and debugfs output listing registered internal clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_client_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_client_modeset.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_client_modeset.c

## Purpose
`drm_client_modeset.c` builds and commits initial/display-recovery modeset configurations for in-kernel DRM clients. It chooses enabled connectors, modes, CRTCs, offsets for tiled displays, rotations, and then commits through atomic or legacy modeset paths. This is the core modeset engine behind fbdev-like clients.

## Important APIs, Types, And Functions
- Allocation/lifetime: `drm_client_modeset_create()` allocates one `drm_mode_set` per CRTC plus connector arrays; `drm_client_modeset_free()` releases modes, connectors, arrays, and mutex state.
- Mode selection helpers: command-line, preferred, first, tiled, and fallback mode pickers; `drm_client_connectors_enabled()`; `drm_client_target_cloned()`; `drm_client_target_preferred()`; `drm_client_firmware_config()`; `drm_client_pick_crtcs()`.
- Public probe/commit APIs: `drm_client_modeset_probe()`, `drm_client_modeset_check()`, `drm_client_modeset_commit_locked()`, `drm_client_modeset_commit()`, `drm_client_modeset_dpms()`, and `drm_client_modeset_wait_for_vblank()`.
- Rotation: `drm_client_rotation()` combines panel orientation and command-line rotation/reflection and checks primary-plane support.
- Commit implementations: `drm_client_modeset_commit_atomic()` and `drm_client_modeset_commit_legacy()`.

## Control Flow
Creation builds a sentinel-terminated modeset array and records every CRTC. Cloning is only allowed for a single-CRTC device and reserves up to `DRM_CLIENT_MAX_CLONED_CONNECTORS` connector slots.

`drm_client_modeset_probe()` enumerates connectors with references, allocates temporary arrays for modes/CRTCs/offsets/enabled flags, fills connector modes under `mode_config.mutex`, determines enabled connectors with strict connected status and fallback non-disconnected status, and tries firmware configuration first for atomic drivers. Firmware configuration uses current connector state/CRTCs if it can light all expected outputs without unsupported cloning; otherwise it falls back. The fallback path tries command-line cloning on single-CRTC devices, then preferred/first/tiled selection, then recursively scores CRTC assignments. The chosen result replaces the client's stored modesets under `modeset_mutex`.

Atomic commit allocates an atomic state with an acquire context, obtains all plane states, resets rotation, disables non-primary planes, applies per-modeset primary rotation when supported, calls `__drm_atomic_helper_set_config()`, optionally forces CRTC inactive for DPMS off, and runs check-only or commit. It handles `-EDEADLK` by clearing state, backing off locks, and retrying. Legacy commit locks all modesets, disables non-primary planes, resets rotation properties, clears cursors, and calls `drm_mode_set_config_internal()`.

## State And Persistence
Persistent client state is the `client->modesets` array, each `struct drm_mode_set`'s duplicated mode, connector references, CRTC, fb, x/y offset, and connector count. `modeset_mutex` serializes access. Temporary probe arrays are destroyed after use. No disk persistence exists.

## Dependencies And Integration Points
The file integrates with connector mode enumeration, EDID/cmdline mode data, tiled monitor metadata, CRTC/encoder possible masks, atomic helper state, DRM master internal acquire/release, vblank APIs, DPMS properties, plane rotation properties, and legacy CRTC cursor/config functions.

## Risks And Edge Cases
The CRTC picker is recursive and can be expensive with many connectors, though client connector counts are normally small. Clone support is deliberately narrow and can reject firmware layouts on multi-CRTC hardware. Tiled-display selection has several fallback cases when not all tiles are present or tiled modes exceed fb size. Atomic commit touches all planes and disables non-primary planes, so client commits can disturb other internal plane state if master exclusion is wrong. Rotation support only accepts 0 and 180 degrees despite computing 90/270 from panel orientation. Correct `-EDEADLK` retry behavior is essential.

## Test Signals
This file includes KUnit coverage when `CONFIG_DRM_KUNIT_TEST` includes `tests/drm_client_modeset_test.c`. Additional signals include connector/mode selection tests for command-line, preferred, first, tiled, clone, and firmware paths; CRTC assignment scoring tests; atomic check-only and commit tests with `-EDEADLK` injection; legacy commit cursor/plane cleanup tests; DPMS on/off behavior; vblank wait returning `-EBUSY` when another master is present; and rotation mask validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_client_modeset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_client_sysrq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_client_sysrq.c

## Purpose
`drm_client_sysrq.c` wires DRM client restore into Magic SysRq. When enabled, SysRq `v` schedules a work item that asks registered DRM devices to force-restore their in-kernel client display state, primarily framebuffer console recovery.

## Important APIs, Types, And Functions
- Global state under `CONFIG_MAGIC_SYSRQ`: `drm_client_sysrq_dev_list`, `drm_client_sysrq_dev_lock`, and `drm_client_sysrq_restore_work`.
- `drm_client_sysrq_register(struct drm_device *dev)` adds a device and registers SysRq key `v` when the first device arrives.
- `drm_client_sysrq_unregister(struct drm_device *dev)` removes a device and unregisters key `v` when the list becomes empty.
- `drm_client_sysrq_restore_handler()` schedules work; `drm_client_sysrq_restore_work_fn()` iterates devices and calls `drm_client_dev_restore(dev, true)` unless switch power is off.

## Control Flow
The SysRq handler runs in constrained context and only schedules work. The work function takes the global mutex, iterates the device list, skips devices in `DRM_SWITCH_POWER_OFF`, and invokes forced restore. Registration and unregistration hold the same mutex and manage key registration according to list emptiness.

## State And Persistence
State is a global in-memory list of devices currently participating in SysRq restore and the registered sysrq key operation. There is no persistence beyond runtime device registration.

## Dependencies And Integration Points
It depends on `CONFIG_MAGIC_SYSRQ`, Linux sysrq registration, workqueues, DRM device list node `client_sysrq_list`, `drm_client_dev_restore()`, and DRM switch power state.

## Risks And Edge Cases
Device list lifetime must be balanced with register/unregister; unregister warns if the list node is empty. The work function holds the global sysrq device mutex while calling restore, so restore paths must not try to acquire the same lock. Restore is intentionally best effort and ignores errors. Devices powered off are skipped to avoid unsafe restore attempts.

## Test Signals
Signals include key registration on first device, unregistration on last device, scheduling work from the handler, skipping powered-off devices, forced restore callback invocation, and warning behavior for double unregister or empty list nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_client_sysrq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_color_mgmt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_color_mgmt.c

## Purpose
`drm_color_mgmt.c` implements DRM CRTC and plane color-management helpers: CRTC degamma/CTM/gamma properties, legacy gamma ioctls, plane color encoding/range properties, LUT validation, and helper routines for programming or filling gamma/palette tables of common bit depths.

## Important APIs, Types, And Functions
- CRTC color setup: `drm_crtc_enable_color_mgmt()` attaches `DEGAMMA_LUT`, `DEGAMMA_LUT_SIZE`, `CTM`, `GAMMA_LUT`, and `GAMMA_LUT_SIZE` properties as requested.
- Conversion: `drm_color_ctm_s31_32_to_qm_n()` converts sign-magnitude S31.32 CTM values to signed Qm.n with clamping.
- Legacy gamma: `drm_mode_crtc_set_gamma_size()`, `drm_mode_gamma_set_ioctl()`, `drm_mode_gamma_get_ioctl()`, and internal `drm_crtc_legacy_gamma_set()`.
- Plane color properties: `drm_plane_create_color_properties()` plus KUnit-visible name helpers for encodings/ranges.
- Validation: `drm_color_lut_check()` and `drm_color_lut32_check()` enforce equal-channel and non-decreasing constraints.
- Programming helpers: `drm_crtc_load_gamma_888()`, `drm_crtc_load_gamma_565_from_888()`, `drm_crtc_load_gamma_555_from_888()`, default gamma fill helpers for 888/565/555, and palette load/fill helpers for C8/RGB332.

## Control Flow
Drivers opt into atomic color management by enabling CRTC properties with nonzero LUT sizes and optional CTM. Legacy gamma setup allocates `crtc->gamma_store` as three contiguous `u16` tables and initializes a linear ramp. Gamma set ioctl validates modeset support, finds the CRTC, validates legacy gamma support and size, copies user red/green/blue tables into `gamma_store` under modeset locks, then either calls the driver's legacy `gamma_set` hook or builds a DRM property blob and atomic state that maps legacy values onto `GAMMA_LUT` or `DEGAMMA_LUT`, clearing CTM. Gamma get ioctl copies the current store back to userspace under the CRTC mutex.

Plane color properties validate supported/default bitmasks, build enum lists for COLOR_ENCODING and COLOR_RANGE, attach properties, and initialize existing plane state defaults. LUT checkers iterate blob entries and return `-EINVAL` on channel mismatch or decreasing values when requested. Programming helpers translate 8-bit or LUT data into 16-bit channel values and call driver-supplied setters.

## State And Persistence
Persistent runtime state includes attached DRM properties, `crtc->gamma_size`, `crtc->gamma_store`, CRTC state blobs (`degamma_lut`, `ctm`, `gamma_lut`), and plane state defaults for color encoding/range. Property blobs are refcounted by DRM core. No disk persistence exists.

## Dependencies And Integration Points
The file integrates with DRM property objects/blobs, atomic state/commit, modeset locks, user-copy APIs, CRTC/plane initialization, KUnit visibility, framebuffer format color paths, and driver hardware programming callbacks.

## Risks And Edge Cases
Legacy gamma bridges old ioctls to atomic properties and must maintain blob reference balance and lock retry semantics through `DRM_MODESET_LOCK_ALL_BEGIN/END`. User pointers can fault, returning `-EFAULT`. `drm_color_ctm_s31_32_to_qm_n()` only warns for unsupported `m`/`n` values instead of failing. `drm_plane_create_color_properties()` can attach one property successfully and fail on the second, leaving partial initialization for caller cleanup. The `fill_gamma_555()` helper computes blue expansion using `(r >> 4)`, which is suspicious and should be checked against intended `(b >> 4)`.

## Test Signals
Signals include KUnit tests for CTM conversion, encoding/range name helpers, LUT validation, legacy gamma set/get with copy fault injection, blob reference behavior in atomic gamma mapping, property defaults on planes with existing state, and golden-value tests for gamma/palette fill/load helpers. Runtime validation also comes from userspace color-management tests in IGT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_color_mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_colorop.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_colorop.c

## Purpose
`drm_colorop.c` implements the DRM plane color pipeline object model. Colorops are DRM mode objects chained through a `NEXT` property and selected through plane color-pipeline properties by atomic userspace that advertises `DRM_CLIENT_CAP_PLANE_COLOR_PIPELINE`.

## Important APIs, Types, And Functions
- Base initialization: `drm_plane_colorop_init()` creates a `DRM_MODE_OBJECT_COLOROP`, links it into `mode_config.colorop_list`, assigns index/type/plane/funcs, and attaches common `TYPE`, optional `BYPASS`, and `NEXT` properties.
- Cleanup: `drm_colorop_cleanup()`, `drm_colorop_destroy()`, and `drm_colorop_pipeline_destroy()`.
- Colorop constructors: `drm_plane_colorop_curve_1d_init()`, `drm_plane_colorop_curve_1d_lut_init()`, `drm_plane_colorop_ctm_3x4_init()`, `drm_plane_colorop_mult_init()`, and `drm_plane_colorop_3dlut_init()`.
- State helpers: `drm_atomic_helper_colorop_duplicate_state()`, `drm_colorop_atomic_destroy_state()`, `drm_colorop_reset()`, and internal state reset/destroy helpers.
- Name helpers: `drm_get_colorop_type_name()`, `drm_get_colorop_curve_1d_type_name()`, `drm_get_colorop_lut1d_interpolation_name()`, and `drm_get_colorop_lut3d_interpolation_name()`.
- Chain helper: `drm_colorop_set_next_property()` updates both the immutable `NEXT` property value and `colorop->next`.

## Control Flow
Each public constructor calls the base initializer with a specific `enum drm_colorop_type`, then adds type-specific properties. 1D curve colorops validate the supported transfer-function bitmask, create a `CURVE_1D_TYPE` enum from supported entries, attach the first supported value as default, and reset state. 1D and 3D LUT colorops attach immutable atomic `SIZE`, interpolation enum, and blob `DATA` property. CTM 3x4 attaches `DATA`. Multiplier attaches an atomic range `MULTIPLIER`.

State duplication copies the current state and takes a reference to the `DATA` blob if present. State destruction drops that blob. Reset frees existing state, allocates a zeroed state, sets `colorop`, defaults `bypass` to true, and copies default `CURVE_1D_TYPE` when present.

Pipeline destruction walks the global colorop list safely and calls each colorop's driver-provided destroy function. `drm_colorop_set_next_property()` is used during pipeline construction to expose object chaining to userspace and retain the in-kernel next pointer.

## State And Persistence
Persistent runtime state includes `mode_config.colorop_list`, `mode_config.num_colorop`, each colorop's DRM mode object and properties, `colorop->state`, optional refcounted data blobs in state, `next` pointers, plane association, and immutable size/interpolation metadata. All state is in-memory and atomic-modeset scoped.

## Dependencies And Integration Points
This file integrates with DRM mode objects, property creation/attachment, plane objects, atomic color pipeline uAPI, DRM colorop function tables, and driver pipeline construction/destruction. It complements older plane color properties in `drm_color_mgmt.c` by providing a richer per-plane pipeline model.

## Risks And Edge Cases
Several constructors can partially initialize a colorop and then return `-ENOMEM`; callers need cleanup paths for objects already added to `colorop_list` or properties already attached. `drm_colorop_cleanup()` assumes list membership and decrements `num_colorop`. State reset silently leaves `colorop->state` NULL on allocation failure. Pipeline destruction trusts every colorop has a valid `funcs->destroy`. The `NEXT` property is created immutable yet changed by core construction helper, so drivers should set chains only during initialization. Userspace must not mix legacy plane color properties with color pipelines once the cap is enabled.

## Test Signals
Tests should cover each constructor's property set and defaults, invalid supported transfer-function masks, cleanup after partial failures, state duplicate/destroy blob refcounts, reset defaults including bypass and curve type, chain construction via `NEXT`, global list/count maintenance, and atomic userspace behavior rejecting old color properties when color pipelines are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_colorop.c -->
