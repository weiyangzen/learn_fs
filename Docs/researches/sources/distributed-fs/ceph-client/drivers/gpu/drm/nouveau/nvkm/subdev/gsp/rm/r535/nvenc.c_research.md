# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvenc.c

Purpose: provides the R535 RM engine allocator for NVENC/MSENC video encode engine objects. It is a small adapter from Nouveau's engine allocation API to `NV_MSENC_ALLOCATION_PARAMETERS`.

Important API: `r535_nvenc_alloc()` obtains an RM alloc RPC buffer using the parent channel, requested object handle, class, payload size, and destination object. It sets `size` and `engineInstance`, then sends the allocation. The exported `r535_nvenc` table installs this allocator.

Control flow and state: the allocator has no persistent local state. Success initializes the supplied `nvkm_gsp_object` through the shared RM allocation helper; failure leaves the caller responsible for unwinding any broader channel setup. The `prohibitMultipleInstances` field in the ABI payload is left at zero from the zeroed allocation buffer, meaning this implementation does not request single-instance enforcement.

Dependencies and integration: selected through `r535_api.nvenc` and consumed by higher-level Nouveau engine/channel setup. It depends on the R535 header definition matching the firmware's expected MSENC allocation structure.

Risks and tests: ABI drift in `NV_MSENC_ALLOCATION_PARAMETERS` or incorrect instance mapping can break encode object creation. Validation should allocate NVENC objects across advertised instances and run encode workloads while checking for GSP RM allocation failures and RC events.
