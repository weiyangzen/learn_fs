# Research group subset-b-003674

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/mm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/mm.c

### Purpose
`mm.c` implements Nouveau's small internal range allocator for GPU-visible address spaces and heaps. It tracks ordered allocation nodes, separate free-list membership, heap identity, allocation type, block alignment, and explicit holes between appended regions.

### Important APIs, types, and functions
The public API is `nvkm_mm_init()`, `nvkm_mm_fini()`, `nvkm_mm_head()`, `nvkm_mm_tail()`, `nvkm_mm_free()`, and `nvkm_mm_dump()`. The state comes from `struct nvkm_mm` and `struct nvkm_mm_node` in `core/mm.h`. Internal helpers `region_head()` and `region_tail()` split a free node from the front or back while preserving node-list and free-list order.

### Control flow
`nvkm_mm_init()` initializes a new allocator or appends a contiguous later heap, inserting a `NVKM_MM_TYPE_HOLE` node if the next heap begins after the previous region. `nvkm_mm_head()` scans the free list forward and returns the first suitable aligned range. `nvkm_mm_tail()` scans backward and returns the highest suitable range. Both clamp usable starts/ends to `block_size` boundaries when adjacent nodes have different types, split off alignment slack, mark the allocated node with the caller's type, and remove it from the free list. `nvkm_mm_free()` merges with adjacent free nodes before re-inserting the resulting node into the free list in offset order.

### State and persistence behavior
Allocator state is purely in memory. The node list is the authoritative ordered map, while `mm->free` contains only nodes whose type is `NVKM_MM_TYPE_NONE`. `heap_nodes` counts real heap regions and is used by `nvkm_mm_fini()` to detect leaked allocations; holes are ignored. Allocated nodes can be chained by users through `node->next`, but this allocator itself returns contiguous nodes with `next = NULL`.

### Dependencies
The file depends on Linux list primitives, `kzalloc_obj`/`kmalloc_obj`, `roundup()`, `rounddown()`, `min()`, and Nouveau's type constants from `core/mm.h`.

### Integration points
It is used by Nouveau memory managers that need simple range accounting for VRAM, instance memory, GPU objects, and related suballocators. Callers must serialize access externally; there is no lock in `struct nvkm_mm`.

### Risks
The allocator assumes power-of-two nonzero alignment because it builds `mask = align - 1`. Incorrect external locking can corrupt both lists. Boundary rounding around unlike typed neighbors can unexpectedly reduce usable space. `nvkm_mm_fini()` returns `-EBUSY` if any non-hole allocations remain, making leak cleanup visible during driver teardown.

### Test signals
Useful signals are allocation/free stress tests with head and tail placement, heap-specific allocation, alignment edge cases, adjacent free-node coalescing, appended heaps with holes, fini leak detection, and GPU object allocation paths that exercise this allocator during device init and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/object.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/object.c

### Purpose
`object.c` implements the base NVKM object model: client-visible handles, object lookup/removal/insertion, method and notification dispatch, map/bind hooks, hierarchical init/fini/destroy ordering, and default object construction.

### Important APIs, types, and functions
The central type is `struct nvkm_object`, driven by `struct nvkm_object_func` callbacks. Public functions include `nvkm_object_search()`, `nvkm_object_insert()`, `nvkm_object_remove()`, `nvkm_object_mthd()`, `nvkm_object_ntfy()`, `nvkm_object_map()`, `nvkm_object_unmap()`, `nvkm_object_bind()`, `nvkm_object_init()`, `nvkm_object_fini()`, `nvkm_object_dtor()`, `nvkm_object_del()`, `nvkm_object_ctor()`, `nvkm_object_new_()`, and `nvkm_object_new()`.

### Control flow
Client objects live in an rb-tree keyed by the `object` handle and protected by `client->obj_lock`. Search with handle zero returns the client's root object. Lifecycle is hierarchical: init runs the object callback first, then children in forward list order; fini runs children in reverse order before the object callback; destroy deletes children, unmaps, calls the type destructor, unreferences the backing engine, removes from client lookup, unlinks from its parent tree, and frees memory.

### State and persistence behavior
Objects persist until `nvkm_object_del()` deletes them. They keep client, engine reference, oclass, handle, rb-tree node, and parent/child list state. Suspend fini has rollback logic: if a child or object fails during suspend/runtime suspend, already-finished objects are reinitialized to restore operational state.

### Dependencies
The file depends on `core/object.h`, client locking and rb-tree state from `core/client.h`, engine references from `core/engine.h`, NVIF logging helpers, Linux rb-tree/list primitives, and kernel time helpers for debug timing.

### Integration points
The object model underpins NVIF user objects, engine classes, events, GPU object binding, method dispatch, memory mapping, and child class enumeration. Engine implementations provide `bind`, `map`, `mthd`, `sclass`, and `uevent` callbacks through this common layer.

### Risks
Lifetime ordering is the main risk. A destructor that returns a different allocation pointer must still be compatible with the final `kfree(*pobject)`. Missing callback checks return `-ENODEV`, so callers must distinguish unsupported operations from object errors. Failing to remove objects from the rb-tree or child list can leave stale handles. Init/fini rollback must remain symmetrical to avoid partially initialized hardware after suspend failures.

### Test signals
Good coverage comes from NVIF object create/destroy tests, duplicate handle insertion rejection, lookup under concurrent client access, object tree init/fini failure injection, suspend/resume rollback, and bind/map/unmap paths for engine classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/oproxy.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/oproxy.c

### Purpose
`oproxy.c` implements an NVKM object proxy that exposes the standard object callback surface while delegating most behavior to another wrapped `struct nvkm_object`. It lets a wrapper add before/after lifecycle hooks around an underlying object.

### Important APIs, types, and functions
The exported constructors are `nvkm_oproxy_ctor()` and `nvkm_oproxy_new_()`. The callback table `nvkm_oproxy_func` implements `dtor`, `init`, `fini`, `mthd`, `ntfy`, `map`, `unmap`, `bind`, `sclass`, and `uevent`. Wrapper-specific behavior is supplied by `struct nvkm_oproxy_func` arrays `init[2]`, `fini[2]`, and `dtor[2]`.

### Control flow
Method, notification, map, bind, subclass, and uevent calls forward to `oproxy->object`. Init runs pre-hook, underlying object init, then post-hook. Fini runs pre-hook, underlying object fini, then post-hook, returning errors only during suspend-style operations. Destruction runs pre-dtor hook, deletes the underlying object through `nvkm_object_del()`, then runs post-dtor hook.

### State and persistence behavior
The proxy owns a base `nvkm_object`, a function table pointer, and the wrapped object pointer. It does not clone underlying object state; it forwards to the live child. `nvkm_oproxy_unmap()` tolerates a missing wrapped object and returns success, which matters during teardown.

### Dependencies
It depends on `core/oproxy.h` and the base object APIs from `core/object.h`. The wrapped object must already implement the relevant callbacks.

### Integration points
Proxy objects integrate with the same NVIF object tree and handle model as normal objects. They are useful where a class needs to adapt lifecycle behavior without reimplementing method, map, bind, notification, or event forwarding.

### Risks
Most callbacks assume `oproxy->object` is valid; only `unmap` checks for NULL. Constructor users must assign the wrapped object before any forwarded operation. Init/fini hook failures can leave the wrapper and wrapped object initialized to different depths. `sclass` rewrites `oclass->parent` to the wrapped object, so child object constructors depend on that parent substitution.

