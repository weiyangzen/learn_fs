<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/base.c

Purpose: common display engine object implementation. It owns top-level display lifecycle, display object lists, vblank and user channel events, and registration of the root user display class.

Important APIs and functions: `nvkm_disp_new_()` allocates and initializes `struct nvkm_disp`, list heads, client lock, engine base, optional supervisor workqueue, and the user event object. `nvkm_disp_vblank()` emits per-head vblank events. The engine callbacks `nvkm_disp_oneinit()`, `nvkm_disp_init()`, `nvkm_disp_fini()`, `nvkm_disp_intr()`, and `nvkm_disp_dtor()` implement lifecycle. `nvkm_disp_class_get()` exposes the generation-specific display root class through `nvkm_udisp_new()`.

Control flow: oneinit calls generation `func->oneinit`, counts heads, and initializes vblank events. Init initializes outputs first, then generation display hardware, then powers all IORs into a fully enabled normal state. Fini calls generation fini and output fini callbacks. Destructor tears down RAMHT/GPU object, events, supervisor workqueue/mutex, then deletes connectors, outputs, IORs, and heads in list order.

State and persistence: persistent state is in `struct nvkm_disp`: object lists, `disp->chan[]`, client spinlock, RAMHT/GPU object pointers, vblank/uevent structures, and optional supervisor work item. Hardware state is delegated to generation callbacks and output/IOR callbacks.

Dependencies and integration points: depends on the NVKM engine framework, RAMHT/GPU object management, event subsystem, output/connector/head/IOR helpers, and user display class wrappers.

Risks: destructor ordering matters because outputs reference connectors/IORs and events may point at heads. Init ordering matters for output setup before display core programming. Event head count must reflect the maximum head ID plus one.

Test signals: display engine construction/destruction, hotplug/vblank event subscription, modeset init/fini, suspend/resume, and memory leak checks for list-owned objects and workqueues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/base.c -->
