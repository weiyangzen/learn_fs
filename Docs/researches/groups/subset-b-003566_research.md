# subset-b-003566 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gpuvm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gpuvm.c

## Purpose

`drm_gpuvm.c` implements the DRM GPU virtual-address manager. It gives render drivers a common in-kernel model for a GPU VM address space, backed by interval-tree/rb-tree GPU VA nodes (`struct drm_gpuva`) and per-VM/per-GEM object association records (`struct drm_gpuvm_bo`). It also provides the split/merge algorithms used by VM_BIND-style APIs, helpers for dma-resv locking through `drm_exec`, evicted-object validation, fence propagation, and operation-list construction.

## Important APIs, Types, And Functions

The central types are `struct drm_gpuvm`, `struct drm_gpuva`, `struct drm_gpuvm_bo`, `struct drm_gpuva_op`, `struct drm_gpuva_ops`, `struct drm_gpuvm_map_req`, and `struct drm_gpuvm_ops`. Exported lifecycle and locking APIs include `drm_gpuvm_resv_object_alloc()`, `drm_gpuvm_init()`, `drm_gpuvm_put()`, `drm_gpuvm_prepare_vm()`, `drm_gpuvm_prepare_objects()`, `drm_gpuvm_prepare_range()`, `drm_gpuvm_exec_lock()`, `drm_gpuvm_exec_lock_array()`, `drm_gpuvm_exec_lock_range()`, `drm_gpuvm_validate()`, and `drm_gpuvm_resv_add_fence()`.

Object association APIs include `drm_gpuvm_bo_create()`, `drm_gpuvm_bo_put()`, `drm_gpuvm_bo_put_deferred()`, `drm_gpuvm_bo_deferred_cleanup()`, `drm_gpuvm_bo_find()`, `drm_gpuvm_bo_obtain_locked()`, `drm_gpuvm_bo_obtain_prealloc()`, `drm_gpuvm_bo_extobj_add()`, and `drm_gpuvm_bo_evict()`. GPUVA tree/list APIs include `drm_gpuva_insert()`, `drm_gpuva_remove()`, `drm_gpuva_link()`, `drm_gpuva_unlink()`, `drm_gpuva_unlink_defer()`, `drm_gpuva_find_first()`, `drm_gpuva_find()`, `drm_gpuva_find_prev()`, `drm_gpuva_find_next()`, `drm_gpuvm_interval_empty()`, `drm_gpuva_map()`, `drm_gpuva_remap()`, and `drm_gpuva_unmap()`. Split/merge APIs are `drm_gpuvm_sm_map()`, `drm_gpuvm_sm_unmap()`, `drm_gpuvm_sm_map_exec_lock()`, `drm_gpuvm_sm_unmap_exec_lock()`, `drm_gpuvm_sm_map_ops_create()`, `drm_gpuvm_madvise_ops_create()`, `drm_gpuvm_sm_unmap_ops_create()`, `drm_gpuvm_prefetch_ops_create()`, `drm_gpuvm_bo_unmap_ops_create()`, and `drm_gpuva_ops_free()`.

## Control Flow

`drm_gpuvm_init()` initializes the GPUVA rb-tree/list, external-object and evicted-object lists, deferred BO cleanup list, reference count, VM bounds, common reservation object, and optional kernel-reserved GPUVA node. `drm_gpuvm_put()` drops the VM kref; final release removes the reserved node, warns if mappings/lists are still populated, puts the reservation object, and calls the driver's `vm_free` callback.

Locking flows are built around `drm_exec`. `drm_gpuvm_exec_lock()` locks or prepares the VM reservation object first, then every external BO, then optional driver-provided extra objects inside a retry-on-contention loop. Range and array variants narrow or extend the object set. `drm_gpuvm_validate()` walks evicted VM BOs and delegates repair to `ops->vm_bo_validate`; if the VM is protected by its common reservation lock, it uses that lock rather than internal spinlocks.

BO flows preserve the unique tuple `(gpuvm, gem_object)`. Drivers either allocate with `drm_gpuvm_bo_create()` and install with `drm_gpuvm_bo_obtain_locked()`, or use `drm_gpuvm_bo_obtain_prealloc()` for immediate-mode paths that cannot allocate while holding the GEM GPUVA mutex. Mapping insertion validates address/range against the VM bounds and reserved kernel node, rejects overlap in `__drm_gpuva_insert()`, links into both interval tree and ordered list, and takes a VM reference. Link/unlink calls attach individual GPUVA mappings to the VM BO and maintain VM BO references.

