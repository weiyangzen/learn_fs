# Research Report: subset-b-005812

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gpusvm.h -->
## sources/distributed-fs/ceph-client/include/drm/drm_gpusvm.h

Purpose: declares the DRM GPU Shared Virtual Memory helper API. It lets a driver track CPU `mm_struct` address ranges mirrored into GPU page tables, bind those ranges to MMU interval notifiers, cache acquired pages and DMA mappings, and react to CPU invalidations.

Important APIs and types: `struct drm_gpusvm` is the top-level SVM tracker, with an interval tree and ordered list of notifiers protected by `notifier_lock`. `struct drm_gpusvm_notifier` wraps `mmu_interval_notifier` and owns an interval tree/list of `drm_gpusvm_range` objects. `struct drm_gpusvm_range` carries range interval metadata, kref lifetime, and `drm_gpusvm_pages`. `struct drm_gpusvm_ctx` controls get-pages behavior: device-private owner, chunk thresholds, timeslice, notifier context, read-only mode, device-memory policy, and mixed mapping allowance. Driver callbacks in `drm_gpusvm_ops` allocate/free notifiers and ranges and perform required invalidation. Key functions cover initialization/finalization, VMA discovery, range find/insert/remove/evict/refcounting, page acquisition/unmap/free, validity checks, notifier/range lookup, and `drm_gpusvm_scan_mm()`.

Control flow: drivers initialize the embedded `drm_gpusvm`, then on GPU faults or map requests call `drm_gpusvm_range_find_or_insert()`. The helper locates or creates a notifier-sized tracking object, inserts a range into that notifier, acquires CPU or device-private pages through `drm_gpusvm_range_get_pages()`, and later validates cached pages against notifier sequence state. MMU invalidation enters the driver's `invalidate` callback while the notifier lock is held, allowing safe traversal with `drm_gpusvm_for_each_notifier()` and `drm_gpusvm_for_each_range()` or their safe variants.

State and persistence behavior: all state is runtime kernel memory. Pages record DMA addresses, an optional `drm_pagemap`, notifier sequence, and flags for migration, unmap status, device pages, and DMA mapping. Range and notifier interval nodes provide fast overlap lookup plus list order for mutation during traversal. No standalone SVM refcount exists; the header expects embedding inside a driver VM whose lifetime is managed elsewhere.

Dependencies and integration points: depends on Linux interval trees, krefs, MMU interval notifiers, optional lockdep, device private memory/dev_pagemap, and DRM pagemap abstractions. It integrates with driver GPU page table invalidation, page migration to device memory, DMA mapping, and VM lock annotations through `drm_gpusvm_driver_set_lock()`.

Risks: invalidation ordering is subtle because page validity depends on notifier sequence and per-range flags set under `notifier_lock`. Mixing system and device pages is only conditionally supported and multiple device pagemaps are rejected by policy. Driver callbacks are optional except invalidation, so NULL callback paths must match allocation expectations. Iterators assume the caller holds the driver SVM lock or notifier lock.

Test signals: compile with and without `CONFIG_LOCKDEP`, map/unmap overlapping SVM ranges, MMU invalidation during traversal, migration to and from device memory, DMA mapping cleanup, mixed system/device page scans, notifier removal, refcount put/free paths, and lockdep coverage with a driver-provided lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gpusvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gpuvm.h -->
## sources/distributed-fs/ceph-client/include/drm/drm_gpuvm.h

Purpose: declares the DRM GPU virtual address manager. It tracks GPU virtual mappings, their backing GEM objects, eviction state, external reservation objects, and split/merge operation plans used by drivers to implement map, unmap, remap, prefetch, madvise, and BO-wide unmap flows.

Important APIs and types: `struct drm_gpuvm` owns the VA interval tree/list, reference count, reserved kernel allocation node, shared reservation GEM object, external object list, evict list, deferred BO cleanup list, and `drm_gpuvm_ops`. `struct drm_gpuva` represents a mapped VA range with flags such as `DRM_GPUVA_INVALIDATED` and `DRM_GPUVA_SPARSE`. `struct drm_gpuvm_bo` ties one GEM object to one GPUVM and indexes all GPUVAs backed by that object. `struct drm_gpuva_op` and `struct drm_gpuva_ops` describe generated map/remap/unmap/prefetch operations. Public functions cover VA insertion/removal/lookup, VM init/refcounting, dma-resv locking with `drm_gpuvm_exec`, object preparation/validation, fence publication, BO obtain/find/evict, split/merge op creation, and state-changing helpers `drm_gpuva_map()`, `drm_gpuva_remap()`, and `drm_gpuva_unmap()`.

Control flow: a driver initializes a GPUVM with address limits and callbacks, locks the VM and relevant GEM reservations with `drm_gpuvm_exec_lock*()`, asks the split/merge helpers to create or execute an operation sequence, then applies driver page table updates in `sm_step_map`, `sm_step_remap`, and `sm_step_unmap`. Mapping links GPUVAs to both the VM interval tree and the GEM-specific `drm_gpuvm_bo`; unmapping detaches both. Evicted BOs are marked on GEM eviction and later validated via `drm_gpuvm_validate()`.