### Test signals
Test with proxy creation over a real object, forwarded method/map/bind/uevent calls, init and fini hook failure injection, destruction of proxies with and without an underlying object, and child class enumeration through the proxy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/oproxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/option.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/option.c

### Purpose
`option.c` parses Nouveau's comma-separated configuration and debug option strings. It provides string, boolean, numeric, and debug-level extraction for module and per-subdevice configuration.

### Important APIs, types, and functions
The exported helpers are `nvkm_stropt()`, `nvkm_boolopt()`, `nvkm_longopt()`, and `nvkm_dbgopt()`. Debug parsing maps textual levels to `NV_DBG_FATAL`, `NV_DBG_ERROR`, `NV_DBG_WARN`, `NV_DBG_INFO`, `NV_DBG_DEBUG`, `NV_DBG_TRACE`, `NV_DBG_PARANOIA`, and `NV_DBG_SPAM`.

### Control flow
`nvkm_stropt()` scans `name=value` pairs separated by commas or equal signs and returns the value span plus length for a matching option. `nvkm_boolopt()` uses that span to accept common true/false words while preserving the supplied default on unknown values. `nvkm_longopt()` duplicates the value substring, parses it with `kstrtol(..., base 0)`, and preserves the default on parse failure. `nvkm_dbgopt()` scans a debug string with optional `subsystem=level` scoping and returns the current default level after applying matching tokens.

### State and persistence behavior
The file is stateless. It reads immutable option strings and returns parsed values. `nvkm_longopt()` allocates a temporary copy of a value and frees it before returning.

### Dependencies
It depends on `core/option.h`, `core/debug.h`, kernel string helpers, `kstrndup()`, `kstrtol()`, and `CONFIG_NOUVEAU_DEBUG_DEFAULT`.

### Integration points
Device construction uses `nvkm_longopt()` for development chipset override and `nvkm_boolopt()` for unsupported-chipset enabling. Subdevice construction uses `nvkm_dbgopt()` to set per-subdevice log verbosity. Other Nouveau components use these helpers for module option parsing without duplicating scanner logic.

### Risks
The scanner is simple and treats comma/equal delimiters specially; option values cannot contain those characters. Unknown boolean strings silently keep the old value. Debug parsing has a mode flag that changes after scoped entries, so malformed strings can broaden or narrow the effect of later tokens.

### Test signals
Useful tests cover empty strings, missing values, repeated options, mixed case names and values, scoped debug strings, numeric bases accepted by `kstrtol`, and malformed option strings that should leave defaults intact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/option.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/ramht.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/ramht.c

### Purpose
`ramht.c` implements Nouveau's RAMHT handle table helper for older FIFO/channel hardware. It stores channel/handle to GPU object instance bindings in both CPU-side metadata and a GPU object backing table.

### Important APIs, types, and functions
The API consists of `nvkm_ramht_new()`, `nvkm_ramht_del()`, `nvkm_ramht_insert()`, `nvkm_ramht_remove()`, and `nvkm_ramht_search()`. Internal helpers are `nvkm_ramht_hash()` and `nvkm_ramht_update()`. State is held in `struct nvkm_ramht` and `struct nvkm_ramht_data`.

### Control flow
`nvkm_ramht_new()` allocates a variable-sized CPU table, initializes every entry with `chid = -1`, computes hash bits from entry count, and allocates the GPU object backing store. Insert rejects duplicate channel/handle pairs, probes linearly from the XOR hash, binds the object into a small context GPU object when supported, computes the instance address for pre/post NV50 hardware, writes handle/context dwords into the RAMHT GPU object, and returns a one-based cookie. Remove converts the cookie back to an index and clears the entry via `nvkm_ramht_update()` with no object.

### State and persistence behavior
Entries persist in `ramht->data` and in the GPU object until removed or the whole table is deleted. Per-entry bound instance GPU objects are destroyed before replacement. The table does not compact or rehash; deletion marks slots empty by setting `chid = -1`.

### Dependencies
The file depends on `core/ramht.h`, `core/engine.h`, `core/object.h`, GPU object allocation/map/write helpers, `order_base_2()`, `vzalloc()`, and `vfree()`.

### Integration points
FIFO/channel setup uses RAMHT entries to let hardware resolve object handles to engine contexts. It integrates with `nvkm_object_bind()` so engine object classes can provide hardware-specific context records.

### Risks
Hash/probe behavior depends on table size being a power-of-two-compatible byte size. The `addr` argument shifts instance addresses into caller-specified context fields; wrong values corrupt RAMHT entries. The code has no internal lock, so channel/object management must serialize access. Binding returns `-ENODEV` for objects with no bind callback and is treated as a valid unbound object, which callers must expect.

### Test signals
Exercise duplicate insert, full-table `-ENOSPC`, search after wraparound probing, remove/reinsert of the same slot, engine objects with and without bind callbacks, and hardware channel creation on G8x/NV50-era GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/ramht.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/subdev.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/subdev.c

### Purpose
`subdev.c` implements the common lifecycle, reference management, logging identity, and callback dispatch for NVKM subdevices and engines embedded in a device.

### Important APIs, types, and functions
Key APIs include `nvkm_subdev_intr()`, `nvkm_subdev_info()`, `nvkm_subdev_preinit()`, `nvkm_subdev_oneinit()`, `nvkm_subdev_init()`, `nvkm_subdev_fini()`, `nvkm_subdev_ref()`, `nvkm_subdev_unref()`, `nvkm_subdev_del()`, `nvkm_subdev_disable()`, `__nvkm_subdev_ctor()`, and `nvkm_subdev_new_()`. `nvkm_subdev_type[]` is generated from `core/layout.h`.

### Control flow
Construction records the device, type, instance, generated name, debug level, initial refcount, and device list membership. `preinit`, `oneinit`, `init`, and `fini` dispatch optional callbacks with timing and logging. `oneinit` is one-shot. `init` is skipped when already enabled or when no users hold references. `fini` marks the subdevice disabled and resets it through MC. Ref/unref transitions call init on first reference and fini when the final reference drops.

### State and persistence behavior
Each subdevice keeps a refcount, mutex, enabled flag, interrupt handle, list node, `pself` backpointer, and oneinit flag. The device owns the subdevice list. `nvkm_subdev_disable()` nulls the owning device pointer slot and deletes the matching subdevice.

### Dependencies
It depends on `core/subdev.h`, `core/device.h`, option parsing for debug levels, and MC reset support from `subdev/mc.h`.

### Integration points
Every NVKM subdevice and engine constructor calls this layer, and `device/base.c` drives these lifecycle hooks during device bring-up, suspend, runtime suspend, and teardown. Logging macros in `subdev.h` depend on the debug level set here.

### Risks
Reference transitions must hold `use.mutex` correctly; otherwise init/fini can race with users. Constructors add the subdevice to the device list before later setup finishes, so failure cleanup must delete partially built subdevices. `nvkm_subdev_fini()` ignores non-suspend callback failures after logging, which is intentional for poweroff but can hide shutdown errors. MC reset after fini is a hardware-visible side effect.

### Test signals
Use refcount transition tests, bind/unbind or module unload, suspend and runtime-suspend failure injection, oneinit idempotence checks, debug option parsing per subdevice name, and interrupt callback smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/subdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/uevent.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/uevent.c

### Purpose
`uevent.c` implements client-visible NVIF event objects. It wraps an `nvkm_event_ntfy` subscription in an NVKM object and exposes allow/block methods so userspace can control event delivery.

