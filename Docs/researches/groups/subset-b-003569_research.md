# subset-b-003569 DRM core helper research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_prime.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_prime.c

Purpose: implements DRM PRIME dma-buf import/export helpers for GEM objects, including per-file handle caches, PRIME ioctls, generic dma-buf ops, scatter-gather conversion helpers, mmap/vmap glue, and cleanup for imported GEM objects.

Important APIs/types/functions: `struct drm_prime_member` stores weak per-file `dma_buf` to GEM handle mappings in two rbtrees. `drm_prime_add_buf_handle()`, `drm_prime_remove_buf_handle()`, `drm_prime_init_file_private()`, and `drm_prime_destroy_file_private()` manage those caches. `drm_gem_prime_fd_to_handle()`, `drm_prime_fd_to_handle_ioctl()`, `drm_gem_prime_handle_to_dmabuf()`, `drm_gem_prime_handle_to_fd()`, and `drm_prime_handle_to_fd_ioctl()` implement user-visible PRIME conversion. `drm_gem_dmabuf_export()` and `drm_gem_dmabuf_release()` define GEM export lifetime. `drm_gem_map_attach()`, `drm_gem_map_detach()`, `drm_gem_map_dma_buf()`, `drm_gem_unmap_dma_buf()`, `drm_gem_dmabuf_vmap()`, `drm_gem_dmabuf_vunmap()`, and `drm_gem_dmabuf_mmap()` are reusable `dma_buf_ops`. `drm_gem_prime_export()`, `drm_gem_prime_import_dev()`, `drm_gem_prime_import()`, and `drm_prime_gem_destroy()` are the default GEM driver implementation path.

Control flow: fd-to-handle gets a dma-buf fd, checks the file-private cache under `file_priv->prime.lock`, imports through the driver or generic helper under `dev->object_name_lock`, creates a GEM handle, and registers the dma-buf to handle mapping. Handle-to-fd allocates the fd first, looks up the GEM object, reuses existing cache/import/export dma-buf when possible, otherwise exports and registers the object, then installs the dma-buf file. Generic import self-imports locally exported GEM dma-bufs by taking a GEM reference; otherwise it attaches to the dma-buf, maps it bidirectionally, and asks the driver to build a GEM object from the sg table. Generic export wires the GEM object into `dma_buf_export_info` with shared reservation object and standard ops.

State and persistence behavior: cache state is per DRM file and protected by a mutex; cache nodes hold dma-buf references but are described as weak relative to GEM object lifetime and should be removed when GEM handles close. Exported dma-bufs hold references on both `drm_device` and `drm_gem_object` until release. Imported GEM objects persist `import_attach` and reuse the dma-buf reservation object until the driver free hook calls `drm_prime_gem_destroy()`.

Dependencies and integration points: integrates DRM GEM handle management, dma-buf core, dma-resv locking, scatterlist DMA mapping, driver `gem_prime_import`, `gem_prime_import_sg_table`, and `drm_gem_object_funcs` callbacks. It is an ioctl backend for PRIME handle/fd conversion and a helper library for GEM based DRM drivers.

Risks: ordering between `file_priv->prime.lock` and `dev->object_name_lock` is central to avoiding gem-close races. Drivers using generic import must call `drm_prime_gem_destroy()` from object free or leak/dangle dma-buf attachments. Export helpers assume coherent, permanently pinned or indefinitely pinnable backing storage. The rbtree cache keys dma-bufs by pointer value and handles by integer; duplicate insertion callers must be disciplined. Error paths around handle creation and cache insertion intentionally rely on GEM free paths for attachment cleanup.

Test signals: PRIME fd-to-handle and handle-to-fd ioctl round trips, self-import of locally exported objects, repeated import returning the same handle in one file, handle close removing cache entries, mmap/vmap/map_dma_buf paths, dma-buf attach failure without `get_sg_table`, and driver unload/import cleanup tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_prime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_print.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_print.c

Purpose: provides DRM printing infrastructure, debug category control, `drm_printer` backends for coredumps and seq_file, device-aware printk wrappers, bit/register/hex dump helpers, and dynamic-debug integration.

Important APIs/types/functions: global `__drm_debug` is the DRM debug category bitmask. Dynamic debug builds define `drm_debug_classes` and a `ddebug_class_param`. `__drm_puts_coredump()` and `__drm_printfn_coredump()` implement offset/range copying into `drm_print_iterator`. `__drm_puts_seq_file()` and `__drm_printfn_seq_file()` write to seq_file. `__drm_printfn_info()`, `__drm_printfn_dbg()`, `__drm_printfn_err()`, `__drm_printfn_line()`, `drm_puts()`, `drm_printf()`, `drm_dev_printk()`, `__drm_dev_dbg()`, and `__drm_err()` are printer and log entry points. `drm_print_bits()`, `drm_print_regset32()`, and `drm_print_hex_dump()` format common diagnostics.