State and persistence behavior: state is in-memory and reference counted. The VM's shared reservation object serializes private VM work unless the driver declares external protection. External objects are GEMs whose dma-resv differs from the GPUVM reservation and are tracked separately for locking/fencing. `DRM_GPUVM_IMMEDIATE_MODE` changes locking of GEM GPUVA lists for fence-signalling path modifications. Deferred BO cleanup uses an llist to avoid freeing during sensitive paths.

Dependencies and integration points: integrates with `drm_gem_object`, GEM GPUVA lists, `dma_resv`, `drm_exec`, dma fences, rb-tree interval lookup, and driver memory managers such as TTM through validation callbacks. It is the common contract used by newer DRM drivers to avoid each driver reimplementing VA splitting and object reservation choreography.

Risks: deadlock avoidance depends on consistently using the `drm_exec` wrappers and not mutating VA trees without required reservations. Split/remap operations preserve driver-private VA data by handing the original unmap object to callbacks; misuse can lose metadata. External BO and evict list state is protected by a mix of spinlocks, GEM locks, and dma-resv locks. Async or immediate-mode users must not race GEM GPUVA list mutation.

Test signals: overlapping maps that split existing VAs, partial unmaps producing prev/next remaps, sparse mappings, BO-wide unmap creation, GEM eviction and validation, external-object fence addition, lock retry behavior under contention, deferred BO cleanup, invalidation flag toggling, and driver callback error unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gpuvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_ioctl.h -->
## sources/distributed-fs/ceph-client/include/drm/drm_ioctl.h

Purpose: declares the DRM ioctl dispatch interface, ioctl descriptor format, permission flags, and common helper handlers used by DRM core and drivers.

Important APIs and types: `drm_ioctl_t` is the normal kernel-space handler signature after `drm_ioctl()` has copied ioctl payload data. `drm_ioctl_compat_t` supports 32-bit compatibility handlers. `enum drm_ioctl_flags` defines access policy: `DRM_AUTH`, `DRM_MASTER`, `DRM_ROOT_ONLY`, and `DRM_RENDER_ALLOW`. `struct drm_ioctl_desc` stores command number, flags, handler, and debug name. `DRM_IOCTL_DEF_DRV()` builds driver-private descriptor table entries from UAPI command names. Public functions include `drm_ioctl()`, `drm_ioctl_kernel()`, optional `drm_compat_ioctl()`, `drm_ioctl_flags()`, `drm_noop()`, and `drm_invalid_op()`.

Control flow: file operations route userspace ioctl calls to `drm_ioctl()`, which decodes the command number/type, enforces descriptor flags against the `drm_file` state and node type, copies payload according to ioctl direction, calls the descriptor handler, and copies results back as needed. Kernel callers can bypass userspace copying through `drm_ioctl_kernel()`.

State and persistence behavior: the header defines no persistent state, but its flags gate access to per-file authentication, master ownership, capabilities, and render-node behavior maintained by DRM core.

Dependencies and integration points: uses Linux ioctl encoding, bit operations, `struct file`, `struct drm_device`, and `struct drm_file`. It is included by DRM core ioctl tables and driver files that define private ioctls.

Risks: incorrect flags expose privileged display-control operations to unauthenticated clients or render nodes. Compat handlers should be rare; adding one usually indicates UAPI structure layout issues. Handler data has already been copied and may be copied back, so handler assumptions must match ioctl direction bits.

Test signals: ioctl permission tests across primary/control/render nodes, unauthenticated and non-master file descriptors, root-only SETMASTER/DROPMASTER-like paths, compat builds, invalid op handling, and driver-private `DRM_IOCTL_DEF_DRV()` table indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_kunit_helpers.h -->
## sources/distributed-fs/ceph-client/include/drm/drm_kunit_helpers.h

Purpose: declares KUnit helpers for constructing lightweight DRM devices and modeset objects in tests without requiring a full hardware driver.

Important APIs and types: device helpers allocate and free mock parent devices. `__drm_kunit_helper_alloc_drm_device_with_driver()` allocates a DRM device embedded at a caller-specified offset in a test container type using a supplied `drm_driver`. The `drm_kunit_helper_alloc_drm_device_with_driver()` macro provides type-safe container recovery. `__drm_kunit_helper_alloc_drm_device()` creates a managed test `drm_driver` from feature bits, and `drm_kunit_helper_alloc_drm_device()` wraps it. Additional helpers allocate atomic state, create primary planes and CRTCs, enable a CRTC/connector pair with a mode, register mode destruction actions, and build display modes from CEA VICs.

Control flow: tests allocate a parent `struct device`, allocate an embedded DRM device through devm-managed allocation, then create planes, CRTCs, connectors, modes, and atomic state. KUnit assertions inside inline allocation helpers fail the test immediately if a mock driver allocation fails.

State and persistence behavior: all resources are scoped to the KUnit test and/or devm lifetime of the mock parent device. Mode destruction can be registered as a KUnit cleanup action. The helpers intentionally keep state local to test contexts.