### Important APIs, types, and functions
The file defines private `struct nvkm_uevent` with base object, parent object, optional callback, wait flag, event notification, and atomic `allowed` state. Public functions are `nvkm_uevent_new()` and `nvkm_uevent_add()`. Object methods include `NVIF_EVENT_V0_ALLOW` and `NVIF_EVENT_V0_BLOCK`.

### Control flow
Creation validates versioned `nvif_event_args`, constructs the object, stores the parent and wait mode, then delegates to the parent object's `uevent` callback to bind a concrete event source. `nvkm_uevent_add()` adds the notifier to an event, stores an optional delivery callback, and rejects reuse. Allow/block methods update the notifier and mirror the state in `allowed`. Fini blocks delivery; init re-allows delivery only if `allowed` was set before fini.

### State and persistence behavior
The event object's allowed state persists across object init/fini cycles through an atomic flag. The notifier remains attached until destructor calls `nvkm_event_ntfy_del()`. Delivery either calls the per-event `nvkm_uevent_func` or falls back to `client->event()` with the event object's handle.

### Dependencies
It depends on `core/event.h`, `core/client.h`, NVIF event ABI headers `if000e.h`, and the base object system.

### Integration points
Any NVKM object with a `uevent` callback can create a user event object. This bridges kernel event sources to the NVIF client event callback path and participates in object lifecycle ordering.

### Risks
`nvkm_uevent_add()` warns and returns `-EBUSY` if called twice on one object. Version/size mismatches return `-ENOSYS`. Allow/block must stay synchronized with suspend/fini to avoid delivering events when the object is inactive. Parent `uevent` callbacks must fully initialize the notifier or creation returns an error with a partially allocated object handled by caller cleanup.

### Test signals
Test event object creation with bad versions, allow/block method calls, suspend/resume preserving allow state, notifier deletion on object destroy, and parent event callbacks that use both direct function delivery and client fallback delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/uevent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/Kbuild -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/Kbuild

### Purpose
This Kbuild fragment defines the top-level NVKM engine objects that are always part of the Nouveau build and includes every engine-family subdirectory build fragment.

### Important APIs, types, and functions
It adds `nvkm/engine/falcon.o` and `nvkm/engine/xtensa.o` to `nvkm-y`, then includes Kbuild fragments for BSP, CE, cipher, device, display, DMA, FIFO, GR, MPEG, MSENC, MSPDEC, MSPPP, MSVLD, NVENC, NVDEC, SEC, SEC2, SW, VIC, and VP.

### Control flow
There is no runtime control flow. The build system evaluates this file to determine which objects become part of the `nvkm` built-in object list.

### State and persistence behavior
The file owns build state only: the object list and the inclusion order. Runtime state is introduced by the compiled engine source files.

### Dependencies
It depends on the kernel Kbuild `nvkm-y` convention and the existence of all included `$(src)/nvkm/engine/*/Kbuild` files.

### Integration points
This is the root build integration point for engine code used by the Nouveau DRM driver. Removing or reordering includes changes which engine constructors and symbols are available to `device/base.c`.

### Risks
Missing includes or object entries cause link failures or silently omit hardware support. Because engine families export constructors referenced from the device chipset table, build coverage must stay synchronized with `base.c`.

### Test signals
Full Nouveau builds across common configs, link-time symbol resolution for all constructors used in `device/base.c`, and build tests after adding new engine directories are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/bsp/Kbuild -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/bsp/Kbuild

### Purpose
This Kbuild fragment builds the NVKM BSP engine implementation for G84-era hardware.

### Important APIs, types, and functions
It adds `nvkm/engine/bsp/g84.o` to `nvkm-y`, making `g84_bsp_new()` available to the chipset table.

### Control flow
There is no runtime control flow; Kbuild appends one object file.

### State and persistence behavior
Only build state is affected. Runtime state comes from the compiled Xtensa-backed BSP engine.

### Dependencies
It depends on `engine/Kbuild` including this file and on `g84.c` compiling with the shared engine/xtensa infrastructure.

### Integration points
`device/base.c` references `g84_bsp_new()` for G84/G86/G92/G94/G96/GT200-era chipsets that expose the BSP video engine.

### Risks
Dropping this object breaks link or runtime support for legacy BSP acceleration. Adding newer BSP implementations requires extending this fragment and the chipset table together.

### Test signals
Kernel build and probe on G84-class GPUs with BSP constructor paths enabled are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/bsp/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/bsp/g84.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/bsp/g84.c

### Purpose
`g84.c` defines the G84 BSP video bitstream processor engine as an Xtensa-backed NVKM engine with a single exposed BSP class.

### Important APIs, types, and functions
The public constructor is `g84_bsp_new()`. Static `g84_bsp` is an `nvkm_xtensa_func` with FIFO value `0x1111`, register-like field `unkd28 = 0x90044`, and class `NV74_BSP`.

### Control flow
Device construction calls `g84_bsp_new()`, which delegates to `nvkm_xtensa_new_()` with the function table, engine type, instance, an enable flag that is false only for chipset `0x92`, base address `0x103000`, and the output engine pointer.

### State and persistence behavior
This file owns only a constant function table. Runtime engine state is allocated by the shared Xtensa engine helper and later managed through the subdevice/engine lifecycle.

### Dependencies
It depends on `engine/bsp.h`, the shared Xtensa engine implementation, and NVIF class definitions from `nvif/class.h`.

### Integration points
The chipset table selects this constructor for several G8x/G9x/GT200 devices. The resulting engine registers a BSP class that user channels can bind through FIFO/object infrastructure.

### Risks
The chipset-specific enable flag documents a special-case exclusion for G92. Wrong base address or class exposure would break legacy video decode command submission. Most behavior is hidden in the Xtensa helper, so changes must be tested with that shared engine path.

### Test signals
Build/link coverage, device probe on G84/G86/G94-class cards, absence of BSP registration on excluded chipset `0x92`, and basic video decode command submission are relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/bsp/g84.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/Kbuild -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/Kbuild

### Purpose
This Kbuild fragment builds the copy engine implementations across Nouveau-supported generations from GT215 through GB202 helper support.

### Important APIs, types, and functions
It adds object files for `gt215`, `gf100`, `gk104`, `gm107`, `gm200`, `gp100`, `gp102`, `gv100`, `tu102`, `ga100`, `ga102`, and `gb202` CE sources.

### Control flow
There is no runtime flow. The build list ensures each generation-specific constructor and shared interrupt/helper symbol is available.

### State and persistence behavior
The file affects build composition only. Runtime state is in compiled CE engine instances selected by `device/base.c`.

### Dependencies
It depends on `engine/Kbuild`, the CE sources, generated firmware headers for GT215/GF100, and shared engine/falcon infrastructure.

### Integration points
The chipset table references these constructors with per-chip instance masks. `priv.h` shares helpers among CE implementation files, so all listed objects must be linked together.

### Risks
Forgetting a new object here creates unresolved symbols or missing support for a chipset entry. Removing an older object can break legacy copy engines even if newer platforms still build.

### Test signals
Allmodconfig or Nouveau-enabled kernel builds, link checks for constructor symbols, and device probe across CE generations verify this fragment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/fuc/gf100.fuc3.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/fuc/gf100.fuc3.h

### Purpose
`gf100.fuc3.h` embeds Falcon microcontroller data and instruction images for the Fermi GF100 copy engine. It is included directly by `gf100.c` and loaded through the shared Falcon engine helper.

