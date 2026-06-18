<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uhead.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uhead.c

## Purpose

`uhead.c` exposes display heads to NVIF clients. It provides vblank event subscription and scanout-position/timing queries for DRM timestamping.

## Important APIs, Types, And Functions

`nvkm_uhead_uevent()` registers vblank events on `head->disp->vblank`. `nvkm_uhead_mthd_scanoutpos()` validates ABI arguments, refreshes armed head state, fills total/blank timing, samples time before and after `head->func->rgpos()`, and returns current hline/vline. `nvkm_uhead_mthd()` dispatches `NVIF_HEAD_V0_SCANOUTPOS`. `nvkm_uhead_new()` finds a head by id and installs its embedded object under `disp->client.lock`.

## Control Flow

Userspace opens a head object through the display root. Event registration is direct to the vblank event source. Method calls route through the object function to scanout position. Destruction clears `head->object.func`.

## State And Persistence Behavior

The user object is embedded in `struct nvkm_head` and is single-open. Scanout data is not persisted; each call reads hardware state through the head function table.

## Dependencies And Integration Points

It depends on head generation hooks, display vblank event dispatch, NVIF head ABI, and kernel time sampling.

## Risks And Edge Cases

Pre-NV50 VGA paths can lack htotal/vtotal reads, so the method returns `-ENOTSUPP` to force DRM fallback. Event ABI validation is intentionally strict. Duplicate opens return `-EBUSY`.

## Test Signals

Test vblank event delivery, scanout-position monotonicity, proper `-ENOTSUPP` on unsupported legacy heads, and no stale object exposure after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uhead.c -->