Dependencies and integration points: depends on KUnit, Linux device management, `drm_drv.h`, DRM atomic state, plane/CRTC/helper vtables, connector objects, and display mode helpers. It is an integration point for DRM unit tests that need realistic object initialization.

Risks: helper macros rely on correct container type/member/offset arguments. Feature-bit-only mock drivers may omit callbacks that tested code assumes exist. Tests must pair helper-created modes and atomic states with cleanup actions to avoid leaks detected by KUnit.

Test signals: KUnit suites using managed DRM device allocation, object construction failure paths, atomic state allocation, CRTC/connector enabling, CEA VIC conversion, and leak-free cleanup at test teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_kunit_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_lease.h -->
## sources/distributed-fs/ceph-client/include/drm/drm_lease.h

Purpose: declares the DRM KMS leasing interface that lets a DRM master delegate selected mode objects to a lessee file descriptor while retaining ownership hierarchy and revocation support.

Important APIs and types: `drm_lease_owner()` finds the owner master for a lessee, `drm_lease_destroy()` releases lease state for a lessee master, `drm_lease_held()` and `_drm_lease_held()` test access to a KMS object id, `drm_lease_revoke()` revokes a master's leases, and `drm_lease_filter_crtcs()` masks CRTC bits through lease visibility. UAPI ioctl handlers are declared for create lease, list lessees, get current lease objects, and revoke lease.

Control flow: a master creates a lease through `drm_mode_create_lease_ioctl()`, passing a set of object IDs. Later KMS object lookup and ioctl paths use lease checks to restrict object visibility. Lessees can be listed, queried, and revoked through the other ioctl handlers; destruction runs when a lessee master is torn down.

State and persistence behavior: lease state is tied to `struct drm_master` and `struct drm_file` lifetimes, not persistent storage. Revocation changes in-kernel master/lease relationships and immediately affects object access.

Dependencies and integration points: integrates with DRM master handling, mode object lookup, CRTC masks, KMS ioctls, and access control in mode-setting paths.

Risks: lease filtering must be applied consistently or lessees can access objects outside their lease. Revocation must handle active lessee file descriptors without use-after-free. CRTC bit filtering can silently affect legacy APIs that use bitmasks instead of object IDs.

Test signals: create/list/get/revoke lease ioctls, lessee object lookup denial, CRTC mask filtering, lease owner traversal, master destruction with active leases, and revocation during modeset attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_lease.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_managed.h -->
## sources/distributed-fs/ceph-client/include/drm/drm_managed.h

Purpose: declares DRM-device-managed resource helpers, mirroring devres-style cleanup but tied to the final `drm_dev_put()` lifetime of a `drm_device`.

Important APIs and types: `drmres_release_t` is a cleanup callback receiving the DRM device and resource pointer. `drmm_add_action()` and `drmm_add_action_or_reset()` register reverse-order release actions, the latter immediately running the action on registration failure. `drmm_release_action()` removes and runs matching actions early. Managed allocators include `drmm_kmalloc()`, `drmm_kzalloc()`, `drmm_kmalloc_array()`, `drmm_kcalloc()`, `drmm_kstrdup()`, and `drmm_kfree()`. `drmm_mutex_init()` registers mutex destruction, and `drmm_alloc_ordered_workqueue()` registers ordered workqueue destruction.

Control flow: drivers allocate resources during probe or mode-config init and register cleanup actions against the DRM device. On final DRM device release, actions run in reverse allocation order. The array helpers check multiplication overflow before allocation; the workqueue macro creates the workqueue and registers cleanup atomically from the caller's perspective.

State and persistence behavior: resources persist until manually freed or until the DRM device's last reference is dropped. Cleanup ordering is stack-like, which lets dependent resources be unwound safely.

Dependencies and integration points: uses Linux GFP allocation, overflow helpers, mutexes, workqueues, and `struct drm_device`. It underpins managed variants such as `drmm_mode_config_init()` and modern DRM probe cleanup patterns.

Risks: resources whose lifetime is shorter than the DRM device still need explicit release. `drmm_add_action_or_reset()` callbacks must tolerate being invoked on partial initialization failure. Workqueue cleanup must happen after queued work is quiesced or designed to be destroyed by the release callback.

Test signals: probe failure unwinding, final `drm_dev_put()` cleanup order, overflow rejection in array allocation, early `drmm_kfree()` and action release, mutex lockdep cleanup, and managed workqueue destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_managed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_mipi_dbi.h -->
## sources/distributed-fs/ceph-client/include/drm/drm_mipi_dbi.h

Purpose: declares helper infrastructure for small MIPI DBI/SPI display controllers, combining bus command helpers, a simple DRM device container, framebuffer conversion/copy support, and ready-made plane/CRTC/connector/mode-config helper vtables.