### Important APIs, types, and functions
The file defines static arrays `gf100_ce_data[]` and `gf100_ce_code[]`. The data image contains copy-engine context fields such as object, query address/counter, source and destination addresses, pitches, tiling modes, sizes, offsets, format, swizzle constants, counters, and a dispatch table. The code image has labeled firmware routines including main, interrupt handler, software context save/load, channel switch, method dispatch, validation errors, PM trigger, surface setup, query, execution kick, and write-cache flush.

### Control flow
There is no C control flow. `gf100.c` passes these arrays and sizes into `struct nvkm_falcon_func`; the Falcon loader copies them to the CE microcontroller, which then runs the encoded firmware to process methods and perform copies.

### State and persistence behavior
The arrays are static read-only driver data after build. At runtime the firmware maintains CE context state in Falcon data memory using the layout encoded here. Persistence across channel switches is controlled by firmware routines and the host Falcon engine code.

### Dependencies
It depends on inclusion from `gf100.c`, C fixed-width integer availability, and compatibility with the Falcon loader and GF100 CE method/class programming.

### Integration points
GF100 CE0/CE1 constructors expose Fermi DMA/decompress classes and point both engines at this firmware. The interrupt handler in `gt215.c` interprets firmware-reported dispatch errors.

### Risks
This is opaque machine code; small changes can break hardware execution, context switching, or method validation. Data layout must match firmware offsets and host class methods. Because the arrays are static in a header, including it in multiple C files would duplicate definitions.

### Test signals
Build of `gf100.c`, firmware load during GF100-class device init, CE channel creation, memory copy/decompress commands, dispatch error logging on invalid methods, and suspend/resume of Falcon CE state are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/fuc/gf100.fuc3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/fuc/gt215.fuc3.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/fuc/gt215.fuc3.h

### Purpose
`gt215.fuc3.h` embeds Falcon data and instruction images for the GT215-generation copy engine firmware. It gives the legacy CE Falcon the context layout and method interpreter used by `gt215.c`.

### Important APIs, types, and functions
The file defines static `gt215_ce_data[]` and `gt215_ce_code[]`. Its data image includes context DMA handles for query/source/destination plus query address, source/destination layout, format, swizzle, counts, and dispatch tables. Its code labels cover main execution, interrupt handling, context switching, method dispatch, DMA setup, invalid method/bitfield errors, PM trigger, tiled/linear surface setup, waits, query writes, copy execution, and cache flush.

### Control flow
The header contributes binary firmware only. `gt215.c` points the Falcon function table at these arrays. Runtime control flow happens on the CE Falcon, not in host C, after `nvkm_falcon_new_()` loads and starts the firmware.

### State and persistence behavior
The arrays are static driver data. Runtime state is Falcon-local context data initialized from `gt215_ce_data[]` and updated by firmware across method dispatch and channel switches.

### Dependencies
It depends on `gt215.c` inclusion, Falcon loader support, and class/method semantics for `GT212_DMA`.

### Integration points
This firmware powers the GT215 CE implementation exposed by `gt215_ce_new()`. Host-side interrupt decoding in `gt215_ce_intr()` maps firmware status values to readable dispatch errors.

### Risks
Firmware is difficult to review and architecture-specific. The GT215 layout differs from GF100 by carrying context DMA fields; mixing the images would break method execution. Any edit must preserve instruction/data alignment and labels assumed by the generated image.

### Test signals
Probe on GT215/GT216/GT218/MCP89-class hardware, successful Falcon firmware boot, DMA copy command execution, expected dispatch errors for invalid methods, and suspend/resume or channel-switch stress are the important checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/fuc/gt215.fuc3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/ga100.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/ga100.c

### Purpose
`ga100.c` implements Ampere GA100 copy engine support using direct interrupt handles rather than the older shared CE interrupt register decoder.

### Important APIs, types, and functions
It exports `ga100_ce_new()`, `ga100_ce_oneinit()`, `ga100_ce_init()`, `ga100_ce_fini()`, and `ga100_ce_nonstall()`. Static `ga100_ce` is an `nvkm_engine_func` with oneinit/init/fini/nonstall callbacks, `gv100_ce_cclass`, and class `AMPERE_DMA_COPY_A`.

### Control flow
`ga100_ce_new()` refuses direct engine creation when GSP-RM owns the device, then calls `nvkm_engine_new_()`. One-time init reads a per-instance interrupt vector from `0x10442c + inst * 0x80` and registers `ga100_ce_intr()` with the VFN interrupt domain. Init allows the subdevice interrupt handle; fini blocks it. `ga100_ce_nonstall()` reads nonstall interrupt status from `0x104424 + inst * 0x80`.

### State and persistence behavior
The file stores no private state beyond the constant function table. Interrupt handle state lives in `engine->subdev.inth`. Hardware interrupt mask/enable state is controlled through `nvkm_inth_allow()` and `nvkm_inth_block()`.

### Dependencies
It depends on `priv.h`, GSP ownership checks, VFN interrupt infrastructure, `gv100_ce_cclass`, and Ampere NVIF class definitions.

### Integration points
`device/base.c` selects this constructor for GA100 CE instances. `ga102.c` reuses the exported oneinit/init/fini/nonstall callbacks. The VFN interrupt domain is the routing layer for per-engine interrupts on this generation.

### Risks
The actual interrupt handler is marked TODO and returns `IRQ_NONE` after logging, so real interrupt diagnosis is incomplete. Wrong vector/status register offsets would leave CE interrupts unhandled. GSP-RM checks must stay aligned with firmware-managed device modes.

### Test signals
Probe on GA100 without GSP-RM, interrupt vector registration, allow/block behavior across init/fini, nonstall status reads, CE class exposure, and negative probe behavior under GSP-RM are relevant tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/ga100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/ga102.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/ga102.c

### Purpose
`ga102.c` provides the GA102-family Ampere CE function table, reusing GA100 interrupt lifecycle helpers while exposing both A and B Ampere DMA copy classes.

### Important APIs, types, and functions
The public constructor is `ga102_ce_new()`. Static `ga102_ce` uses `ga100_ce_oneinit()`, `ga100_ce_init()`, `ga100_ce_fini()`, `ga100_ce_nonstall()`, `gv100_ce_cclass`, and classes `AMPERE_DMA_COPY_A` and `AMPERE_DMA_COPY_B`.

### Control flow
Construction checks `nvkm_gsp_rm(device->gsp)` and returns `-ENODEV` when the GSP resource manager owns CE. Otherwise it calls `nvkm_engine_new_()` with the GA102 function table and true enable flag.

### State and persistence behavior
This file has no mutable state. Runtime CE state, interrupt handle state, and context class GPU objects are managed by shared engine/subdevice code and the callbacks imported from GA100/GV100.

### Dependencies
It depends on `priv.h`, GSP helpers, Ampere NVIF class definitions, and the exported GA100/GV100 helpers declared in `priv.h`.

### Integration points
`device/base.c` uses this constructor for GA102, GA103, GA104, GA106, GA107, and Ada AD10x CE masks. The class table allows userspace/FIFO paths to bind the appropriate Ampere copy object class.

### Risks
All interrupt behavior is inherited from GA100, including the incomplete TODO handler. The class set must match hardware/FIFO expectations; exposing B on devices that do not support it would surface invalid classes.

### Test signals
Build/link with GA100 helpers, probe on GA102-family devices with GSP-RM disabled, class enumeration for A/B copy classes, interrupt registration through VFN, and expected `-ENODEV` with GSP-RM enabled are key checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/ga102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gb202.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gb202.c