Control flow: module parameter `debug` either directly controls `__drm_debug` or maps bit classes to dynamic debug. Printer callbacks receive a `drm_printer` whose `arg`, `prefix`, `origin`, and category determine the output target. Coredump printing either skips until the requested offset, copies directly when the formatted string fits, or formats into a temporary buffer and feeds the generic puts path. Debug printing first checks `__drm_debug_enabled()` before emitting.

State and persistence behavior: persistent state is the global debug bitmask and dynamic-debug class map. Coredump state is caller-supplied iterator offset/start/remain/data. Line printers mutate an embedded counter in the `drm_printer`.

Dependencies and integration points: used across DRM core and drivers through `drm_print.h` macros. Integrates with kernel printk, device logging, seq_file/debugfs, coredump capture, dynamic debug, and MMIO register dumps.

Risks: coredump formatting intentionally uses `GFP_KERNEL | __GFP_NOWARN | __GFP_NORETRY`; allocation failure silently drops that formatted fragment. `drm_print_regset32()` performs raw MMIO reads and depends on valid register mappings. Debug gating must stay aligned with enum category ordering and dynamic-debug class names.

Test signals: module parameter and dynamic-debug category toggling, coredump offset/length boundary tests, seq_file/debugfs output checks, prefix/origin formatting, bit list formatting for empty and unknown names, register dump smoke tests with safe mock mappings, and hex dump line splitting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_print.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_privacy_screen.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_privacy_screen.c

Purpose: implements the DRM privacy-screen class used by non-KMS provider drivers and KMS connector consumers to expose standard privacy-screen properties and state notifications.

Important APIs/types/functions: global lookup and device lists are guarded by `drm_privacy_screen_lookup_lock` and `drm_privacy_screen_devs_lock`. `drm_privacy_screen_lookup_add()` and `drm_privacy_screen_lookup_remove()` manage static provider lookup entries. `drm_privacy_screen_get()` resolves a consumer device/connector to a provider, and `drm_privacy_screen_put()` drops the reference. `drm_privacy_screen_set_sw_state()`, `drm_privacy_screen_get_state()`, notifier register/unregister helpers, `drm_privacy_screen_register()`, `drm_privacy_screen_unregister()`, and `drm_privacy_screen_call_notifier_chain()` are the provider/consumer API surface. Sysfs exposes read-only `sw_state` and `hw_state`.

Control flow: consumers resolve lookup entries with clock-framework-style fuzzy matching, preferring dev+connector over dev-only over connector-only. Provider registration allocates a `drm_privacy_screen`, initializes locking and notifier state, queries initial hardware state through provider ops, registers a class device, then adds it to the provider list. Software state setting stores requested state when hardware is locked or already matching; otherwise it calls provider `set_sw_state`. Unregister removes the device from lookup visibility, clears ops/data under lock, then unregisters the class device.

State and persistence behavior: lookup entries are owned by callers and must outlive list membership. Provider devices persist in the DRM class until `device_unregister()` release frees them. Each privacy screen stores `sw_state`, `hw_state`, provider ops/data, a notifier chain, and class-device sysfs state.

Dependencies and integration points: integrates `drm_privacy_screen_machine.h`, consumer and driver privacy-screen APIs, DRM class sysfs, provider drivers such as platform/x86 implementations, and connector helpers that attach/update privacy-screen connector properties.

Risks: provider lookup is static and not firmware-node based yet, so mismatched names can cause `-ENODEV` or indefinite `-EPROBE_DEFER`. Provider `get_hw_state()` is called during registration and must initialize states correctly. Notifiers are deliberately not called for `set_sw_state()`, so drivers must emit external-change notifications themselves. Clearing ops during unregister means readers must honor `-ENODEV` paths.

Test signals: provider register/unregister lifetime, lookup specificity ordering, deferred probe before provider registration, locked hardware state preserving requested software state, sysfs state reads, notifier callbacks for external changes, and connector property integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_privacy_screen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_privacy_screen_x86.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_privacy_screen_x86.c

Purpose: provides x86 architecture-specific privacy-screen lookup initialization for known laptop platform providers, currently ThinkPad ACPI and ChromeOS privacy-screen devices when configured.

Important APIs/types/functions: static `arch_lookup` is the runtime lookup copy. `struct arch_init_data` pairs a lookup entry with a detect callback. `detect_thinkpad_privacy_screen()` discovers EC method `HKEY.GSSS`; `detect_chromeos_privacy_screen()` checks ACPI device `GOOG0010`. `drm_privacy_screen_lookup_init()` registers the first detected provider and `drm_privacy_screen_lookup_exit()` removes it.