Important APIs and types: `struct mipi_dbi` stores the command lock, bus-specific command callback, readable command table, byte-swap flag, reset GPIO, and Type-C SPI fields such as D/C GPIO, 9-bit conversion buffer, and write-memory bits-per-word. `struct mipi_dbi_dev` embeds `drm_device`, fixed mode, native pixel format, transfer buffer, rotation, controller offsets, optional backlight/regulators, the DBI interface, and driver-private data. Functions initialize SPI and DRM DBI devices, perform hardware/power-on resets, test display-on state, calculate SPI command speed, transfer SPI buffers, read/write commands, copy framebuffer clips, and initialize debugfs.

Control flow: a tiny-panel driver initializes the SPI-backed DBI bus, initializes `mipi_dbi_dev` with a fixed mode and transfer buffer, registers simple DRM plane/CRTC/connector helpers, then sends MIPI DCS commands via `mipi_dbi_command()` or lower-level buffer helpers. Atomic plane updates copy damaged framebuffer regions into the 16-bit TX buffer and transmit write-memory commands.

State and persistence behavior: command serialization is protected by `cmdlock`. TX buffers, GPIO/regulator/backlight pointers, offsets, rotation, and fixed mode live for the DRM device lifetime. Debugfs is optional under `CONFIG_DEBUG_FS`.

Dependencies and integration points: integrates with SPI, GPIO, regulators, backlight, DRM atomic helpers, GEM shadow framebuffer helpers, format conversion, probe helpers, and MIPI DCS command definitions.

Risks: SPI controllers vary in bits-per-word and max-speed behavior; 9-bit emulation and byte swapping must match panel requirements. Command helpers assume `dbi->spi` is present for error logging. Framebuffer clip copying must respect format, pitch, rotation, offsets, and buffer size. Power/reset sequencing is panel-specific despite common helpers.

Test signals: SPI command/read paths, reset and conditional reset sequencing, RGB565/XRGB8888 framebuffer updates, byte-swap behavior, dirty rectangle clipping, regulator/backlight enable/disable, debugfs command access, and atomic mode validation against the fixed panel mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_mipi_dbi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_mipi_dsi.h -->
## sources/distributed-fs/ceph-client/include/drm/drm_mipi_dsi.h

Purpose: declares the MIPI DSI bus, host/device model, packet/message representation, DSI mode flags, DCS/generic command helpers, multi-command error accumulation, dual-DSI helpers, and DSI driver registration macros.

Important APIs and types: `struct mipi_dsi_msg` describes one transfer with channel, data type, flags, TX buffer, and optional RX buffer. `struct mipi_dsi_packet` is the protocol packet form. `struct mipi_dsi_host_ops` supplies attach/detach/transfer callbacks for host controllers, while `struct mipi_dsi_host` registers those ops on the DSI bus. `struct mipi_dsi_device` records host, device, attachment state, virtual channel, lanes, pixel format, mode flags, HS/LP rates, and optional DSC config. The API covers host/device registration, OF lookup, attach/detach, devm attach, peripheral power commands, compression and PPS commands, generic read/write, DCS command helpers, brightness helpers, multi-context variants, dual-interface macros, and `mipi_dsi_driver` registration.

Control flow: host drivers register a `mipi_dsi_host`; panel or bridge drivers create/find a `mipi_dsi_device`, set lanes/format/mode flags/rates, attach to the host, and send initialization commands. Message helpers build short or long DSI packets and call the host `transfer` callback. Multi helpers skip later commands after the first accumulated error, allowing panel init tables to be linear.

State and persistence behavior: DSI host/device state is Linux driver-model state. `attached` tracks successful host binding. Mode flags persist as device configuration and influence host transfer/video setup. `mipi_dsi_multi_context.accum_err` is transient command-sequence state.

Dependencies and integration points: depends on Linux devices, delays, OF graph lookup, DRM DSC structures, display bus formats, panel/bridge drivers, and module driver helpers. It bridges DRM display drivers to physical DSI host controller transfer implementations.

Risks: macros such as `mipi_dsi_dual()` evaluate function arguments twice and warn about side effects. HS/LP rates of zero are only legacy-compatible and should not hide real hardware limits. Host transfer callbacks may be called regardless of power state, so host drivers must power-manage internally. Packet type/length mistakes can corrupt panel command streams.

Test signals: packet creation for short/long formats, generic and DCS reads/writes, multi-context error short-circuiting, dual-DSI command ordering, attach/detach/devm cleanup, DSC compression/PPS sequences, pixel-format-to-bpp mapping, OF host/device lookup, and host transfer behavior in LP/HS modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_mipi_dsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_mm.h -->
## sources/distributed-fs/ceph-client/include/drm/drm_mm.h

Purpose: declares the DRM generic range allocator, historically used for GPU address spaces and memory heaps. It manages allocated nodes, free holes, address/size-ordered search trees, and eviction scanning.