### Purpose
`gb202.c` provides a small Blackwell CE hardware helper that reads the GRCE mask from generated hardware register definitions.

### Important APIs, types, and functions
The exported function is `gb202_ce_grce_mask(struct nvkm_device *device)`. It reads `NV_CE_GRCE_MASK` and extracts `NV_CE_GRCE_MASK_VALUE` via `NVVAL_GET()`.

### Control flow
There is a single register read and field extraction. No engine is constructed in this file.

### State and persistence behavior
The file owns no state and does not modify hardware. It returns current register state at call time.

### Dependencies
It depends on `priv.h`, `nvhw/drf.h`, and generated reference header `nvhw/ref/gb202/dev_ce.h`.

### Integration points
Other Blackwell-aware Nouveau code can use this helper to identify which copy engines are graphics-related. It is built with CE objects through `ce/Kbuild`.

### Risks
Generated register definitions must match the GB202 hardware spec. A stale field macro would return the wrong mask and misroute CE/GR relationships. Callers must handle masks on devices where firmware/GSP ownership may hide direct CE management.

### Test signals
Compile coverage with generated NVHW headers, register-read smoke tests on GB202 hardware, and callers validating expected GRCE masks from hardware topology are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gb202.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gf100.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gf100.c

### Purpose
`gf100.c` implements Fermi copy engine construction using Falcon firmware embedded in `gf100.fuc3.h`, with separate class exposure for CE0 DMA and CE1 decompress engines.

### Important APIs, types, and functions
The public constructor is `gf100_ce_new()`. Static Falcon function tables `gf100_ce0` and `gf100_ce1` share firmware, `gf100_ce_init()`, and `gt215_ce_intr()`, but expose `FERMI_DMA` and `FERMI_DECOMPRESS` respectively.

### Control flow
`gf100_ce_new()` selects CE1's function table when `inst` is nonzero and CE0 otherwise, enables the Falcon engine, and passes base address `0x104000 + inst * 0x1000` to `nvkm_falcon_new_()`. `gf100_ce_init()` writes the CE instance number to `ce->addr + 0x084`.

### State and persistence behavior
The source owns constant function tables and firmware references. Runtime state is held by the Falcon engine, the loaded firmware image, and subdevice lifecycle state.

### Dependencies
It depends on `priv.h`, `fuc/gf100.fuc3.h`, Falcon engine support, the GT215 dispatch-error interrupt helper, and NVIF class definitions.

### Integration points
`device/base.c` uses this constructor for GF100/GF10x devices with one or two CE instances. FIFO class binding exposes DMA or decompress classes depending on instance.

### Risks
The instance-based class split is hardware-specific; wrong `inst` mapping changes user-visible classes. Firmware image and init register must match Fermi CE hardware. The interrupt handler is shared with GT215 and decodes Falcon dispatch errors using older status registers, so offset compatibility is critical.

### Test signals
Probe on GF100-class GPUs, Falcon firmware load, CE0 DMA copy and CE1 decompress class creation, invalid method error reporting, and multiple-instance base address coverage are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gk104.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gk104.c

### Purpose
`gk104.c` implements Kepler CE interrupt decoding and construction for engines that expose `KEPLER_DMA_COPY_A`.

### Important APIs, types, and functions
It exports `gk104_ce_intr()` and `gk104_ce_new()`. Static data includes `gk104_ce_launcherr_report[]` mapping launch error codes and `gk104_ce` engine function table.

### Control flow
The interrupt handler reads mask/status registers at `0x104904/0x104908 + inst * 0x1000`, reports and acknowledges BLOCKPIPE, NONBLOCKPIPE, and LAUNCHERR bits, and clears any remaining unknown bits. Launch errors are decoded from `0x104f14 + base` and then cleared. Construction delegates to `nvkm_engine_new_()`.

### State and persistence behavior
There is no private mutable state. Interrupt state is hardware register state cleared by writes. Runtime engine state belongs to the common engine/subdevice layer.

### Dependencies
It depends on `priv.h`, `core/enum.h`, MMIO helpers, and NVIF class definitions.

### Integration points
Kepler device entries in `base.c` use this constructor with multi-instance CE masks. Maxwell GM107/GM200 reuse `gk104_ce_intr()` with different class tables.

### Risks
Register offsets and instance stride are generation-specific. Clearing unknown interrupt bits can mask new conditions if hardware evolves. Launch error code naming is diagnostic only, but wrong decoding can mislead debugging.

### Test signals
Interrupt tests on GK104/GK106/GK107, invalid copy launch to trigger launch-error reporting, multi-instance interrupt routing, and class enumeration for `KEPLER_DMA_COPY_A` are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gm107.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gm107.c

### Purpose
`gm107.c` provides the Maxwell GM107 CE function table while reusing Kepler-style interrupt handling.

### Important APIs, types, and functions
The public constructor is `gm107_ce_new()`. Static `gm107_ce` sets `.intr = gk104_ce_intr` and exposes both `KEPLER_DMA_COPY_A` and `MAXWELL_DMA_COPY_A`.

### Control flow
Construction calls `nvkm_engine_new_()` with the GM107 function table. Runtime interrupt flow is entirely delegated to `gk104_ce_intr()`.

### State and persistence behavior
The file has no mutable state. Engine state is allocated by the common engine constructor.

### Dependencies
It depends on `priv.h`, the exported Kepler interrupt helper, and NVIF class definitions.

### Integration points
`device/base.c` uses this constructor for GM107/GM108 CE instance masks. Class exposure lets userspace pick either compatible Kepler or Maxwell copy classes.

### Risks
The compatibility class list must match FIFO/object expectations. Reusing Kepler interrupt offsets assumes GM107 CE register layout remains compatible.

### Test signals
Probe on GM107/GM108, class enumeration for both exposed classes, copy command execution through each class where supported, and interrupt handling under error conditions are relevant checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gm107.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gm200.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gm200.c

### Purpose
`gm200.c` defines the second-generation Maxwell CE engine table.

### Important APIs, types, and functions
The public constructor is `gm200_ce_new()`. Static `gm200_ce` uses `gk104_ce_intr()` and exposes `MAXWELL_DMA_COPY_A`.

### Control flow
Construction delegates to `nvkm_engine_new_()` with the table and the requested instance. Interrupt control flow is inherited from the Kepler handler.

### State and persistence behavior
There is no file-local mutable state. Runtime engine state is common NVKM engine/subdevice state.

### Dependencies
It depends on `priv.h`, `gk104_ce_intr()`, and NVIF class definitions.

### Integration points
GM200/GM204/GM206 and GM20B entries in `device/base.c` reference this constructor with per-chip instance masks. It contributes CE support to Maxwell2 copy channels.

### Risks
The interrupt register layout assumption must remain valid for GM200-class hardware. Exposing only the Maxwell class means compatibility with older class IDs is intentionally not provided here.

### Test signals
Build/link with Kepler interrupt helper, probe on GM20x, class enumeration, copy command submission, and interrupt error handling are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gp100.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gp100.c

### Purpose
`gp100.c` implements Pascal GP100 CE interrupt decoding and construction for `PASCAL_DMA_COPY_A`.

### Important APIs, types, and functions
It exports `gp100_ce_intr()` and `gp100_ce_new()`. Static `gp100_ce_launcherr_report[]` names Pascal launch error codes, and `gp100_ce` is the engine function table.

