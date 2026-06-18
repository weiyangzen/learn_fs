# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/uchan.c

Purpose: implements the user-visible FIFO channel object and channel child engine-object proxying. It creates channels from NVIF args, maps USERD, exposes engine object classes, handles channel init/fini, binds/unbinds engine contexts on object lifecycle, supports non-stall/killed events, and returns channel tokens/instance information to userspace.

Important APIs and data: `struct nvkm_uchan`, `struct nvkm_uobj`, `nvkm_uchan_new()`, `nvkm_uchan_chan()`, `nvkm_uchan_init()`, `nvkm_uchan_fini()`, `nvkm_uchan_map()`, `nvkm_uchan_sclass()`, `nvkm_uchan_object_new()`, and proxy callbacks `nvkm_uchan_object_init_0()`, `nvkm_uchan_object_fini_1()`, and `nvkm_uchan_object_dtor()`.

Control flow: constructor validates NVIF channel args, resolves runlist, VMM, DMA object, and optional USERD memory, allocates a user object, calls `nvkm_chan_new_()`, returns doorbell token or `~0`, CHID, instance aperture, and instance address. Init binds the channel, allows it, and inserts it into the runlist unless already errored. Fini blocks/removes the channel and unbinds hardware. Child object creation finds the host engine, obtains a channel context, constructs the engine object under the context object when present, and inserts RAMHT entries when required.

State and persistence: maintains channel references, channel context references, refcounts for engine/channel context use, RAMHT hash values, and runtime events. No durable persistence.

Dependencies and integration: depends on channel/group/runlist/chid helpers, VMM and DMA object handle lookup, GPU memory mapping, engine FIFO class enumeration, object proxy lifecycle, and FIFO channel function tables.

Risks: complex lifetime/refcount sequencing around `cctx->uses` and `ectx->uses`; partial failures after object/proxy allocation must unwind through object destruction; runqueue-specific CE class filtering assumes `chan->runq` matches runlist runqueue layout; mapping requires channel USERD BAR support.

Test signals: NVIF channel creation with VMM/ctxdma/userd variants, USERD mmap address/size, init/fini channel insertion/removal, killed and non-stall uevents, engine object creation/destruction with RAMHT cleanup, and errored-channel init behavior.