Important APIs and types: `enum drm_mm_insert_mode` selects best-fit, low-address, high-address, eviction-hole, lowest-only, or highest-only allocation behavior. `struct drm_mm_node` represents an allocated block with start, size, color tag, list/rb-tree nodes, hole metadata, allocation/scanned flags, and optional debug stack. `struct drm_mm` owns the allocator, optional `color_adjust` callback, hole stack, sentinel head node, interval tree, hole-size/address trees, and scan state flag. `struct drm_mm_scan` stores parameters and hit range for eviction scanning. APIs reserve existing nodes, insert nodes in a range, remove nodes, initialize/take down allocators, iterate nodes/holes/ranges, initialize eviction scans, add/remove scan blocks, choose color eviction candidates, and print allocator state.

Control flow: drivers initialize an allocator with a base and size, then insert preallocated cleared nodes through `drm_mm_insert_node*()` or reserve known ranges with `drm_mm_reserve_node()`. The allocator searches holes according to mode and range constraints, applies `color_adjust` if present, inserts into all tracking structures, and updates hole metadata. Eviction flow initializes a scan, temporarily marks/removes candidate blocks to form a hole, checks if the requested allocation fits, and then removes or restores candidates.

State and persistence behavior: allocator state is entirely in memory and embedded by drivers. Nodes are driver-allocated and must be zeroed before insertion. Holes are represented implicitly as metadata on the node before the free range, including the sentinel head node. Debug builds can record allocation stack traces and use `BUG_ON` assertions.

Dependencies and integration points: uses Linux rb-trees, lists, stackdepot under `CONFIG_DRM_DEBUG_MM`, and DRM printer support. It is a lower-level allocator used by DRM memory managers and address-space code.

Risks: callers must provide external locking. Range iterator misuse outside allocator bounds can walk the sentinel and potentially loop. Node reuse without clearing violates allocation flag assumptions. Color-adjust callbacks can shrink holes incorrectly and cause false `-ENOSPC`. Eviction scanning restricts other allocator operations while active.

Test signals: allocation modes and alignment, range-limited insertion, reserved node insertion, color-adjust guard pages, hole iteration, node-in-range iteration, removal/clean checks, eviction scan add/remove decisions, debug stack output, and concurrent caller lock coverage in drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_mode_config.h -->
## sources/distributed-fs/ceph-client/include/drm/drm_mode_config.h

Purpose: declares the central KMS mode-configuration object and global driver callbacks for framebuffer creation, mode validation, atomic checking/commit, and optional atomic state subclassing.

Important APIs and types: `struct drm_mode_config_funcs` contains `fb_create`, `get_format_info`, device-wide `mode_valid`, `atomic_check`, `atomic_commit`, and optional `atomic_state_alloc/clear/free`. `struct drm_mode_config` owns the global modeset mutex, connection lock, legacy acquire context, IDR locks and ID spaces, framebuffer list, connector list/free work, encoder/plane/colorop/CRTC/property/private-object lists, display size limits, output polling state, blob property lock/list, standard property pointers, dumb-buffer preferences, quirk flags, async flip and modifier flags, cursor limits, suspend atomic state, and helper-private callbacks. Initialization/cleanup APIs are `drmm_mode_config_init()`, deprecated wrapper `drm_mode_config_init()`, `drm_mode_config_reset()`, and `drm_mode_config_cleanup()`.

Control flow: drivers initialize mode config during probe, fill limits and callback pointers, create KMS objects and properties under this global registry, then expose ioctls. Userspace framebuffer creation calls `fb_create`; mode enumeration and atomic commits consult validation callbacks; atomic commits run `atomic_check` then `atomic_commit`; suspend/resume helpers stash state in `suspend_state`.

State and persistence behavior: `drm_mode_config` persists for the DRM device lifetime. It tracks global object IDs, object lists, property objects, blob properties, framebuffer objects, output polling work, and suspend state. Some lists are immutable after init, while connectors and framebuffers have dedicated locks/free work.

Dependencies and integration points: integrates with modeset locks, IDR/IDA, workqueues, framebuffer and format info, atomic state, connector polling, writeback, color management, TV/HDMI/HDCP/HDR properties, and managed cleanup via `drmm_mode_config_init()`.

Risks: lock layering is complex: global mutex, `connection_mutex`, IDR mutex, framebuffer lock, blob lock, connector spinlock, and panic raw spinlock protect different subsets. Atomic callbacks have strict error-code contracts; `atomic_commit` must not return validation-only errors such as `-EINVAL` or acquire new modeset locks. Modifier and legacy AddFB quirks affect userspace ABI.

Test signals: mode-config init/cleanup, framebuffer creation with modifiers and legacy quirks, atomic check/commit success and failure codes, connector hotplug polling, property/blob lifetime, suspend/resume state restore, connector free work, object ID allocation, and lockdep coverage for modeset locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_mode_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_mode_object.h -->
## sources/distributed-fs/ceph-client/include/drm/drm_mode_object.h

Purpose: declares the base object and property storage used by KMS objects visible to userspace, such as CRTCs, planes, connectors, framebuffers, property blobs, and properties.