### Control flow
The interrupt handler reads mask/status at `0x10440c/0x104410 + inst * 0x80`, reports guessed BLOCKPIPE and NONBLOCKPIPE bits, decodes launch errors from `0x104418 + base`, acknowledges handled bits, and clears unknown residual status. Construction calls `nvkm_engine_new_()`.

### State and persistence behavior
There is no private memory state. Hardware interrupt state is cleared by MMIO writes. Common engine code owns lifecycle state.

### Dependencies
It depends on `priv.h`, `core/enum.h`, MMIO access, and Pascal NVIF class definitions.

### Integration points
`device/base.c` selects this constructor for GP100 and GP10B. `gp102.c` reuses `gp100_ce_intr()` for later Pascal chips with additional class exposure.

### Risks
The handler includes comments marking some bit meanings as guesses; diagnostics and acknowledgments may be incomplete. Pascal uses a different instance stride than Kepler/Maxwell, so reusing offsets incorrectly would break interrupts.

### Test signals
Probe on GP100, invalid launches that trigger each decoded error, multi-instance CE status handling, and successful `PASCAL_DMA_COPY_A` submissions are relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gp100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gp102.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gp102.c

### Purpose
`gp102.c` defines later Pascal CE support, reusing GP100 interrupt handling while exposing both Pascal A and B copy classes.

### Important APIs, types, and functions
The public constructor is `gp102_ce_new()`. Static `gp102_ce` uses `gp100_ce_intr()` and classes `PASCAL_DMA_COPY_B` and `PASCAL_DMA_COPY_A`.

### Control flow
Construction is a direct `nvkm_engine_new_()` call. Runtime interrupts flow through the GP100 handler.

### State and persistence behavior
This file has no mutable state. Engine instance state is created and managed by the common engine layer.

### Dependencies
It depends on `priv.h`, the GP100 interrupt helper, and NVIF class definitions.

### Integration points
GP102/GP104/GP106/GP107/GP108 device entries use this constructor with CE instance masks. FIFO/object class exposure gives later Pascal userspaces access to B and A class variants.

### Risks
Class ordering and support must match hardware and userspace expectations. Interrupt reuse assumes GP102 register layout matches GP100's status block.

### Test signals
Probe on GP10x hardware, class enumeration for Pascal A/B, copy submissions through both class IDs, and error interrupt reporting through `gp100_ce_intr()` are the useful checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gp102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gt215.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gt215.c

### Purpose
`gt215.c` implements the GT215 copy engine as a Falcon engine with embedded firmware and a dispatch-error interrupt decoder.

### Important APIs, types, and functions
It exports `gt215_ce_intr()` and `gt215_ce_new()`. Static `gt215_ce` is an `nvkm_falcon_func` using `gt215_ce_code`, `gt215_ce_data`, the interrupt helper, and class `GT212_DMA`. The interrupt error table maps firmware status values to `ILLEGAL_MTHD`, `INVALID_ENUM`, and `INVALID_BITFIELD`.

### Control flow
`gt215_ce_new()` constructs a Falcon engine at base `0x104000`, using instance `-1` and disabling a boolean path for chipset `0xaf`. `gt215_ce_intr()` reads CE dispatch status, method address/subchannel, data, and channel information, resolves the channel instance when supplied, and logs a detailed dispatch error.

### State and persistence behavior
The file owns constant firmware references and function tables. Runtime state is Falcon firmware state plus common engine/subdevice state. Interrupt reads do not clear status here; higher-level Falcon interrupt handling surrounds this callback.

### Dependencies
It depends on `priv.h`, `fuc/gt215.fuc3.h`, client/enum/gpuobj/fifo helpers, Falcon engine support, and NVIF class definitions.

### Integration points
GT215-family chipset entries use this constructor. GF100 CE reuses the interrupt decoder with its own firmware. FIFO channel lookup integrates error logs with channel ids, instance addresses, and names.

### Risks
The interrupt decoder depends on GT215/GF100 Falcon status register layout. The chipset `0xaf` special case needs preservation. Firmware and class definitions must match the hardware method interface.

### Test signals
Falcon firmware boot on GT215-class GPUs, DMA copy execution, invalid methods producing decoded dispatch errors, channel name/id resolution in logs, and chipset `0xaf` constructor behavior are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gt215.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gv100.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gv100.c

### Purpose
`gv100.c` implements Volta CE construction and the class-context GPU object binder used by Volta and later direct CE implementations.

### Important APIs, types, and functions
It exports `gv100_ce_new()` and global `gv100_ce_cclass`. `gv100_ce_cclass_bind()` allocates a fault method buffer sized from hardware register `NV_PCE_PCE_MAP` at `0x104028`. Static `gv100_ce` uses `gp100_ce_intr()`, the context class binder, and class `VOLTA_DMA_COPY_A`.

### Control flow
Context class binding reads the CE map, counts active bits with `hweight32()`, applies the nvgpu-derived sizing formula, rounds up to a page, and allocates a GPU object. Engine construction calls `nvkm_engine_new_()`.

### State and persistence behavior
The binder creates per-channel/class GPU objects that persist with the owning object. The file's function table is static. Runtime interrupts use Pascal-style handling.

### Dependencies
It depends on `priv.h`, GPU object and object helpers, `gp100_ce_intr()`, and NVIF class definitions.

### Integration points
GV100 device entries use this constructor. Turing, Ampere, and GA102 CE files reuse `gv100_ce_cclass` for fault method buffer allocation.

### Risks
The fault-buffer sizing formula is explicitly derived from external knowledge and hardware maps; wrong sizing can underallocate context buffers. Reusing Pascal interrupt handling assumes Volta status registers are compatible. Page rounding is important for GPU object allocation constraints.

### Test signals
Probe on GV100, class-context object allocation with varying CE maps, copy submissions, interrupt error handling, and later-generation users of `gv100_ce_cclass` are useful checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/gv100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/priv.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/priv.h

### Purpose
`priv.h` is the internal CE engine header that shares constructors, interrupt helpers, context class binders, Ampere callbacks, and Blackwell helpers among CE implementation files.

### Important APIs, types, and functions
It declares `r535_ce_new()`, `gt215_ce_intr()`, `gk104_ce_intr()`, `gp100_ce_intr()`, external `gv100_ce_cclass`, `ga100_ce_oneinit()`, `ga100_ce_init()`, `ga100_ce_fini()`, `ga100_ce_nonstall()`, and `gb202_ce_grce_mask()`.

### Control flow
The header has no executable flow. It allows generation-specific C files to reuse shared implementation pieces without exporting them through the public `engine/ce.h` API.

### State and persistence behavior
It owns no state. The declarations refer to state managed by CE engines, subdevices, interrupt handles, and GPU objects.

### Dependencies
It includes `engine/ce.h`, which exposes public CE constructors and Falcon engine definitions.

### Integration points
All CE implementation C files include this header. It is the private link between GT215/GF100 Falcon helpers, Kepler/Pascal interrupt handlers, Volta context binding, Ampere interrupt lifecycle, R535/GSP-managed paths, and Blackwell hardware helpers.

### Risks
Prototype drift causes build failures or subtle ABI mismatches within the CE directory. Adding declarations here without corresponding Kbuild entries can still leave unresolved symbols.

### Test signals
Compile coverage of every CE object, link checks for shared symbols, and cross-generation CE probe tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/tu102.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/tu102.c