Control flow: init iterates the compile-time `arch_init_data` array, runs each detect callback, logs the first matching provider, copies its `__initconst` lookup into persistent storage, adds it to the privacy-screen core, and stops. Exit removes the lookup only if one was registered.

State and persistence behavior: only one global x86 lookup is active. The selected lookup persists in `arch_lookup` because the source table is init-only memory.

Dependencies and integration points: depends on ACPI, optional ThinkPad ACPI and ChromeOS privacy-screen configs, and `drm_privacy_screen_lookup_add/remove()` from the core privacy-screen file.

Risks: first-match behavior means only one platform provider is registered even if multiple detectors match. ACPI method names and provider device names must match provider drivers exactly. Build coverage varies with optional configs, so stubs may compile away most code.

Test signals: boot on supported ThinkPad and ChromeOS systems, ACPI-disabled path, configs with each detector enabled/disabled, lookup removal at DRM exit, and consumer deferred-probe behavior until the provider class device appears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_privacy_screen_x86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_probe_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_probe_helper.c

Purpose: implements KMS output probing helpers: connector detection, mode collection and validation, connector polling, hotplug event helpers, fixed-mode and EDID-based get_modes helpers, TV mode helpers, and DDC-based detect helpers.

Important APIs/types/functions: `drm_helper_probe_single_connector_modes()` is the central `fill_modes` implementation. `drm_helper_probe_detect()`, `drm_connector_mode_valid()`, `drm_crtc_mode_valid()`, `drm_encoder_mode_valid()`, and `drm_mode_validate_pipeline()` run detect and mode validation callbacks. Polling is controlled by `drm_kms_helper_poll_init()`, `drm_kms_helper_poll_enable()`, `drm_kms_helper_poll_disable()`, `drm_kms_helper_poll_fini()`, `drmm_kms_helper_poll_init()`, and `output_poll_execute()`. Hotplug helpers include `drm_kms_helper_hotplug_event()`, `drm_kms_helper_connector_hotplug_event()`, `drm_connector_helper_hpd_irq_event()`, and `drm_helper_hpd_irq_event()`. Convenience modes helpers include fixed, EDID, TV, and DDC functions.

Control flow: fill_modes requires `mode_config.mutex`, locks `connection_mutex` with deadlock backoff, marks old modes stale, applies forced connector state or runs detect, schedules delayed hotplug if status changes, gathers modes from driver/EDID/fallback/cmdline, validates against basic, size, flags, ycbcr420, connector, encoder, bridge, and CRTC constraints, prunes invalid modes, adds DisplayPort failsafe modes when needed, sorts modes, and logs results. Poll work scans non-forced pollable connectors, runs non-destructive detection, clamps unknown results back to old status, emits hotplug events when epochs change, and reschedules if polling remains needed.

State and persistence behavior: per-device `mode_config` stores polling flags, delayed work, delayed hotplug events, and connector mode lists. Per-connector `status`, `force`, `epoch_counter`, `polled`, EDID properties, and command-line mode data are mutated during probing.

Dependencies and integration points: integrates connector, encoder, CRTC and bridge helper vtables, EDID/DDC helpers, sysfs hotplug events, DRM client hotplug callbacks, workqueues, module parameter `poll`, modeset locking/backoff, and managed cleanup through `drmm_add_action_or_reset()`.

Risks: callers must observe locking and process-context rules around hotplug helpers. Destructive detection is avoided in poll paths, which can temporarily hide true status. Misreported helper callbacks, especially negative `get_modes()` or missing deadlock handling, degrade mode lists. Poll enable/disable ordering matters around suspend/resume and runtime PM deadlocks.

Test signals: connector fill_modes under forced on/off/detect states, EDID fallback and cmdline mode insertion, invalid mode pruning reasons, DisplayPort 640x480 fallback, HPD and polling status-change uevents, suspend/resume poll disable/enable, lockdep for modeset backoff, and fixed/TV/DDC helper unit coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_probe_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_property.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_property.c

Purpose: implements DRM modeset property creation, enumeration metadata, blob properties, userspace property/blob ioctls, blob replacement helpers, and property value validation with object/blob reference handling.

Important APIs/types/functions: property constructors include `drm_property_create()`, enum, bitmask, range, signed range, object, and bool variants. `drm_property_add_enum()` and `drm_property_destroy()` manage metadata. Ioctls include `drm_mode_getproperty_ioctl()`, `drm_mode_getblob_ioctl()`, `drm_mode_createblob_ioctl()`, and `drm_mode_destroyblob_ioctl()`. Blob APIs include `drm_property_create_blob()`, `drm_property_blob_get/put()`, `drm_property_lookup_blob()`, `drm_property_destroy_user_blobs()`, `drm_property_replace_global_blob()`, `drm_property_replace_blob()`, and `drm_property_replace_blob_from_id()`. `drm_property_change_valid_get()` and `drm_property_change_valid_put()` validate and manage referenced dynamic values.