Important APIs and types: `struct drm_mode_object` carries userspace ID, object type, attached properties, optional kref, and free callback for dynamic objects. `DRM_OBJECT_MAX_PROPERTY` caps attached properties at 64. `struct drm_object_properties` stores property pointers and parallel default/current values. `DRM_ENUM_NAME_FN()` generates enum-name lookup helpers. Public APIs find mode objects with lease filtering, get/put dynamic objects, set/get property values, get default or immutable values, attach properties, and ask whether a mode object type requires lease checks.

Control flow: drivers initialize KMS objects and attach immutable/default properties before exposing them. Ioctl paths look up objects by ID/type through `drm_mode_object_find()`, optionally constrained by file lease state. Legacy property paths read/write the stored value array, while atomic drivers normally decode mutable properties into object state through atomic get/set hooks instead of mutating this array.

State and persistence behavior: object IDs live in the device mode-config IDR. Static objects usually have no free callback; dynamic objects use the embedded kref and callback. Property pointer/value arrays persist with the object and are valid until mode-config cleanup.

Dependencies and integration points: includes kref and DRM lease support. It integrates with property creation, atomic property hooks, KMS ioctl object lookup, and lease-required object type checks.

Risks: property array overflow is bounded by `DRM_OBJECT_MAX_PROPERTY` and must be respected by attach paths. Mutable atomic properties should not be treated as authoritative in `values[]`. Dynamic object refcount callbacks must match container layout. Lease filtering must be used for user-visible lookups.

Test signals: object lookup by ID/type, lease-denied lookup, property attach/get/set/default retrieval, immutable property access, dynamic object refcount release, and objects with maximum property counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_mode_object.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_modes.h -->
## sources/distributed-fs/ceph-client/include/drm/drm_modes.h

Purpose: declares DRM display mode representation, mode status codes, mode construction macros, timing conversion helpers, mode validation/comparison APIs, command-line mode parsing, and OF videomode conversion hooks.

Important APIs and types: `enum drm_mode_status` enumerates reasons a mode is unsupported, including sync limits, timing errors, memory limits, interlace/doublescan restrictions, YCbCr 4:2:0 restrictions, stale/bad/error states. `struct drm_display_mode` stores logical timings, adjusted CRTC timings, sync/3D flags, physical size, type flags, exposure flag, list node, name, validation status, and HDMI picture aspect ratio. Macros include `DRM_MODE`, `DRM_MODE_INIT`, `DRM_SIMPLE_MODE`, CRTC adjustment flags, match flags, `DRM_MODE_FMT`, and `DRM_MODE_ARG`. APIs allocate/destroy/duplicate/copy modes, convert to/from UAPI and `videomode`, add probed modes, create CVT/GTF/analog TV modes, set names, compute refresh and hv timing, set CRTC info, compare modes, validate modes, prune/sort mode lists, update connector lists, and parse command-line modes.

Control flow: drivers and helpers create modes from EDID, firmware, OF data, command line, or fixed panels, validate them through device/CRTC/encoder/connector constraints, set adjusted CRTC timings, expose accepted modes to userspace, and later convert selected modes to UAPI or hardware state.

State and persistence behavior: mode objects are list-managed and normally owned by connectors or temporary atomic state. The `status` field records validation result; `expose_to_userspace` is used while preparing GETCONNECTOR output. Hardware-adjusted fields are derived from logical timings and adjustment flags.

Dependencies and integration points: includes HDMI aspect definitions, mode objects, connectors/display info, OF display timings, and videomode conversion. It is central to probe helpers, atomic checks, panel drivers, bridge drivers, and command-line mode handling.

Risks: logical and CRTC-adjusted timings can diverge for interlace, doublescan, stereo, or clock-doubling; drivers must program the right copy. Mode comparison flags determine whether clocks, flags, 3D layout, and aspect ratio matter. Command-line or user-defined modes can bypass connector probed lists, so source hardware limits must be enforced elsewhere.

Test signals: EDID/probed mode creation, CVT/GTF generation, analog TV helpers, OF videomode parsing, mode name/refresh calculations, CRTC timing adjustment flags, YCbCr 4:2:0 validation, prune/sort behavior, command-line parsing, and equality/match variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_modes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_modeset_helper.h -->
## sources/distributed-fs/ceph-client/include/drm/drm_modeset_helper.h

Purpose: declares small KMS helper entry points for common framebuffer metadata filling, legacy CRTC initialization, connector ordering, and mode-config suspend/resume.

Important APIs and types: `drm_helper_move_panel_connectors_to_head()` reorders panel connectors for user-visible preference. `drm_helper_mode_fill_fb_struct()` fills a `drm_framebuffer` from format info and an AddFB2 mode command. `drm_crtc_init()` initializes a CRTC with core function callbacks. `drm_mode_config_helper_suspend()` and `drm_mode_config_helper_resume()` implement common atomic suspend/resume state capture and restoration.

Control flow: drivers call these helpers from probe, framebuffer creation, or PM hooks. Framebuffer creation validates and resolves format/modifier metadata, then uses `drm_helper_mode_fill_fb_struct()` before `drm_framebuffer_init()`. Suspend captures the current atomic state into mode config; resume reapplies it.

