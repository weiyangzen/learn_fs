# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_drv.h

## Purpose
This is the central private header for the vmwgfx driver. It defines driver identity/version constants, VMware SVGA resource limits, private TTM placement IDs, core per-file/per-device/resource structures, inline hardware accessors, shader model helpers, FIFO/register helpers, and cross-module function prototypes.

## Important APIs, types, and definitions
- Driver constants include `VMWGFX_DRIVER_NAME`, version `2.21.0`, static FIFO size, display-unit count, initial mode minimums, and SVGA2/SVGA3 PCI IDs.
- Resource and placement IDs define vmwgfx-specific TTM placements (`VMW_PL_GMR`, `VMW_PL_MOB`, `VMW_PL_SYSTEM`) and TTM object resource classes.
- `struct vmw_fpriv` stores per-open TTM object file state plus whether userspace is guest-backed aware.
- `struct vmw_resource` is the base hardware resource with kref, device id, guest memory attachment, dirty/coherency flags, pin count, MOB tree node, LRU/binding list nodes, and vtable/destructor callbacks.
- `struct vmw_surface_metadata` and `struct vmw_surface` describe legacy and guest-backed surfaces, including cursor snooper state.
- `struct vmw_fifo_state` tracks FIFO reservation buffers, capabilities, mutex, and rwsem.
- `struct vmw_dma_map_mode`, `struct vmw_sg_table`, `struct vmw_piter`, and `struct vmw_ttm_tt` describe DMA/TTM backing details for GMR/MOB bindings.
- `struct vmw_sw_context` carries execbuf validation state, resource caches, relocation lists, query state, staged bindings, command-managed resources, and validation context.
- `struct vmw_private` is the per-device root object embedding `struct drm_device` and holding PCI mappings, capability/state registers, memory limits, KMS/overlay pointers, locks, IDRs, wait queues, fence manager, FIFO/cmdbuf managers, devcaps, PM state, query BOs, resource LRUs, DMA mode, object tables, mksstat pages, and VKMS fields.
- Inline helpers include `vmw_priv()`, `vmw_fpriv()`, `vmw_is_svga_v3()`, `vmw_write()`, `vmw_read()`, shader-model predicates, `vmw_fifo_caps()`, `vmw_is_cursor_bypass3_enabled()`, FIFO memory read/write, fence read/write, IRQ status read/write, and shader type validation.
- The remainder of the header declares subsystem entry points for GMR, user objects, resources, GEM, ioctl, FIFO, execbuf, IRQ/waits, KMS, overlay, GMR ID/system managers, PRIME, MOB/object tables, contexts, surfaces, shaders, streamoutput, command-buffer resources, cotables, command buffer manager, CPU blits, host messaging/mksstat, dirty tracking, and BO VM faults.

## Control flow and integration
Most vmwgfx `.c` files include this header to share `struct vmw_private` and subsystem prototypes. Probe code initializes the fields defined here, ioctl/open paths allocate `vmw_fpriv`, execbuf code uses `vmw_sw_context`, resource-specific modules embed `vmw_resource`, KMS/surface code uses `vmw_surface` and snooper fields, and low-level register/FIFO users call the inline accessors. The header is therefore the compile-time integration point between Linux DRM/TTM frameworks and VMware SVGA device abstractions.

## State and persistence behavior
The structures defined here are the main persistence model for the driver. `vmw_private` lasts for the DRM device lifetime. `vmw_fpriv` lasts for each DRM file. `vmw_resource` derivatives are kref-counted and may be pinned, on LRU lists, dirty, or attached to guest memory. `vmw_sw_context` is reused around command submission and owns transient validation allocations. Inline accessors enforce serialized SVGA2 I/O-port register access with `hw_lock`, while SVGA3 uses MMIO directly. FIFO memory helpers use `READ_ONCE`/`WRITE_ONCE` and assert they are not used on SVGA3.

## Dependencies and integration points
The header depends on Linux suspend/sync/hashtable APIs, DRM auth/device/file/print/rect APIs, TTM execbuf/TT/placement/BO APIs, vmwgfx fence/register/validation headers, TTM object support, and the vmwgfx UAPI header. Because it declares nearly every internal subsystem boundary, changes here have broad rebuild and ABI-adjacent impact even when no UAPI structs change.

## Risks and edge cases
- `struct vmw_private` is large and shared widely; adding fields without clear ownership can create locking or lifetime ambiguity.
- Register helpers take `hw_lock` only for SVGA2 indexed I/O. Callers that need multi-register atomicity must provide higher-level locking, as cursor code does with `cursor_lock`.
- FIFO memory helpers `BUG_ON(vmw_is_svga_v3())`; any SVGA3 caller using legacy FIFO memory access will crash.
- `vmw_surface_unreference()` assumes the input pointer is non-null; callers must guard null pointers.
- Several inline helpers expose raw pointers or unchecked array indexes, such as `vmw_devcap_get()` in the companion header and resource conversion helpers. Callers must enforce capability and bounds invariants.
- Include order is delicate: the file notes that `vmwgfx_drm.h` must be last due to UAPI dependency issues.

## Test signals
Good coverage includes build tests across SVGA2/SVGA3 and CONFIG_COMPAT/MKSSTATS variants, sparse/lockdep checks around register and resource locks, runtime exercising of FIFO versus MMIO paths, resource create/destroy with dirty tracking, PRIME/GEM import-export, execbuf validation, KMS cursor/present paths, hibernation restore, and debugfs resource manager creation for all enabled memory domains.
