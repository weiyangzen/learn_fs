
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv2a.c

Purpose: NV2A/Xbox-derived GR variant using NV20 context infrastructure with NV2A-specific context defaults and supported classes.

Important APIs/types/functions: `nv2a_gr_new()` calls `nv20_gr_new_()`. Local `nv2a_gr_chan_new()` allocates and seeds context memory, while lifecycle hooks are the shared `nv20_gr_chan_*` functions. Runtime init/intr/tile paths are inherited from NV20.

Control flow/state: the file initializes per-channel instance-memory state; channel table and hardware context selection are managed by `nv20.c`.

Dependencies/integration: depends on `nv20.h`, `regs.h`, GPU object allocation, and FIFO channel IDs. Risks are platform-specific magic defaults and class exposure mismatches. Test signals are channel construction, Kelvin/Celsius class operation if supported, and stable suspend/resume or channel teardown.