The split/merge engine scans existing mappings intersecting a requested map or unmap range. `__drm_gpuvm_sm_map()` emits unmap, remap, and at most one final map callback depending on interval overlap, object equality, and GEM offset contiguity; the `keep` flag tells drivers when backing PTEs can be preserved for delta updates. `__drm_gpuvm_sm_unmap()` emits unmaps or split remaps for partially covered mappings. Operation-list creators reuse those callbacks with allocation-backed list nodes, while exec-lock variants reuse the algorithm with callbacks that only lock touched GEM objects.

## State And Persistence

State is in-memory DRM driver state: the GPUVA interval tree, ordered GPUVA list, optional kernel-reserved node, common reservation GEM object, per-GEM GPUVA lists, per-VM external and evicted object lists, BO deferred cleanup lockless list, krefs, and flags such as immediate/resv-protected mode. Nothing persists beyond the `drm_device`/driver VM lifetime; the source of truth is reconstructed by driver VM_BIND or VM initialization code. Fences are written into locked dma-resv objects through `drm_gpuvm_resv_add_fence()`.

## Dependencies And Integration Points

The file depends on DRM GEM, dma-resv, `drm_exec`, interval-tree helpers, Linux rb/list/llist/kref infrastructure, and driver-supplied `drm_gpuvm_ops`. It is consumed by GPU drivers implementing VM_BIND, sparse resources, page-table update batching, BO eviction/validation, and shared VM reservation objects. It integrates with GEM object's `gpuva` list/mutex and with driver alloc/free callbacks for custom VM BO or operation objects.

## Risks And Edge Cases

Range correctness is critical: overflow and reserved-kernel-node checks protect the VM tree, but callers must still update the GPUVM view after processing split/merge operations before requesting another dependent operation. Deferred cleanup is subtle because GEM GPUVA mutex lifetime and GEM object final put must not overlap incorrectly; `drm_gpuvm_bo_deferred_cleanup()` is required after deferred puts. Immediate-mode callers are warned away from allocating under the GEM GPUVA lock and must use preallocation. `drm_gpuva_find_prev(start)` computes `start - 1`, so invalid zero starts rely on range validation to fail. The operation-list path deep-copies remap substructures; allocation failures must unwind through `drm_gpuva_ops_free()`.

## Test Signals

Useful tests include VM init/fini leak warnings, reserved-range rejection, overlapping insert rejection, exact/partial map replacement, left/right/both-side split remaps, sparse/madvise operation generation, unmap of fully and partially covered ranges, prefetch op creation, BO unmap op creation, external-object locking under both resv-protected and spinlock modes, eviction validation, deferred VM BO cleanup, and fence addition to private versus external objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gpuvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_internal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_internal.h

## Purpose

`drm_internal.h` is the private DRM core header used to share non-UAPI declarations across DRM core compilation units. It centralizes internal interface version constants, forward declarations, feature-dependent stubs, and prototypes for file, PCI, PRIME, managed-resource, vblank, IRQ, auth, sysfs, GEM, debugfs, syncobj, and framebuffer helpers.

## Important APIs, Types, And Functions

The header defines `DRM_IF_MAJOR`, `DRM_IF_MINOR`, and `DRM_IF_VERSION(maj, min)`, which are consumed by SET_VERSION/GET_UNIQUE compatibility paths. It declares `drm_global_mutex`, file lifecycle helpers (`drm_file_alloc()`, `drm_file_free()`), PCI bus-id setup (`drm_pci_set_busid()` or an `-EINVAL` stub), PRIME handle-private helpers, managed-resource release entry points (`drm_managed_release()`, `drmm_add_final_kfree()`), vblank counters/workers, ioctl handlers, auth/master operations, sysfs registration, GEM handle/open/close/vmap helpers, debugfs setup/teardown, syncobj ioctls, and framebuffer debug/print helpers.

Conditional sections provide no-op stubs for disabled `CONFIG_DRM_CLIENT`, `CONFIG_MAGIC_SYSRQ`, `CONFIG_PCI`, and `CONFIG_DEBUG_FS` features. This keeps call sites simple while allowing the configured kernel to compile out optional infrastructure.

## Control Flow

