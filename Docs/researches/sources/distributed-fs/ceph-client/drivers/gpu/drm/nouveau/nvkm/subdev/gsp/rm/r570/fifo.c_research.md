# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/fifo.c

Purpose: implements R570 FIFO RM API callbacks for channel allocation, RC event handling, constructed-falcon context sizing, and RM engine-type translation.

Important APIs: `r570_chan_alloc()` fills `NV_CHANNELGPFIFO_ALLOCATION_PARAMETERS` for a physical GPFIFO channel, including GP FIFO offset/entries, dense `NVOS04_FLAGS`, fixed USERD page/index based on `CHID_PER_USERD`, VAS handle, engine type, instance/UserD/RAMFC/method-buffer descriptors, privilege, and notifier types. `r570_fifo_rc_triggered()` logs R570 RC payload fields including GFID, exception level, MMU fault address/type, and calls `r535_fifo_rc_chid()` to mark the affected channel. `r570_fifo_ectx_size()` reads `NV2080_CTRL_CMD_GPU_GET_CONSTRUCTED_FALCON_INFO` and updates matching `engn->rm.size` by `engDesc`. `r570_fifo_xlat_rm_engine_type()` maps R570 `RM_ENGINE_TYPE_*` values to Nouveau subdevice type and NV2080 engine type, extending copy engines through COPY19, NVENC3, and OFA1. `r570_fifo` exports these callbacks and sets `.rsvd_chids = 1`.

Control flow and state: channel allocation constructs persistent RM channel objects using Nouveau-allocated memory addresses. Engine context sizing iterates the returned constructed-falcon table and then all runlists/engines to update per-engine RM context buffer sizes. Engine translation returns the Nouveau instance as the function return value and writes type/NV2080 type through output pointers.

Dependencies and integration: includes RM, MMU, FIFO private channel/runlist headers, `nvhw/drf.h`, R570 FIFO and engine headers, and reuses R535 RC CHID handling. It feeds GR and other engine channel setup through `rm->api->fifo->chan.alloc`.

Risks: channel flag construction is bitfield-heavy; a wrong flag can affect privilege, USERD placement, scheduling, or method-buffer setup. Address-space/cache attributes are hard-coded (`2/1` for instance/UserD/RAMFC and `1/0` for method buffer), so they must match actual memory placement. Engine translation must stay aligned with R570 headers or engines will be missing/misclassified. The RC handler assumes the R570 payload size and field names, which differ from R535.

Test signals: create user and privileged channels on GR/CE/video engines, verify USERD placement by CHID, submit workloads, provoke or simulate RC events, check constructed falcon sizes populate matching engines, and validate discovery of COPY10-19, NVENC3, and OFA1 where present.
