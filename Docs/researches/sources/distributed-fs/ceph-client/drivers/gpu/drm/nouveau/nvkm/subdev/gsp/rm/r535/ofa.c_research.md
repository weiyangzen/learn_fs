# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/ofa.c

Purpose: provides the R535 RM engine allocator for OFA objects.

Important API: `r535_ofa_alloc()` allocates an `NV_OFA_ALLOCATION_PARAMETERS` payload using the parent channel, handle, class, and destination object. It sets only `args->size` and commits with `nvkm_gsp_rm_alloc_wr()`. The `r535_ofa` API table exposes this as `.alloc`.

Control flow and state: the function is stateless and ignores its `inst` parameter because the R535 OFA ABI payload has no instance field. The allocated `nvkm_gsp_object` becomes the persistent handle on success.

Dependencies and integration: depends on `rm/engine.h` and `nvrm/ofa.h`, and is selected through `r535_api.ofa`. It integrates with FIFO/engine discovery that decides whether an OFA object should be allocated.

Risks and tests: the unused instance argument is notable. It matches R535 payload shape, but multi-OFA support requires newer ABI handling. Test signals are successful OFA allocation on supported GPUs and no invalid-instance assumptions when RM reports OFA engines.
