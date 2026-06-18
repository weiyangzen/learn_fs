# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/base.c

Purpose: implements the generic GR engine wrapper. It adapts `struct nvkm_gr_func` chip callbacks to `struct nvkm_engine_func`, exposes context-switch helpers, tile/TLB/unit helpers, FIFO class hooks, and the GR constructor.

Important APIs and data: `nvkm_gr_ctxsw_inst()`, `nvkm_gr_ctxsw_resume()`, `nvkm_gr_ctxsw_pause()`, `nvkm_gr_units()`, `nvkm_gr_tlb_flush()`, `nvkm_gr_ctor()`, and internal engine callbacks for object class lookup, channel class construction, interrupt, non-stall, oneinit, reset, init, fini, and dtor. The static `nvkm_gr` engine function table wires these callbacks into NVKM.

Control flow: public helpers check for `device->gr` and optional chip callbacks before invoking them. FIFO object enumeration calls `nvkm_gr_oclass_get()` to fetch graphics object classes, and channel object creation calls `nvkm_gr_cclass_new()` for per-channel class setup. Engine lifecycle calls forward to chip-specific GR functions if present.

State and persistence: `struct nvkm_gr` stores the selected function table and is embedded in an `nvkm_engine`. The file manages no durable state; lifecycle callbacks may create hardware state in chip files.

Dependencies and integration: depends on `priv.h`, FIFO channel objects, and the NVKM engine core. It is the bridge between FIFO-created channel objects and GR-specific object/context handling.

Risks: optional callback handling returns neutral values in many cases, so missing chip callbacks can silently disable features; object class index accounting must remain correct for FIFO enumeration; reset returns `-ENOSYS` if not implemented.

Test signals: GR engine construction, object class enumeration through FIFO channels, context-switch pause/resume helpers, interrupt forwarding, non-stall forwarding, and chip-specific init/fini/reset callbacks firing during device lifecycle.