Control flow: property creation validates flags/name, allocates value storage, registers a mode object, initializes enum list and device property list membership. User property get copies fixed values first and enum metadata second. Blob creation allocates one object plus inline data, registers a refcounted mode object with `drm_property_free_blob()` release, and links it globally; user-created blobs are additionally linked to `file_priv->blobs`. Blob destroy verifies file ownership, unlinks file membership, then drops both lookup and file references.

State and persistence behavior: properties persist in `dev->mode_config.property_list` until mode config cleanup. Blobs are refcounted mode objects in a global blob list protected by `blob_lock`; user blobs also persist per DRM file until explicit destroy or file release. Blob data is immutable after creation by contract.

Dependencies and integration points: used by legacy and atomic modeset objects, connector/CRTC/plane properties, EDID/path/color metadata blobs, user ioctls, mode object ID lookup, and `uaccess` copy paths.

Risks: property flags must contain exactly one valid type class; bad flags are rejected with warnings. User blob ownership checks prevent one file from destroying another file's blob, but global lookups still expose readable blob IDs. `drm_property_replace_global_blob()` assumes caller-side locking around the pointer being replaced. Reference-returning validation requires paired `drm_property_change_valid_put()` on failure paths.

Test signals: constructor validation for all property types, duplicate enum rejection, getproperty count-only and copy paths, create/get/destroy blob ownership, file release cleanup, blob replacement with size and element constraints, immutable property rejection, object/blob value reference leak checks, and atomic property validation fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_property.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ras.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ras.c

Purpose: implements DRM RAS node registration and Generic Netlink handlers for listing RAS nodes and reading error counters from registered DRM driver components.

Important APIs/types/functions: global `drm_ras_xa` stores `struct drm_ras_node` by allocated ID. `struct drm_ras_ctx` carries dump restart state. Netlink handlers are `drm_ras_nl_list_nodes_dumpit()`, `drm_ras_nl_get_error_counter_dumpit()`, and `drm_ras_nl_get_error_counter_doit()`. Helpers include `get_node_error_counter()`, `msg_reply_value()`, and `doit_reply_value()`. Driver-facing registration APIs are `drm_ras_node_register()` and `drm_ras_node_unregister()`.

Control flow: register validates node names, supported type, error-counter range, and callback, then allocates an xarray ID. List-nodes dump iterates from the saved restart ID and emits one generic-netlink reply per node. Error-counter dump validates node ID, walks the node's configured error ID range from restart, skips driver-returned `-ENOENT` holes, and emits ID/name/value attributes. Single-counter doit validates node and error ID attributes, allocates a reply skb, queries the counter, appends attributes, and replies.

State and persistence behavior: RAS nodes remain in the global xarray until driver unregister. Dump restart offset is stored in netlink callback context. Error counter values are live data returned by driver callbacks, not persisted by the core.

Dependencies and integration points: depends on `drm_ras.h` driver contracts, generated `drm_ras_nl.h` command declarations, xarray allocation, and Generic Netlink message construction. Drivers integrate by filling `drm_ras_node` and callback fields.

Risks: xarray access does not add per-node refcounts, so unregister must not race active netlink dumps unless higher-level lifetime rules cover nodes. `doit_reply_value()` allocates and starts a message before querying the counter; on query failure it returns without freeing/canceling the skb, which is a leak risk. Dump handlers must update restart carefully on `-EMSGSIZE` to avoid repeating or skipping entries.

Test signals: register validation failures, list dump with multiple nodes and small skb continuation, sparse error ID ranges using `-ENOENT`, single-counter query errors and success replies, unregister during/after queries under KASAN/KCSAN, and YNL userspace coverage for the drm_ras family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ras.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ras_genl_family.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ras_genl_family.c

Purpose: wraps registration and unregistration of the generated DRM RAS Generic Netlink family.

Important APIs/types/functions: static `registered` records whether `genl_register_family()` succeeded. `drm_ras_genl_family_register()` registers `drm_ras_nl_family`; `drm_ras_genl_family_unregister()` unregisters it if currently registered.

Control flow: register clears `registered`, calls Generic Netlink registration, and sets `registered` only on success. Unregister tests the flag, unregisters the family, and clears the flag, making exit callable after failed init.

State and persistence behavior: one file-local boolean persists family registration state for DRM core init/exit.

Dependencies and integration points: depends on `drm_ras_genl_family.h`, generated `drm_ras_nl_family`, and DRM driver core init/exit ordering.

