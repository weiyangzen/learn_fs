# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/ucgrp.c

Purpose: implements the user-visible FIFO channel-group object. It parses NVIF channel-group creation arguments, resolves runlist and VMM handles, creates a hardware/software channel group, exposes channel child classes, and returns the CGID to userspace.

Important APIs and data: `struct nvkm_ucgrp`, `nvkm_ucgrp_new()`, `nvkm_ucgrp_chan_new()`, `nvkm_ucgrp_sclass()`, and `nvkm_ucgrp_dtor()`. It uses `union nvif_cgrp_args` version 0 and stores a referenced `struct nvkm_cgrp`.

Control flow: constructor validates ABI version and name length, looks up the requested runlist by id, resolves the VMM handle from the client, allocates the user object, calls `nvkm_cgrp_new(runl, name, vmm, true, &cgrp)`, and writes `args->v0.cgid`. The class enumerator exposes the FIFO channel class as a child whose constructor creates a channel inside this group.

State and persistence: holds a reference to `nvkm_cgrp` until object destruction. Runtime group state lives in the channel-group object and runlist; no durable persistence exists.

Dependencies and integration: depends on `nvkm_runl_get()`, `nvkm_uvmm_search()`, `nvkm_cgrp_new()`, `nvkm_uchan_new()`, MMU/VMM handles, and the FIFO function table's channel class.

Risks: ABI validation is strict; missing runlist/VMM returns errors; exposing only one child channel class means class table correctness depends on `fifo->func->chan.user`; failure after object construction relies on object cleanup.

Test signals: NVIF channel-group creation with valid/invalid runlist and VMM handles, returned CGID, child channel class enumeration, group destruction releasing references, and channel creation within the group.
