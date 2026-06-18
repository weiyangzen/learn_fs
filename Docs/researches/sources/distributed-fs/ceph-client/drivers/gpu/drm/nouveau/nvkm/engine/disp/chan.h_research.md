<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/chan.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/chan.h

Purpose: private display channel header defining `struct nvkm_disp_chan`, channel function tables, user-channel descriptors, method-list metadata, and cross-generation exported channel helpers.

Important APIs and types: `struct nvkm_disp_chan` stores callback pointers, display pointer, control/user channel IDs, head ID, object base, memory/push state, saved suspend put pointer, and optional GSP object. `struct nvkm_disp_chan_func` defines push/init/fini/intr/user/bind callbacks. `struct nvkm_disp_chan_user` binds a public class to a channel function, control ID, user ID, and optional method map. `struct nvkm_disp_chan_mthd` and `nvkm_disp_mthd_list` describe method-to-register debug maps.

Control flow: constructors in `chan.c` consume these descriptors from generation `nvkm_disp_func.user[]` arrays. Debug/error paths use method maps through `nv50_disp_chan_mthd()`.

State and persistence: no runtime state itself, but it fixes the layout and saved state fields used across all display channel generations, including `suspend_put`.

Dependencies and integration points: depends on `core/object.h`, display private state, GSP object state, and numerous generation exports (`nv50`, `gf119`, `gp102`, `gv100` channel functions and method maps).

Risks: changing struct layout or callback contracts affects every generation file. Incorrect extern declarations can silently mismatch shared method maps or channel functions during refactors.

Test signals: build coverage across all display generations plus runtime channel creation and error decoding on NV50 through Ampere-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/chan.h -->