### Purpose
`tu102.c` defines Turing CE support, using Pascal-style interrupts and the Volta context class binder while avoiding direct engine creation when GSP-RM controls the device.

### Important APIs, types, and functions
The public constructor is `tu102_ce_new()`. Static `tu102_ce` uses `gp100_ce_intr()`, `gv100_ce_cclass`, and class `TURING_DMA_COPY_A`.

### Control flow
`tu102_ce_new()` checks `nvkm_gsp_rm(device->gsp)` and returns `-ENODEV` under GSP-RM ownership. Otherwise it constructs the engine with `nvkm_engine_new_()`.

### State and persistence behavior
No file-local mutable state exists. Runtime state is common engine/subdevice state plus per-context GPU objects allocated by `gv100_ce_cclass`.

### Dependencies
It depends on `priv.h`, GSP helpers, Pascal interrupt helper, Volta context binder, and NVIF Turing class definitions.

### Integration points
Turing chipset entries in `base.c` use this constructor with CE instance masks. It bridges pre-GSP direct CE management and newer firmware-managed modes.

### Risks
Direct CE support must remain disabled under GSP-RM to avoid conflicting ownership. Reusing Pascal interrupt handling and Volta context sizing assumes Turing compatibility. Class exposure is limited to Turing A.

### Test signals
Probe on TU10x with direct management, expected `-ENODEV` under GSP-RM, context buffer allocation, class enumeration, copy command execution, and interrupt error reporting are relevant tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/tu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/cipher/Kbuild -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/cipher/Kbuild

### Purpose
This Kbuild fragment builds the legacy G84 cipher engine implementation.

### Important APIs, types, and functions
It appends `nvkm/engine/cipher/g84.o` to `nvkm-y`, making `g84_cipher_new()` and related static class behavior part of the NVKM object.

### Control flow
There is no runtime flow; Kbuild includes one object file.

### State and persistence behavior
Only build composition is affected.

### Dependencies
It depends on `engine/Kbuild` including this file and `g84.c` compiling with engine/fifo/gpuobj support.

### Integration points
`device/base.c` references `g84_cipher_new()` for G84/G86/G92/G94/G96/GT200-era chipsets.

### Risks
Removing the object breaks legacy cipher engine constructor availability. Adding another cipher generation requires this build file and chipset table updates.

### Test signals
Nouveau build/link checks and probe on G84-class hardware with cipher engine enabled validate this fragment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/cipher/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/cipher/g84.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/cipher/g84.c

### Purpose
`g84.c` implements the legacy G84 cipher engine, including class binding records, context allocation, interrupt decoding, and engine initialization.

### Important APIs, types, and functions
The public constructor is `g84_cipher_new()`. Internal callbacks include `g84_cipher_oclass_bind()`, `g84_cipher_cclass_bind()`, `g84_cipher_intr()`, and `g84_cipher_init()`. Static tables define object class bind behavior, context class bind behavior, interrupt bit names, and engine class `NV74_CIPHER`.

### Control flow
Object class binding allocates a 16-byte GPU object and writes the object class plus zeros. Context class binding allocates a 256-byte zeroed GPU object. Init clears and enables interrupt registers at `0x102130`, `0x102140`, and `0x10200c`. Interrupt handling reads status, method, data, and instance, resolves the channel by instance, logs decoded errors, acknowledges status, and pokes the engine interrupt control register.

### State and persistence behavior
Per-object and per-context GPU objects persist with their owning classes. Hardware interrupt state is cleared during init and interrupt handling. The file has no private heap state.

### Dependencies
It depends on `engine/cipher.h`, `engine/fifo.h`, client/enum/gpuobj helpers, channel lookup, MMIO access, and NVIF class definitions.

### Integration points
The G84-family chipset table entries construct this engine. FIFO channel lookup connects interrupt diagnostics to channel identity. Object binding integrates with RAMHT/FIFO class contexts.

### Risks
The register offsets are G84-specific. Interrupt handling logs and clears all status bits; unknown future bits may be lost. Binding record layout must match hardware expectations for class/context objects.

### Test signals
Probe on G84/G9x with cipher enabled, class/context object allocation, interrupt injection or invalid method tests, channel lookup in error logs, and engine init register programming checks are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/cipher/g84.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/Kbuild -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/Kbuild

### Purpose
This Kbuild fragment builds the NVKM device engine core and platform-specific device transport layers.

### Important APIs, types, and functions
It appends `acpi.o`, `base.o`, `ctrl.o`, `pci.o`, `tegra.o`, and `user.o` under `nvkm/engine/device/` to `nvkm-y`.

### Control flow
There is no runtime flow. Build inclusion makes device construction, control object methods, ACPI hooks, PCI/Tegra backends, and user object support available.

### State and persistence behavior
The file controls object inclusion only. Runtime device state is implemented by the compiled sources.

### Dependencies
It depends on top-level `engine/Kbuild` and the listed source files.

### Integration points
This is the build entry for `device/base.c`, the central chipset database used by the rest of NVKM. The platform files provide concrete `nvkm_device_func` backends.

### Risks
Omitting `base.o` or platform backends breaks Nouveau device construction. Adding a new platform backend requires this build file to be updated.

### Test signals
Kernel build/link checks, PCI and Tegra probe tests, control-object ioctl tests, and ACPI notifier build coverage validate this fragment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/acpi.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/acpi.c

### Purpose
`acpi.c` registers a small ACPI notifier for NVKM devices so AC adapter changes can refresh Nouveau clock power-source state.

### Important APIs, types, and functions
The public functions are `nvkm_acpi_init()` and `nvkm_acpi_fini()`. Under `CONFIG_ACPI`, static `nvkm_acpi_ntfy()` handles ACPI bus events.

### Control flow
Init assigns `device->acpi.nb.notifier_call` and registers the ACPI notifier. The notifier checks for `device_class == "ac_adapter"` and calls `nvkm_clk_pwrsrc(device)`. Fini unregisters the notifier. When `CONFIG_ACPI` is disabled, init/fini compile to no-ops.

### State and persistence behavior
The notifier block is stored in `device->acpi.nb` for the device lifetime while registered. No additional state is persisted in this file.

### Dependencies
It depends on `acpi.h`, `core/device.h`, `subdev/clk.h`, and ACPI notifier APIs when configured.

### Integration points
`device/base.c` calls `nvkm_acpi_init()` after subdevices initialize and `nvkm_acpi_fini()` during device fini. The clock subdevice consumes AC/DC source changes.

### Risks
Notifier registration must be balanced with unregister during teardown. The string match is narrow to AC adapter events. Calling into clock code during ACPI notification requires the device and clock subdevice to remain valid.

### Test signals
Builds with and without `CONFIG_ACPI`, AC adapter plug/unplug while Nouveau is loaded, clock power-source updates, and device unload after notifier registration are useful checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/acpi.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/acpi.h

### Purpose
`acpi.h` declares the NVKM device ACPI init/fini hooks used internally by the device engine.

### Important APIs, types, and functions
It forward-declares `struct nvkm_device` and declares `nvkm_acpi_init()` and `nvkm_acpi_fini()`.

### Control flow
The header has no runtime flow.

### State and persistence behavior
It owns no state. The functions it declares manipulate notifier state stored in `struct nvkm_device`.

### Dependencies
It includes `core/os.h` for kernel/NVKM base definitions.

### Integration points
`device/base.c` includes this header to call ACPI setup/teardown around device lifecycle. `acpi.c` provides the implementation.