This header has no executable control flow of its own except small inline helpers. `drm_vblank_passed()` compares sequence numbers with 24-bit wrap semantics. `drm_vblank_flush_worker()` and `drm_vblank_destroy_worker()` wrap kthread worker operations. Debugfs and client/sysrq stubs collapse to empty or success-returning functions when their configs are disabled.

## State And Persistence

The header owns no runtime storage. It exposes state owned by other compilation units, such as `drm_global_mutex`, `drm_class`, DRM file private data, GEM object handle state, syncobj state, vblank workers, sysfs minors, and managed-resource lists. Its constants affect persistent userspace ABI behavior for DRM interface version negotiation but do not themselves store data.

## Dependencies And Integration Points

It includes Linux `kthread.h`, `types.h`, and public DRM headers `drm_ioctl.h` and `drm_vblank.h`. It is included by core files such as ioctl, compat ioctl, leasing, managed resources, GEM, sysfs, auth, debugfs, and vblank code. Because it is private to the DRM core, declarations here are integration contracts between DRM internals rather than driver-facing API.

## Risks And Edge Cases

Prototype drift is the main risk: changing a function signature in an implementation without updating this header breaks core builds or silently changes call semantics if casts are involved elsewhere. Config stubs must match real function semantics closely enough that disabled-feature builds remain correct; returning success for debugfs registration is intentional but could hide code that assumes debugfs side effects. `DRM_IF_MINOR` changes affect old libdrm compatibility logic and must be handled cautiously.

## Test Signals

Primary validation is build coverage across config combinations: with and without PCI, debugfs, DRM client, sysrq, syncobj, modeset, and GEM users. Runtime signals come from successful DRM device open/close, sysfs/debugfs registration, vblank handling, PRIME handle conversion, syncobj ioctls, GEM handle lifetimes, and SET_VERSION/GET_UNIQUE behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ioc32.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ioc32.c

## Purpose

`drm_ioc32.c` implements the 32-bit userspace compatibility ioctl layer for DRM core ioctls on 64-bit kernels. It translates legacy pointer-sized structures to native structures for the subset of DRM core ioctls that need explicit marshalling, then forwards handling to `drm_ioctl_kernel()` or `drm_ioctl()`.

## Important APIs, Types, And Functions

The exported entry point is `drm_compat_ioctl()`. Explicit compat handlers include `compat_drm_version()`, `compat_drm_getunique()`, `compat_drm_setunique()`, `compat_drm_getclient()`, `compat_drm_getstats()`, `compat_drm_wait_vblank()`, and x86-only `compat_drm_update_draw()` and `compat_drm_mode_addfb2()`. The file defines 32-bit variants of `drm_version`, `drm_unique`, `drm_client`, `drm_stats`, `drm_wait_vblank`, and x86 packed `drm_update_draw`/`drm_mode_fb_cmd2` structures.

`drm_compat_ioctls[]` maps core ioctl numbers to handlers with `DRM_IOCTL32_DEF()`. Missing entries intentionally fall back to `drm_ioctl()` on the assumption that the ioctl layout is compat-safe.

## Control Flow

`drm_compat_ioctl()` extracts `DRM_IOCTL_NR(cmd)`, bounds-checks against `drm_compat_ioctls[]`, applies `array_index_nospec()`, and either dispatches an explicit compat function or falls back to the normal DRM ioctl path. Handlers copy compact 32-bit structures from userspace, populate native kernel structures with `compat_ptr()` pointer expansion, call the corresponding native DRM core handler through `drm_ioctl_kernel()`, then copy result fields back.

`compat_drm_wait_vblank()` converts request fields into native `union drm_wait_vblank`, calls `drm_wait_vblank_ioctl()`, and copies reply sequence/time fields back even when the native ioctl returns an error. `compat_drm_mode_addfb2()` handles an x86 packed layout by copying fields up to `modifier`, then separately copying the modifier array into the native request before invoking `drm_mode_addfb2()`.

## State And Persistence

This file does not own persistent state. It temporarily stores marshalled ioctl arguments on the kernel stack. Persistent effects are delegated to the native DRM ioctl handlers: version strings, bus IDs, client authentication reporting, vblank waits, and framebuffer creation. The compat dispatch table is static read-only after initialization.

## Dependencies And Integration Points

The file depends on Linux compat pointer helpers, nospec array-index hardening, usercopy helpers, DRM file/device/print headers, `drm_crtc_internal.h`, and `drm_internal.h`. It integrates directly with `drm_ioctl_kernel()` for permission-checked native calls and with the normal `drm_ioctl()` fallback for compatible layouts. Driver-private ioctls are not translated here unless they share normal layouts; drivers with incompatible private ioctls must wrap this path themselves.