Risks: no locking protects `registered`, so the functions assume single-threaded core init/exit. The generated family object must remain initialized for the life of registration.

Test signals: init success, init failure injection, exit after failed init, double-exit no-op behavior, and netlink family visibility after registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ras_genl_family.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ras_nl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ras_nl.c

Purpose: generated YNL Generic Netlink specification binding for DRM RAS commands, policies, operations, and family metadata.

Important APIs/types/functions: `drm_ras_get_error_counter_do_nl_policy` requires node ID and error ID as `NLA_U32` for do requests. `drm_ras_get_error_counter_dump_nl_policy` accepts node ID for dump requests. `drm_ras_nl_ops` binds `DRM_RAS_CMD_LIST_NODES` and `DRM_RAS_CMD_GET_ERROR_COUNTER` to dumpit/doit handlers. `drm_ras_nl_family` defines family name, version, netns support, parallel ops, module owner, split ops, and op count.

Control flow: Generic Netlink dispatch validates attributes with the policy associated with each split op, enforces admin permission flags, and calls handlers implemented in `drm_ras.c`.

State and persistence behavior: family and ops tables are static; `drm_ras_nl_family` is marked `__ro_after_init`.

Dependencies and integration points: generated from `Documentation/netlink/specs/drm_ras.yaml`; depends on UAPI `drm_ras.h`, netlink/genetlink headers, and handler prototypes from `drm_ras_nl.h`.

Risks: generated files should not be hand-edited; mismatch with YAML or UAPI breaks userspace tooling. `parallel_ops = true` means handlers must be concurrency safe. Admin permission flags restrict access and need to match intended observability.

Test signals: YNL regeneration diff, family registration, policy rejection for missing/wrong attrs, admin permission behavior, list and get command dispatch, and build checks after UAPI changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ras_nl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ras_nl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ras_nl.h

Purpose: generated internal header declaring DRM RAS netlink handler prototypes and the generated family object.

Important APIs/types/functions: declares `drm_ras_nl_list_nodes_dumpit()`, `drm_ras_nl_get_error_counter_doit()`, `drm_ras_nl_get_error_counter_dumpit()`, and `extern struct genl_family drm_ras_nl_family`.

Control flow: no runtime control flow; it provides compile-time coupling between generated op tables, family registration, and manually implemented handlers.

State and persistence behavior: no state.

Dependencies and integration points: includes netlink/genetlink headers and UAPI `drm_ras.h`; consumed by `drm_ras.c`, `drm_ras_nl.c`, and `drm_ras_genl_family.c`.

Risks: generated header must stay synchronized with the YAML spec and generated C table. Prototype drift produces build failures or incorrect dispatch signatures.

Test signals: YNL regeneration, `make drivers/gpu/drm/`, include self-containment checks where configured, and command prototype changes reflected in all users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ras_nl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_rect.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_rect.c

Purpose: provides rectangle math helpers for DRM plane clipping, scaling validation, debug printing, and coordinate transforms for rotation/reflection.

Important APIs/types/functions: `drm_rect_intersect()` clips one rectangle by another. `drm_rect_clip_scaled()` clips destination and adjusts 16.16 source coordinates while preserving scale. `drm_rect_calc_hscale()` and `drm_rect_calc_vscale()` calculate bounded source/destination scale factors through `drm_calc_scale()`. `drm_rect_debug_print()` logs integer or fixed-point rectangles. `drm_rect_rotate()` and `drm_rect_rotate_inv()` transform rectangles through DRM rotation/reflection flags.

Control flow: clipping computes side deltas, maps each destination clip delta to source shrinkage with pessimistic rounding, updates edges, and returns destination visibility. Scale calculation rejects negative dimensions, handles zero destination size, rounds down for upscaling and up for downscaling, then enforces min/max. Rotation applies reflections before rotation; inverse rotation applies inverse rotation before reflections.

State and persistence behavior: all functions are stateless and mutate only caller-provided rectangles.

Dependencies and integration points: used by plane atomic checks, helpers validating scaling limits, and debug output; depends on `drm_rect.h`, DRM mode rotation flags, and DRM debug macros.

Risks: callers must supply dimensions in the expected coordinate space and fixed-point convention. Overflow is mitigated in scaled clipping with 64-bit multiplication, but invalid large/negative rectangles can still trigger warnings or wrong caller behavior. Rotation and inverse rely on valid single rotation flag combinations.

Test signals: intersection visible/invisible cases, scaled clipping at all four edges, upscaling/downscaling rounding boundaries around 1.0, zero-size rectangles, min/max scale rejection, rotate followed by inverse returning original coordinates, and reflection combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_rect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_self_refresh_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_self_refresh_helper.c

Purpose: implements atomic helper support for panel self refresh, scheduling entry into self refresh after inactivity and adjusting atomic state to exit self refresh transparently.