State and persistence behavior: the header owns no state. Helpers mutate DRM object initialization fields, framebuffer metadata, connector list order, and `mode_config.suspend_state`.

Dependencies and integration points: forward-declares core KMS types and integrates with framebuffer UAPI parsing, CRTC setup, connector lists, and atomic suspend/resume helpers.

Risks: framebuffer metadata must preserve implied modifiers and plane offsets/pitches for GETFB2 correctness. Suspend/resume helpers assume atomic modeset support and valid mode-config state. Connector reordering affects userspace-visible enumeration and should be used only for intended panel priority.

Test signals: AddFB2 framebuffer metadata, CRTC init paths, panel connector ordering, atomic suspend/resume with active CRTCs, and cleanup after failed resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_modeset_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_modeset_helper_vtables.h -->
## sources/distributed-fs/ceph-client/include/drm/drm_modeset_helper_vtables.h

Purpose: gathers the helper callback tables for DRM KMS objects: CRTC, encoder, connector, plane, and global mode-config helper operations. These vtables define the contracts consumed by legacy helper paths, atomic modeset helpers, probe helpers, writeback helpers, panic display, and commit helpers.

Important APIs and types: `struct drm_crtc_helper_funcs` includes legacy DPMS/prepare/commit/mode_set hooks, mode validation/fixup, atomic check/begin/flush/enable/disable, scanout-position, and vblank-timeout hooks. `struct drm_encoder_helper_funcs` covers encoder DPMS, mode validation/fixup, prepare/commit, mode_set/atomic_mode_set, detect, enable/disable, atomic enable/disable, and atomic_check. `struct drm_connector_helper_funcs` covers get_modes, atomic detect and mode validation with acquire context, best encoder selection, atomic connector check/commit, writeback job prepare/cleanup, and HPD enable/disable. `struct drm_plane_helper_funcs` covers framebuffer prepare/cleanup, begin/end access, atomic check/update/enable/disable, async check/update, panic scanout buffer retrieval, and panic flush. `struct drm_mode_config_helper_funcs` provides atomic commit tail/setup hooks. Inline `*_helper_add()` functions install vtables into object `helper_private` fields.

Control flow: drivers attach helper vtables after creating each KMS object. Probe helpers use connector, encoder, and CRTC mode validation to build exposed mode lists. Atomic helpers call check hooks first without touching persistent state, then commit helpers invoke prepare/access/update/flush/enable/disable callbacks in defined phases. Nonblocking commits can use global commit setup/tail hooks to track completion and cleanup. Panic paths call plane scanout hooks under the panic lock.

State and persistence behavior: vtable pointers persist in KMS objects for the device lifetime. Check callbacks must only mutate atomic state, while commit callbacks update hardware and driver runtime state. Framebuffer resources acquired in `prepare_fb` persist until cleanup; resources acquired in `begin_fb_access` last only for one commit.

Dependencies and integration points: includes CRTC and encoder core headers and references atomic state, connector/CRTC/plane state, writeback jobs, scanout buffers, vblank helpers, probe helpers, and DRM panic support.

Risks: legacy and atomic hooks have different semantics; mixing them incorrectly can break runtime PM or leak resources. Mode validation in probe paths cannot depend on current display state. Atomic check hooks may need to add more state and handle `-EDEADLK`. Async plane updates must swap framebuffer references correctly. Panic hooks run in constrained context and must not sleep or rely on complex locking.

Test signals: mode probing with connector/encoder/CRTC validation, atomic commit ordering, runtime PM enable/disable symmetry, writeback job prepare/cleanup, async cursor update, framebuffer pin/vmap cleanup, vblank timestamp callbacks, panic scanout path, HPD enable/disable balance, and lockdep/deadlock retries in atomic checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_modeset_helper_vtables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_modeset_lock.h -->
## sources/distributed-fs/ceph-client/include/drm/drm_modeset_lock.h

Purpose: declares DRM modeset locking primitives built on wound/wait mutexes, plus helper macros for acquiring all modeset locks with deadlock backoff.

Important APIs and types: `struct drm_modeset_acquire_ctx` wraps `ww_acquire_ctx`, tracks the contended lock, optional stackdepot debugging, list of held locks, trylock-only mode for panic contexts, and interruptible behavior. `struct drm_modeset_lock` wraps a `ww_mutex` plus list node used while held in an atomic update. APIs initialize/finalize acquire contexts, drop locks, back off after `-EDEADLK`, initialize/finalize individual locks, test/assert lock state, lock/unlock one lock, take one interruptibly, lock/unlock all device modeset locks, warn if not all locked, and lock all with a caller-provided context. `DRM_MODESET_LOCK_ALL_BEGIN/END` wrap retry/backoff boilerplate.

Control flow: callers initialize an acquire context, attempt to lock required modeset resources, and if any lock returns `-EDEADLK`, jump to cleanup/backoff, slow-lock the contended lock, and retry. The all-lock macros also take the legacy mode-config mutex for non-atomic drivers.

State and persistence behavior: held locks are linked into the acquire context until dropped. The contended pointer and debug stack record unresolved deadlock handling. Individual modeset locks persist inside CRTCs, planes, connectors, and mode-config objects.