## Risks And Edge Cases

The fallback assumption can be wrong for ioctl structs with embedded pointers or different packing, especially driver-private commands. `compat_drm_setunique()` is intentionally dead and returns `-EINVAL`, preserving modern DRM behavior. `compat_drm_getstats()` clears the defunct stats structure instead of querying real stats. Type width truncation is deliberate for old ABI fields such as pid/uid/iocs. The x86-only packed ADD_FB2 handling is architecture-specific; other architectures rely on native compatibility.

## Test Signals

Test with 32-bit userspace on a 64-bit kernel using `DRM_IOCTL_VERSION`, `GET_UNIQUE`, `GET_CLIENT`, `GET_STATS`, `WAIT_VBLANK`, and x86 `MODE_ADDFB2`. Useful negative tests include unsupported SET_UNIQUE, invalid user pointers, short buffers, no explicit compat-table entry fallback, and render-node permission propagation through `drm_ioctl_kernel()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ioc32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ioctl.c

## Purpose

`drm_ioctl.c` is the DRM core ioctl dispatcher and implementation home for several legacy and generic core ioctls. It exposes version/bus-id/client/capability operations, client capability negotiation, no-op/invalid-op helpers for deprecated ioctls, core ioctl permission checks, core ioctl descriptor table, driver-private ioctl dispatch, userspace argument marshalling, and permission flag lookup.

## Important APIs, Types, And Functions

Important exported functions are `drm_getunique()`, `drm_getclient()`, `drm_noop()`, `drm_invalid_op()`, `drm_version()`, `drm_ioctl_kernel()`, `drm_ioctl()`, and `drm_ioctl_flags()`. Important internal helpers are `drm_unset_busid()`, `drm_set_busid()`, `drm_getstats()`, `drm_getcap()`, `drm_setclientcap()`, `drm_setversion()`, `drm_copy_field()`, `drm_validate_value_string()`, `drm_set_client_name()`, and `drm_ioctl_permit()`.

The central table is `drm_ioctls[]`, built with `DRM_IOCTL_DEF()`. It maps core ioctl command numbers to functions and access flags such as `DRM_RENDER_ALLOW`, `DRM_AUTH`, `DRM_MASTER`, and `DRM_ROOT_ONLY`. The table covers version/auth, master, vblank, GEM, PRIME, KMS resource/property/framebuffer/atomic/dumb-buffer operations, syncobj operations, CRTC sequence operations, and DRM lease ioctls.

## Control Flow

Simple core ioctls first marshal user buffers through `drm_ioctl()` and then operate on DRM state. `drm_getunique()` returns the current master's bus ID under `dev->master_mutex`. `drm_setversion()` validates the requested DRM interface and driver versions, updates `dev->if_version`, and for interface minor >= 1 populates the master's bus ID through PCI or `dev->unique`. `drm_getclient()` is hollowed out to report only the current client's authentication state for index zero. `drm_getcap()` and `drm_setclientcap()` implement feature negotiation, with render-safe caps handled before KMS-only caps.

`drm_ioctl()` validates the ioctl type, chooses either a driver-private descriptor from `dev->driver->ioctls` or a core descriptor from `drm_ioctls[]`, hardens the index with `array_index_nospec()`, computes input/output/kernel buffer sizes from the userspace command and the trusted descriptor command, copies input from userspace, zero-extends to the kernel struct size, calls `drm_ioctl_kernel()`, and copies output back. `drm_ioctl_kernel()` updates file ownership for passed file descriptors, rejects unplugged devices, applies `drm_ioctl_permit()`, and invokes the handler.

## State And Persistence

Persistent state touched here includes `drm_master.unique`, `drm_master.unique_len`, `dev->if_version`, per-file capability booleans (`stereo_allowed`, `universal_planes`, `atomic`, `aspect_ratio_allowed`, `writeback_connectors`, `supports_virtualized_cursor_plane`, `plane_color_pipeline`), and `file_priv->client_name`. The ioctl dispatcher itself keeps only stack or temporary heap buffers for ioctl arguments. Capabilities returned from `drm_getcap()` reflect driver feature flags and `mode_config` fields.

## Dependencies And Integration Points

The file depends on Linux usercopy, nospec, PCI device checks, capabilities, and DRM auth, CRTC/KMS, driver, file, print, PRIME, GEM, syncobj, lease, and vblank internals. It is the normal `file_operations.unlocked_ioctl` path for DRM drivers. Driver-private ioctls integrate by publishing `drm_driver.ioctls` and `num_ioctls`; core permission and marshalling behavior applies to both core and private commands.

## Risks And Edge Cases

The GET_UNIQUE/SET_VERSION behavior is constrained by old libdrm open-by-name and open-by-busid semantics; returning a bus ID too early can break old userspace. `drm_set_busid()` does not return `-ENOMEM` if `kstrdup(dev->unique)` fails for non-PCI devices, leaving `unique_len` zero. `drm_ioctl()` copies output even if the handler failed, then reports `-EFAULT` if output copy fails, which can mask the original handler error. Permission flags are central security boundaries: render nodes require `DRM_RENDER_ALLOW`, master ioctls require current master, and root-only ioctls require `CAP_SYS_ADMIN`. The atomic client cap has a special Xorg process-name compatibility rejection. `drm_set_client_name()` rejects non-graphical ASCII and embedded NUL by comparing `strlen()` to the requested length.

## Test Signals

Important tests include ioctl type rejection, invalid core and driver ioctl numbers, stack versus heap argument buffers, zero-extension of shorter user structs, permission failures for render/auth/master/root-only calls, unplugged-device `-ENODEV`, SET_VERSION bus-id behavior on PCI and platform devices, GET_UNIQUE compatibility, GET_CAP values for render-only and KMS drivers, client cap negotiation, SET_CLIENT_NAME validation, syncobj/GEM/PRIME dispatch, lease ioctl dispatch, and driver-private ioctl bounds hardening.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_kms_helper_common.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_kms_helper_common.c

## Purpose

`drm_kms_helper_common.c` is the minimal common module metadata unit for the DRM KMS helper module. It identifies the module authors, description, and license so the helper object can be built and loaded with consistent metadata.

## Important APIs, Types, And Functions

There are no functions, exported symbols, or runtime data structures in this file. The only statements are `MODULE_AUTHOR("David Airlie, Jesse Barnes")`, `MODULE_DESCRIPTION("DRM KMS helper")`, and `MODULE_LICENSE("GPL and additional rights")`.

## Control Flow

There is no control flow. The module macros are compiled into ELF module metadata consumed by the kernel module loader and modinfo tooling.

## State And Persistence

The file owns no mutable state and persists no runtime data. Its metadata persists in the built kernel object/module and can affect module loading policy through the license string.

## Dependencies And Integration Points

The only include is `<linux/module.h>`. The file integrates with the kernel build and module-information infrastructure rather than with DRM runtime paths. It is expected to be linked with the broader DRM KMS helper module objects.

## Risks And Edge Cases

Risk is limited to metadata accuracy. A wrong license string can affect GPL-only symbol availability or taint/module policy. A missing description/author would reduce diagnostics but not change runtime behavior.

## Test Signals

Build the DRM KMS helper module or built-in object and inspect `modinfo`/module metadata. Runtime signal is successful loading of the KMS helper module when configured as a module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_kms_helper_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_lease.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_lease.c

## Purpose

`drm_lease.c` implements DRM KMS leasing. Leasing lets a DRM master create another master that controls a subset of mode-setting objects, used by workflows such as VR compositors that need direct ownership of specific connectors/CRTCs/planes while the main compositor owns the rest. The code tracks lessor/lessee relationships, validates lease object sets, filters object visibility, creates lease file descriptors, lists/get/revokes leases, and destroys lease state.

## Important APIs, Types, And Functions

The key type is `struct drm_master`, specifically its `lessor`, `lessees`, `lessee_list`, `lessee_id`, `lessee_idr`, and `leases` fields. Important functions include `drm_lease_owner()`, `_drm_lease_held()`, `drm_lease_held()`, `drm_lease_filter_crtcs()`, `drm_lease_destroy()`, `drm_lease_revoke()`, `drm_mode_create_lease_ioctl()`, `drm_mode_list_lessees_ioctl()`, `drm_mode_get_lease_ioctl()`, and `drm_mode_revoke_lease_ioctl()`. Internal helpers include `_drm_find_lessee()`, `_drm_lease_held_master()`, `_drm_has_leased()`, `drm_lease_create()`, `_drm_lease_revoke()`, `validate_lease()`, and `fill_object_idr()`.

`drm_lease_idr_object` is a dummy non-NULL IDR payload used to represent membership in a lease set; actual mode objects are resolved through `dev->mode_config.object_idr`.

## Control Flow

Lease creation begins in `drm_mode_create_lease_ioctl()`. It requires `DRIVER_MODESET`, validates flags against `O_CLOEXEC | O_NONBLOCK`, obtains the current master, rejects sub-leasing, copies object IDs from userspace, and builds an IDR with `fill_object_idr()`. That helper resolves each object through `drm_mode_object_find()`, rejects non-leaseable object types, requires at least a CRTC and connector plus a plane when universal planes are enabled, adds IDs to the lease IDR, and auto-adds primary/cursor planes for leased CRTCs when universal planes are not enabled. The ioctl then allocates a file descriptor, creates the lessee master with `drm_lease_create()`, clones the lessor file, swaps the cloned file's master to the lessee, marks it master/authenticated, returns fd and lessee ID, and installs the fd.

`drm_lease_create()` validates under `mode_config.idr_mutex` that every requested object exists and has not already been leased by another lessee, assigns a lessee ID in the owner `lessee_idr`, links the lessee into the lessor list, and transfers ownership of the lease IDR. Lease queries and filtering also lock `idr_mutex`: `drm_lease_held()` checks membership for lessees and returns true for owners; `drm_lease_filter_crtcs()` remaps CRTC bitmasks to only visible CRTCs. Revocation empties lease IDRs for a lessee tree without destroying the master object, preserving references. Destruction removes a master from the owner IDR and lessor list and emits a sysfs lease event.

## State And Persistence

Leasing state persists in DRM master objects for as long as the relevant file descriptors/masters exist. Owners have `lessor == NULL` and an IDR of lessees. Lessees store leased object IDs in `leases` and reference their lessor. Revocation empties `leases`, while close/destruction removes the lessee from IDRs/lists and drops lessor references. Lease visibility affects subsequent KMS ioctl behavior elsewhere by making non-leased objects appear unavailable.

## Dependencies And Integration Points

The file depends on Linux file descriptor helpers, usercopy, IDR/list locking, DRM auth/master/file infrastructure, CRTC/mode object helpers, sysfs lease events, and core ioctl dispatch through declarations in `drm_crtc_internal.h` and `drm_internal.h`. KMS object lookup and object-type leaseability are provided by the mode configuration layer. The core ioctl table in `drm_ioctl.c` exposes the create/list/get/revoke lease ioctls with `DRM_MASTER` permissions.

## Risks And Edge Cases

Sub-leases are explicitly rejected, so the conceptual tree is limited even though revocation walks generically. Lease validation requires a connector and CRTC, and conditionally a plane; unusual users requesting non-display objects or incomplete sets receive `-EINVAL`. Duplicate IDs in the lease request fail through `idr_alloc()` with `-EEXIST`. `drm_mode_create_lease_ioctl()` assumes `drm_file_get_master()` returns a valid master and must unwind fd, IDR, lessee, and cloned file references exactly. Empty leases are allowed when `object_count == 0`, producing a lessee with no controllable objects. Listing lessees omits revoked leases by checking for non-empty lease IDRs.

## Test Signals

Test create/list/get/revoke using valid connector/CRTC/plane sets, duplicate IDs, invalid object IDs, non-leaseable object types, missing connector/CRTC/plane combinations, universal-plane on/off behavior, attempted sub-leases, object already leased to another lessee, empty leases, close-time destruction, sysfs lease uevents, CRTC mask filtering for lessees, and KMS ioctls against leased versus non-leased objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_lease.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_managed.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_managed.c

## Purpose

`drm_managed.c` implements DRM-device-managed resources, modeled after devres but tied to `struct drm_device` lifetime rather than the physical device lifetime. It lets DRM drivers register cleanup actions and allocations that are released on the final `drm_dev_put()`, which matters because DRM devices can outlive physical devices while userspace still holds file handles.

## Important APIs, Types, And Functions

Internal resource records are `struct drmres_node` and `struct drmres`; `struct drmres` embeds metadata plus aligned payload storage. Exported or internal entry points are `drm_managed_release()`, `drmm_add_final_kfree()`, `__drmm_add_action()`, `__drmm_add_action_or_reset()`, `drmm_release_action()`, `drmm_kmalloc()`, `drmm_kstrdup()`, `drmm_kfree()`, `__drmm_mutex_release()`, and `__drmm_workqueue_release()`. Internal helpers are `free_dr()`, `alloc_dr()`, `del_dr()`, and `add_dr()`.

## Control Flow

`__drmm_add_action()` allocates a resource node that stores an optional data pointer and release callback, records a constant-duplicated name for debug, and pushes the node to the front of `dev->managed.resources` under `dev->managed.lock`. `__drmm_add_action_or_reset()` adds the action and immediately invokes it if allocation/registration fails. `drmm_kmalloc()` allocates a resource node with payload bytes and no release callback, then returns the payload. `drmm_kstrdup()` layers string duplication on top of `drmm_kmalloc()`.

`drm_managed_release()` walks the resources list in list order with safe iteration, logs each resource, invokes callbacks with either the stored pointer or NULL, removes each node, and frees metadata/payload. Because `add_dr()` uses `list_add()`, release happens in reverse registration order. `drmm_release_action()` searches from the tail for a matching action/data pair, removes it under the spinlock, calls the action immediately, and frees the node. `drmm_kfree()` searches for the allocation payload, removes the node, and frees it early.

## State And Persistence

State lives in `dev->managed.resources`, protected by `dev->managed.lock`, and in `dev->managed.final_kfree`. Resources persist until early release/free or final DRM device release. The payload for `drmm_kmalloc()` is inside the resource object; action resources may store a caller-provided pointer. Resource names are stored with `kstrdup_const()` for debug output.

## Dependencies And Integration Points

The implementation depends on Linux list, spinlock, slab, node-aware allocation, overflow checking, and DRM device/print infrastructure. It integrates with `devm_drm_dev_alloc()` and final DRM device teardown paths through `drm_managed_release()`. Public wrappers/macros in `drm_managed.h` call the double-underscore functions here, supplying action names. Mutex and workqueue release helpers support managed initialization wrappers for common kernel primitives.

## Risks And Edge Cases

`drm_managed_release()` walks the list without taking `dev->managed.lock`, so it assumes final release has excluded concurrent registration/removal. `drmm_release_action()` matches only by callback and optional data; if multiple same-callback resources use NULL data, it releases the last matching node. `drmm_kfree()` warns and returns if the pointer was not allocated by `drmm_kmalloc()` for that device. `drmm_add_final_kfree()` uses pointer-range `WARN_ON()` checks to ensure the embedded `drm_device` lives inside the final allocation container; misuse can leave final freeing incorrect. Allocation size overflow is explicitly checked before adding header and payload sizes.

## Test Signals

Test managed allocations and actions for reverse-order release, early `drmm_kfree()`, early `drmm_release_action()`, add-action-or-reset failure behavior, managed string duplication, mutex/workqueue managed cleanup, final release with many resources, invalid early-free warning paths, and concurrent registration/removal during normal device lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_managed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mipi_dbi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mipi_dbi.c

## Purpose

`drm_mipi_dbi.c` provides DRM helpers for MIPI Display Bus Interface LCD controllers, especially small SPI-attached panels using Type C option 1 or option 3. It wraps MIPI DCS command I/O, framebuffer format conversion and dirty flushing, simple CRTC/plane/connector helper callbacks, power/reset sequencing, SPI transfer encoding, and debugfs command access.

## Important APIs, Types, And Functions

The primary public structures are declared in `drm_mipi_dbi.h`, especially `struct mipi_dbi` and `struct mipi_dbi_dev`. Exported command/display helpers include `mipi_dbi_command_read()`, `mipi_dbi_command_buf()`, `mipi_dbi_command_stackbuf()`, `mipi_dbi_buf_copy()`, `mipi_dbi_hw_reset()`, `mipi_dbi_display_is_on()`, `mipi_dbi_poweron_reset()`, `mipi_dbi_poweron_conditional_reset()`, `mipi_dbi_spi_cmd_max_speed()`, `mipi_dbi_spi_init()`, `mipi_dbi_spi_transfer()`, and `mipi_dbi_debugfs_init()`.

DRM helper callbacks include `drm_mipi_dbi_crtc_helper_mode_valid()`, `drm_mipi_dbi_plane_helper_atomic_check()`, `drm_mipi_dbi_plane_helper_atomic_update()`, `drm_mipi_dbi_crtc_helper_atomic_check()`, `drm_mipi_dbi_crtc_helper_atomic_disable()`, `drm_mipi_dbi_connector_helper_get_modes()`, and `drm_mipi_dbi_dev_init()`. Static helpers cover DCS read-command allowlisting, address-window programming, dirty updates, blanking, rotation, Type C option 1/3 command paths, 9-bit emulation, and debugfs file operations.

## Control Flow

Drivers first call `mipi_dbi_spi_init()` for SPI panels. It ensures a DMA mask exists for GEM DMA use, records the SPI device, installs the DCS read-command table, initializes defaults for write-memory bits-per-word, selects Type C option 3 when a D/C GPIO is supplied or Type C option 1 otherwise, allocates the 9-bit staging buffer for option 1, sets byte-swapping when option 3 lacks 16-bpw support, and initializes the command mutex. `drm_mipi_dbi_dev_init()` then allocates a transmit buffer, copies/rotates the fixed display mode, records rotation and pixel format, and adjusts write-memory bpw for RGB888.

Command submission uses `mipi_dbi_command_buf()`, which duplicates the command byte into a DMA-safe buffer, serializes through `dbi->cmdlock`, and calls the selected `dbi->command` backend. Read commands are restricted to `mipi_dbi_dcs_read_commands`. Option 1 sends the D/C bit as a ninth SPI bit, using native 9-bpw transfers when supported or packing 8 data bytes into 9 bytes otherwise. Option 3 toggles the D/C GPIO and uses locked SPI bus transfers for command and data phases. Read paths cap speed at 2 MHz or half max speed and handle special Nokia-style dummy-clock reads for display ID/status.

Framebuffer flushing flows from `drm_mipi_dbi_plane_helper_atomic_update()`: damage is merged, `mipi_dbi_fb_dirty()` copies/converts the damaged rectangle when needed, sets column/page address windows with left/top offsets, computes transfer length from the destination format, and writes memory with `MIPI_DCS_WRITE_MEMORY_START`. Disable either turns off backlight or blanks display memory, then disables regulators. Power-on enables regulators, optionally skips reset if the display can be verified already on, performs hardware and DCS soft reset, and waits per reset path.

## State And Persistence

Runtime state lives in `mipi_dbi` and `mipi_dbi_dev`: SPI pointer, D/C and reset GPIOs, command callback, command mutex, DCS read table, write-memory bpw, byte-swap flag, 9-bit staging buffer, display mode, rotation, pixel format, offsets, transmit buffer, backlight, and regulators. No display contents are persisted by this file; framebuffer memory is copied to panel GRAM during dirty updates. Power state is external in regulators, GPIOs, backlight, and the panel controller.

## Dependencies And Integration Points

The file depends on Linux SPI, GPIO, regulator, backlight, debugfs, delay, module infrastructure, DRM atomic helpers, damage helpers, format conversion helpers, GEM framebuffer CPU access, fixed-mode helpers, and MIPI DCS command definitions. It integrates with tiny DRM panel drivers that embed `mipi_dbi_dev`, simple display pipelines, shadow-plane state, debugfs minor initialization, and SPI controller capabilities (`bits_per_word`, max transfer size, max speed).

## Risks And Edge Cases

Read support for Type C option 1 without native 9-bpw SPI is explicitly unimplemented. `mipi_dbi_command_is_read()` scans until a zero sentinel but caps at 255 entries; malformed read-command arrays without a sentinel can still stop at the cap. `mipi_dbi_fb_dirty()` directly uses `src->vaddr` for a full-frame fast path with a TODO about mapping abstraction, so non-vaddr iosys maps would be unsafe there. `mipi_dbi_spi_transfer()` aligns max chunks down to a multiple of two; a controller reporting a max transfer size below two could make progress impossible. Power-on conditional reset returns `1` for already-on displays, so callers must treat positive return as non-error. Debugfs command writes accept at most 64 parameters and expose raw panel commands to privileged debugfs users.

## Test Signals

Test with Type C option 1 native 9-bpw, option 1 emulated 9-bit writes, option 3 with and without 16-bpw support, RGB565/RGB888/XRGB8888 framebuffers, byte-swapped RGB565, partial damage and full-frame updates, rotated modes at 0/90/180/270 and invalid rotations, regulator enable/disable failures, hardware and software reset timing, conditional bootloader-on detection through GET_POWER_MODE, debugfs read/write commands, SPI max-transfer chunking, unsupported read paths, and panel disable blanking/backlight behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mipi_dbi.c -->
