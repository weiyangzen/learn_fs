<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/chan.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/chan.c

Purpose: generic user display channel object implementation for core, head/base/window, cursor, overlay, and immediate channels. It validates NVIF channel creation arguments, maps channel MMIO, handles channel init/fini/intr, and proxies child DMA objects through RAMHT binding.

Important APIs and functions: `nvkm_disp_core_new()`, `nvkm_disp_chan_new()`, and `nvkm_disp_wndw_new()` create channels with limits based on core count, head count, or window count. `nvkm_disp_chan_new_()` selects the generation `nvkm_disp_chan_user` by class, validates `nvif_disp_chan_args`, allocates `struct nvkm_disp_chan`, optionally binds push buffers, and reserves `disp->chan[user]` under `client.lock`. Channel object callbacks provide `.init`, `.fini`, `.ntfy`, `.map`, and `.sclass`.

Control flow: init enables interrupts then calls the generation channel init callback. Fini calls generation fini then disables interrupts. Child class creation uses DMAOBJ engine classes when the channel supports `bind`; the child is wrapped in `nvkm_oproxy` so the RAMHT hash is removed in the proxy destructor.

State and persistence: each channel tracks control/user channel IDs, head/window ID, memory/push buffer, suspend put pointer, and optional GSP RM object. `disp->chan[]` is the live lookup table used by interrupt/error paths.

Dependencies and integration points: depends on NVKM object/proxy classes, RAMHT, NVIF display channel ABI, DMAOBJ engine classes, and generation-specific channel function tables from files such as `gf119.c`, `gp102.c`, and `gv100.c`.

Risks: argument validation ties push-buffer presence to channel type; wrong `ctrl`/`user` offsets can corrupt another channel. The live slot is protected by a spinlock, but hardware callbacks must tolerate concurrent interrupts and teardown. RAMHT removal must pair exactly with successful binds.

Test signals: create duplicate channels and expect `-EBUSY`, pass malformed args and unsupported versions, map channel registers, create DMAOBJ children, and exercise init/fini with suspend resume and interrupt delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/chan.c -->