Important APIs/types/functions: `struct drm_self_refresh_data` stores the target CRTC, delayed entry work, average mutex, and EWMA entry/exit times. `drm_self_refresh_helper_entry_work()` commits a self-refresh-active state. `drm_self_refresh_helper_update_avg_times()` updates transition timing. `drm_self_refresh_helper_alter_state()` modifies atomic state for self-refresh exit and queues future entry. `drm_self_refresh_helper_init()` and `drm_self_refresh_helper_cleanup()` manage per-CRTC helper lifetime.

Control flow: alter_state detects async or no-modeset updates that would touch a CRTC currently in self refresh and forces a normal modeset-capable update so SR can exit. For active CRTCs with helper data, it schedules entry work after twice the sum of recent entry and exit averages. Entry work allocates an atomic state, handles modeset deadlock retries, verifies the CRTC is enabled and all affected connectors are `self_refresh_aware`, sets `active=false` and `self_refresh_active=true`, then commits.

State and persistence behavior: helper data hangs off `crtc->self_refresh_data`, with delayed work on `system_percpu_wq` and EWMA timings seeded to 200 ms. Atomic commits persist self-refresh state in CRTC state, hidden from userspace.

Dependencies and integration points: integrates atomic state allocation/commit, modeset locking, connector self-refresh awareness, CRTC state flags, and driver atomic_check/commit_tail expectations.

Risks: entry work races with normal atomic commits and depends on deadlock backoff correctness. Drivers must fail atomic_check if hardware cannot enter SR despite awareness. Cleanup must cancel delayed work before freeing helper data. Forcing async updates into full modesets can surprise paths assuming no modeset work.

Test signals: init/cleanup and double-init rejection, delayed entry after inactivity, no entry when connectors are not aware, SR exit on plane/CRTC updates, EWMA transition updates, deadlock retry coverage, and suspend/unload cancellation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_self_refresh_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_simple_kms_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_simple_kms_helper.c

Purpose: provides simple display pipe helpers for DRM drivers with one primary plane, one CRTC, and one encoder, forwarding atomic operations to optional driver callbacks.

Important APIs/types/functions: `drm_simple_encoder_init()` and `__drmm_simple_encoder_alloc()` create simple encoders. Internal CRTC helper funcs handle mode validation, atomic check, enable, and disable. CRTC funcs handle reset, state duplicate/destroy, config, page flip, and vblank. Plane helper funcs handle prepare/cleanup framebuffer, begin/end access, atomic check/update. `drm_simple_display_pipe_attach_bridge()` attaches bridges, and `drm_simple_display_pipe_init()` wires plane, CRTC, encoder, optional connector, formats, and modifiers.

Control flow: pipe init stores connector/functions, registers plane helper and universal primary plane, registers CRTC helper and CRTC with the plane, initializes encoder possible CRTCs, creates encoder, and optionally attaches the connector. Atomic CRTC check ensures enabled CRTCs have a primary plane and adds affected planes. Plane check enforces no scaling and calls driver `check` only when visible. Enable/update/disable and framebuffer access paths forward to pipe callbacks when present, otherwise default GEM prepare is used for GEM drivers.

State and persistence behavior: state is embedded in `struct drm_simple_display_pipe` and standard DRM plane/CRTC/encoder objects. Atomic state duplication/reset can be default or driver-supplied.

Dependencies and integration points: integrates DRM atomic helpers, GEM plane helpers, bridge attach, probe helper mode validation, encoder/plane/CRTC init, and optional simple display pipe callback table.

Risks: this helper assumes a linear simple pipeline and no scaling. Non-GEM drivers without custom `prepare_fb` hit warnings. Format modifier support defaults to linear only. Partial init failures return immediately but callers must handle cleanup through normal DRM object cleanup or managed allocation patterns.

Test signals: simple driver modeset smoke tests, atomic check without primary plane, visible/invisible plane callback behavior, GEM prepare fallback, bridge attach, connector attach, vblank callback forwarding, format modifier rejection except linear, and init failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_simple_kms_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_suballoc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_suballoc.c

Purpose: implements a fence-aware linear range suballocator for DRM memory pools, optimized for ring-like GPU progress and reuse after fences signal.

Important APIs/types/functions: `drm_suballoc_manager_init()` and `drm_suballoc_manager_fini()` manage allocator lifetime. `drm_suballoc_alloc()`, `drm_suballoc_insert()`, `drm_suballoc_new()`, and `drm_suballoc_free()` allocate, insert, create, and free suballocations. Internal helpers manage holes, signaled frees, queue selection, and waiting. `drm_suballoc_dump_debug_info()` prints allocator state under debugfs.