Dependencies and integration points: uses Linux ww_mutex, stackdepot, lockdep, and DRM device/object declarations. It is foundational for atomic state acquisition, legacy modeset serialization, and helper callbacks that may add more state.

Risks: every `-EDEADLK` must trigger the backoff dance or deadlocks and debug warnings follow. `trylock_only` is for panic paths and cannot be used for normal blocking updates. Non-atomic and atomic drivers differ in whether the mode-config mutex is also taken. `drm_modeset_lock_fini()` warns if the lock is still linked.

Test signals: atomic commits acquiring multiple object locks, forced deadlock retry paths, interruptible lock acquisition, all-lock macros on atomic and non-atomic drivers, lockdep assertions, panic trylock users, and cleanup with no held lock list entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_modeset_lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_module.h -->
## sources/distributed-fs/ceph-client/include/drm/drm_module.h

Purpose: declares module registration helpers for DRM PCI and platform drivers that honor the global DRM firmware-driver-only policy and, for older users, a driver-specific modeset parameter.

Important APIs and types: `drm_pci_register_driver()` wraps `pci_register_driver()` and returns `-ENODEV` when `drm_firmware_drivers_only()` is active. `drm_module_pci_driver()` plugs that wrapper into `module_driver()`. `drm_pci_register_driver_if_modeset()` additionally rejects registration when a deprecated `modeset` parameter is disabled or when firmware-only mode and default modeset policy conflict; `drm_module_pci_driver_if_modeset()` exposes that legacy behavior. `drm_platform_driver_register()` and `drm_module_platform_driver()` provide the platform-bus equivalent.

Control flow: at module init, generated `module_driver()` code calls the DRM wrapper instead of raw bus registration. If policy allows, normal PCI/platform driver registration proceeds; otherwise init fails with `-ENODEV`. Module exit unregisters through the standard bus unregister function.

State and persistence behavior: this header does not own runtime state. It reads global DRM policy and optional driver modeset parameter at module initialization time.

Dependencies and integration points: includes Linux PCI and platform driver APIs plus `drm_drv.h` for `drm_firmware_drivers_only()`. It is used directly in DRM driver module source files instead of `module_pci_driver()` or `module_platform_driver()`.

Risks: each macro replaces explicit `module_init()`/`module_exit()` and can only be used once per module. The `_if_modeset` helper is deprecated and preserves legacy parameter semantics that new drivers should avoid. Firmware-only policy can make a driver appear absent even though the module loaded.

Test signals: module init with firmware-driver-only enabled/disabled, modeset parameter values `0`, `-1`, and enabled, PCI and platform unregister paths, and build coverage for drivers using the macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_of.h -->
## sources/distributed-fs/ceph-client/include/drm/drm_of.h

Purpose: declares Open Firmware/device-tree helpers for DRM display pipelines: CRTC endpoint discovery, component matching/probing, active encoder endpoints, panel/bridge lookup/removal, LVDS dual-link metadata, DSI bus lookup, and data-lane parsing.

Important APIs and types: `enum drm_lvds_dual_link_pixels` describes even/odd pixel ordering across dual LVDS links. Under `CONFIG_OF`, helpers compute CRTC masks from graph ports, find possible CRTCs, add component matches, run component probe, get an encoder's active endpoint, find a panel or bridge by port/endpoint, query LVDS pixel order at source or sink, read LVDS data mapping, and count data lanes from endpoints. Optional DSI support exposes `drm_of_get_dsi_bus()`. `drm_of_panel_bridge_remove()` finds a remote bridge and removes panel bridge wrapping when panel bridge support is enabled. Convenience helpers return active endpoint or port IDs.

Control flow: display drivers parse their DT graph during probe, derive possible CRTC routing masks, match component devices, locate downstream panels/bridges or DSI hosts, and configure LVDS/MIPI lane metadata. On teardown, panel bridge removal follows the remote endpoint and drops references.

State and persistence behavior: helper state is primarily OF node references and returned bridge/panel/host references. Stub implementations return zero or `-EINVAL` when config options are disabled. `drm_of_panel_bridge_remove()` obtains and releases OF node and bridge references within the helper.

Dependencies and integration points: depends on OF graph APIs, component framework, DRM bridge/panel, DRM encoder, MIPI DSI, LVDS bindings, and conditional `CONFIG_OF`, `CONFIG_DRM_PANEL_BRIDGE`, and `CONFIG_DRM_MIPI_DSI`.

Risks: callers must handle stubs on non-OF builds. Device-tree graph port/endpoint numbering errors propagate to wrong routing masks or missing panels. Reference handling around remote nodes and bridges must be balanced. Dual-link LVDS pixel order and lane count validation must match binding limits.

Test signals: OF and non-OF builds, componentized display pipeline probing, panel-vs-bridge lookup, DSI host lookup, active endpoint/port ID helpers, LVDS dual-link even/odd order, data-lane min/max validation, and panel bridge removal on driver unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_of.h -->