### Risks
Prototype drift between header and implementation would break builds. Keeping this private to the device engine avoids exposing ACPI hooks as broad public NVKM API.

### Test signals
Compile coverage of `base.c` and `acpi.c` with `CONFIG_ACPI` enabled and disabled validates the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/base.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/base.c

### Purpose
`base.c` is the central NVKM device core. It keeps the global device registry, maps BAR0 PRI MMIO, identifies chipsets, selects the per-chip subdevice/engine constructor table, constructs all subdevices from `core/layout.h`, and drives device preinit/init/fini/delete lifecycle.

### Important APIs, types, and functions
Public functions include `nvkm_device_find()`, `nvkm_device_subdev()`, `nvkm_device_engine()`, `nvkm_device_fini()`, `nvkm_device_init()`, `nvkm_device_del()`, and `nvkm_device_ctor()`. Internal helpers include `nvkm_device_find_locked()`, `nvkm_device_preinit()`, and `nvkm_device_endianness()`. The bulk of the file is `static const struct nvkm_device_chip` tables for NV04 through GB20x families, mapping subdevice/engine instance masks to constructor functions.

### Control flow
Construction is serialized by `nv_devices_mutex`, rejects duplicate handles, maps PRI MMIO, switches GPU endianness if needed, reads boot registers, applies optional `NvChipset` override, derives chipset/card type, selects the matching chipset table, rejects unsupported vGPU modes on TU100+, reads strap bits to set crystal frequency, initializes interrupts, then expands `core/layout.h` macros to construct each singleton or instanced subdevice indicated by the selected table. `-ENODEV` constructors are treated as absent optional components; other errors abort construction.

Preinit unarms interrupts, calls device preinit, preinits subdevices in list order, runs devinit post, parses top topology, and unlocks framebuffer memory. Full init calls preinit, powers off existing state, rearms interrupts, runs device init, initializes subdevices in list order, registers ACPI notification, and enables thermal clock gating. Fini unregisters ACPI, finishes subdevices in reverse order, disables thermal clock gating, calls device fini, and unarms interrupts. Suspend failures trigger restart of already-finished subdevices. Delete destroys interrupt infrastructure, deletes subdevices in reverse order, unmaps PRI, removes the device from the registry, calls backend destructor, and frees memory.

### State and persistence behavior
Global state is `nv_devices`, protected by `nv_devices_mutex`. Per-device persistent state includes backend function table, quirk pointer, Linux device pointer, type, handle, config/debug option strings, name, debug level, MMIO mapping, chipset metadata, crystal frequency, interrupt state, subdevice list, and direct pointers to constructed subdevices/engine arrays. The chipset tables are static read-only hardware support data.

### Dependencies
It depends on `priv.h`, `acpi.h`, option parsing, BIOS and thermal helpers, interrupt helpers, devinit/top/fb helpers, all subdevice and engine constructor declarations, Linux `ioremap()`/`iounmap()`, MMIO helpers, list/mutex primitives, and `core/layout.h`.

### Integration points
PCI, Tegra, and user-facing device layers call `nvkm_device_ctor()` with platform-specific resource functions. Every subdevice/engine constructor referenced in the chipset tables is integrated through this file. The control object, FIFO, display, GR, memory, firmware/GSP, and CE engines are all selected from these tables based on chipset.

### Risks
This file has very high blast radius. A wrong chipset table entry can instantiate incompatible hardware blocks, omit required firmware managers, expose invalid engine counts, or break probe for a whole GPU family. The `NvChipset` and unsupported-chipset options are development paths that can force mismatched tables. Endianness switching and BAR mapping failures occur early and must clean up correctly. Treating `-ENODEV` as optional is necessary for GSP-owned components but can hide unexpected missing hardware if constructors overuse it.

### Test signals
Essential signals include build/link coverage for all constructor symbols, probe tests across representative NV04/NV50/Fermi/Kepler/Maxwell/Pascal/Volta/Turing/Ampere/Ada/Blackwell devices, duplicate handle rejection, vGPU rejection on TU100+, suspend/resume and runtime suspend rollback, GSP-RM device modes, optional constructor `-ENODEV` handling, ACPI notifier registration, and teardown leak/error checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/ctrl.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/ctrl.c

### Purpose
`ctrl.c` implements the NVIF device control object, currently focused on power-state and clock-domain query/control methods.

### Important APIs, types, and functions
The exported object class descriptor is `nvkm_control_oclass`. Internal method handlers are `nvkm_control_mthd_pstate_info()`, `nvkm_control_mthd_pstate_attr()`, `nvkm_control_mthd_pstate_user()`, `nvkm_control_mthd()`, and constructor `nvkm_control_new()`.

### Control flow
The method dispatcher handles `NVIF_CONTROL_PSTATE_INFO`, `NVIF_CONTROL_PSTATE_ATTR`, and `NVIF_CONTROL_PSTATE_USER`. Each method unpacks a versioned v0 NVIF structure with `nvif_unpack()`. Pstate info returns count, AC/DC user states, power source, and current pstate, or disabled/unknown values when no clock subdevice exists. Pstate attr validates state/index, finds the indexed clock domain with a monitor name, computes min/max from the requested pstate's base/cstate list or current clock read, fills name/unit/range, and returns the next index. Pstate user applies requested user state to one or both power sources via `nvkm_clk_ustate()`.

### State and persistence behavior
Each control object stores a base `nvkm_object` and `struct nvkm_device *`. It does not cache pstate data; all state is read from or written to `device->clk`. User pstate changes persist in the clock subdevice's `ustate_ac`/`ustate_dc` behavior.

### Dependencies
It depends on `ctrl.h`, client logging, clock subdevice types and helpers, NVIF control ABI headers, ioctl logging, and `nvif_unpack()`.

### Integration points
`nvkm_control_oclass` exposes `NVIF_CLASS_CONTROL` to NVIF clients. Device/user object creation can instantiate this control object so userspace can query and set performance states.

### Risks
Versioned ABI unpacking must stay strict. The pstate attr loop assumes valid clock domain and pstate lists after validation; clock state mutations elsewhere could race if not externally serialized by higher-level ioctl/device locking. Applying user state to both power sources accumulates return codes with bitwise OR, so callers receive a combined error.

### Test signals
NVIF control ioctl tests for pstate info/attr/user, no-clock-device behavior, invalid state/index rejection, current-state clock reads, AC/DC user-state changes, and ABI size/version mismatch tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/ctrl.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/ctrl.h

### Purpose
`ctrl.h` defines the private NVKM control object wrapper and exports its class descriptor to the device engine.

### Important APIs, types, and functions
It defines `nvkm_control(p)` as a `container_of()` helper, declares `struct nvkm_control` with base object and device pointer, and declares `extern const struct nvkm_device_oclass nvkm_control_oclass`.

### Control flow
The header has no runtime control flow.

### State and persistence behavior
It describes the per-control-object state allocated in `ctrl.c`; it owns no storage itself.

### Dependencies
It includes `core/object.h`, which provides `struct nvkm_object` and object callback contracts.

### Integration points
`ctrl.c` implements the declared class. Device object construction code can expose `nvkm_control_oclass` as the NVIF control class.

### Risks
The container helper assumes the embedded object is the first relevant member of `struct nvkm_control`; layout changes must preserve the helper's intent. Prototype or type drift breaks control object construction.

### Test signals
Compile coverage of `ctrl.c` and any device user code referencing `nvkm_control_oclass`, plus control object create/destroy tests, validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/ctrl.h -->