Control flow: insert validates size/alignment, initializes the suballoc, then loops under the waitqueue spinlock. It frees signaled allocations after the current hole, tries to allocate from the current hole, advances to the next viable hole by removing closest signaled allocations or collecting unsignaled oldest fences, and waits on collected fences or the waitqueue until space may be available. Free either removes immediately if no unsignaled fence is supplied or queues the allocation on a fence bucket selected by fence context and wakes waiters.

State and persistence behavior: manager stores total size, alignment, current hole pointer, ordered allocation list, per-queue fence lists, and waitqueue. Each suballoc records offsets, manager pointer, optional fence reference, and list nodes.

Dependencies and integration points: used by DRM drivers needing temporary GPU-visible subranges; depends on dma-fence signaling, waitqueues, spin locking, DRM printer debug output, and caller-managed backing storage.

Risks: manager finalization with unsignaled fences logs and clears anyway, indicating caller lifetime bugs. Alignment is rounded to power of two at manager init but per-insert align greater than manager align is rejected. Waiting behavior must not be used from contexts that cannot sleep. Fence bucket hashing by context can affect fairness.

Test signals: aligned allocation and wraparound reuse, immediate free and fenced free, wait interrupted vs uninterruptible paths, multiple fence queues, finalization with outstanding fences, debug dump formatting, size/align invalid input, and stress tests with concurrent producers under external serialization assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_suballoc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_syncobj.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_syncobj.c

Purpose: implements DRM synchronization objects for binary and timeline GPU synchronization, including handle/fd lifetime, sync_file import/export, wait and eventfd notification ioctls, reset/signal/query operations, and timeline point transfer.

Important APIs/types/functions: `struct syncobj_wait_entry` and `struct syncobj_eventfd_entry` track blocking waits and eventfd waits. Core APIs include `drm_syncobj_find()`, `drm_syncobj_add_point()`, `drm_syncobj_replace_fence()`, `drm_syncobj_find_fence()`, `drm_syncobj_create()`, `drm_syncobj_get_handle()`, `drm_syncobj_get_fd()`, `drm_syncobj_open()`, and `drm_syncobj_release()`. Ioctl handlers cover create, destroy, handle-to-fd, fd-to-handle, transfer, wait, timeline wait, eventfd, reset, signal, timeline signal, and query. Wait conversion uses `drm_timeout_abs_to_jiffies()`.

Control flow: syncobjs are per-file xarray handles referencing refcounted objects. Binary replacement swaps the RCU fence pointer under spinlock and wakes wait/eventfd entries. Timeline signaling wraps fences in `dma_fence_chain` nodes and installs a new head. Wait paths resolve handles, copy optional timeline points, prevalidate missing fences unless wait-for-submit/available is set, register syncobj callbacks for future fence submission and dma-fence callbacks for signaling, sleep interruptibly until any/all conditions are met, timeout, or signal, then clean all callbacks and refs. FD export uses an anon-inode for whole syncobjs or sync_file for immutable fence snapshots; import reverses those paths.

State and persistence behavior: each `drm_file` owns a `syncobj_xa` until release. Each syncobj stores a refcount, spinlock, RCU fence pointer, submit-wait list, and eventfd list. Timeline history persists through dma_fence_chain links until garbage collected by fence references.

Dependencies and integration points: integrates dma-fence, dma-fence-chain, sync_file, eventfd, anon_inode, xarray, DRM driver feature flags `DRIVER_SYNCOBJ` and `DRIVER_SYNCOBJ_TIMELINE`, and user ioctls used by Vulkan/OpenGL synchronization stacks.

Risks: callback lifetime is subtle: every wait path must remove syncobj callbacks and dma-fence callbacks on all exits. Wait-for-submit asserts no locks are held because it can sleep on userspace-driven submission. Timeline points can be added out of order, producing query ambiguity noted by debug messages. Eventfd callbacks free their own entries after signaling. Importing a sync_file to a timeline point has an allocation error path after finding the syncobj that must still drop references correctly.

Test signals: create/destroy and fd import/export refcounts, sync_file import/export snapshots, binary wait for all/any/timeout/deadline, wait-for-submit across threads, timeline wait-available and signal points, eventfd signal-on-available/signal-on-fence, reset and signal arrays, transfer between binary/timeline syncobjs, query last submitted/signaled, lockdep sleep assertions, and KASAN/KCSAN callback cleanup stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_syncobj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_sysfs.c

Purpose: creates the DRM sysfs class, DRM minor and connector devices, connector attributes, EDID binary attribute, Type-C and DDC links, ACPI companion mapping, hotplug/property/lease uevents, and helper registration for class devices.

Important APIs/types/functions: `drm_sysfs_init()` and `drm_sysfs_destroy()` manage global `drm_class`. `drm_sysfs_connector_add()`, `_add_late()`, `_remove_early()`, and `_remove()` manage connector devices and links. Attribute handlers expose `status`, `enabled`, `dpms`, `modes`, `connector_id`, and binary `edid`; `status_store()` also forces/reprobes connector state. Uevent helpers include `drm_sysfs_lease_event()`, `drm_sysfs_hotplug_event()`, `drm_sysfs_connector_hotplug_event()`, and `drm_sysfs_connector_property_event()`. `drm_sysfs_minor_alloc()`, `drm_class_device_register()`, and `_unregister()` handle minor and auxiliary class devices.

Control flow: sysfs init creates class `drm`, adds a version attribute, installs a devnode callback returning `dri/<name>`, and registers the ACPI bus type. Connector add allocates a device, sets class/type/parent/groups/driver data/name, registers it, saves `connector->kdev`, and adds a Type-C component link if firmware node exists. Late add creates a DDC symlink. Status writes lock `mode_config.mutex`, update force state from strings, and invoke `fill_modes()` when force changes or detect is requested. Uevent helpers build environment strings and emit `KOBJ_CHANGE`.

State and persistence behavior: global `drm_class` persists between DRM core init and exit. Connector `kdev` persists while registered and is freed by `drm_sysfs_release()`. Sysfs reads reflect live connector state protected by locks or `READ_ONCE`; mode names come from connector mode list.

Dependencies and integration points: integrates Linux driver core, sysfs attributes, kobjects, ACPI bus matching, component framework for Type-C links, I2C DDC devices, PCI primary display detection, accel minors, DRM connector/mode/property internals, and userspace udev/hotplug consumers.

Risks: `status_store()` invokes `fill_modes()` under `mode_config.mutex`, so connector callbacks must obey expected locking. `modes_show()` uses `scnprintf()` into one PAGE_SIZE buffer and can truncate many modes. Uevent environment is fixed-size stack storage and must remain valid during call. Connector remove paths split early DDC unlink from device unregister and must be ordered by callers.

Test signals: class init/destroy, minor allocation for card/render/accel, connector sysfs add/remove and DDC link lifecycle, status force writes and invalid values, EDID binary reads, Type-C symlink creation/removal, hotplug/property/lease uevent environment, ACPI companion lookup, and primary boot display attribute visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_trace.h

Purpose: declares DRM tracepoints for vblank event creation, queueing, and delivery.

Important APIs/types/functions: defines `TRACE_SYSTEM drm` and `TRACE_INCLUDE_FILE drm_trace`. Trace events are `drm_vblank_event(crtc, seq, time, high_prec)`, `drm_vblank_event_queued(file, crtc, seq)`, and `drm_vblank_event_delivered(file, crtc, seq)`.

Control flow: each `TRACE_EVENT` declares prototype arguments, stores fields in the trace entry, assigns them in `TP_fast_assign`, and formats output with `TP_printk`. The header ends with `TRACE_INCLUDE_PATH ../../drivers/gpu/drm` and includes `trace/define_trace.h` outside the include guard per tracepoint conventions.

State and persistence behavior: no direct state; tracepoint enablement and buffers are managed by ftrace/tracefs.

Dependencies and integration points: included by DRM vblank code and by `drm_trace_points.c` with `CREATE_TRACE_POINTS`. Depends on Linux tracepoint infrastructure and forward declaration of `struct drm_file`.

Risks: tracepoint ABI names and fields are observable by tracing tools. Include path and guard structure must remain tracepoint-compatible. File pointer tracing exposes kernel pointer formatting subject to kernel pointer restrictions.

Test signals: build with tracing enabled/disabled, tracefs event presence under `events/drm`, vblank queue/delivery trace capture, and header self-containment with `TRACE_HEADER_MULTI_READ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_trace_points.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_trace_points.c

Purpose: instantiates the DRM tracepoints declared in `drm_trace.h`.

Important APIs/types/functions: includes `drm/drm_file.h`, defines `CREATE_TRACE_POINTS`, then includes local `drm_trace.h`.

Control flow: compile-time tracepoint instantiation only; the tracepoint macros emit the storage and registration code for events declared in the header.

State and persistence behavior: tracepoint registration/static key state is owned by kernel tracing infrastructure; this file holds no custom state.

Dependencies and integration points: must be built exactly once into DRM core so other files can include `drm_trace.h` without duplicate definitions.

Risks: duplicate `CREATE_TRACE_POINTS` elsewhere causes linker conflicts; omitting this object removes tracepoint definitions. Include order must provide complete types needed by trace macros.

Test signals: DRM core link succeeds, trace events appear once, enabling/disabling vblank tracepoints works, and no duplicate symbol errors under modular and built-in builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_trace_points.c -->
