# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/alloc.h

Purpose: defines the R535 RM allocation and free RPC payload headers used by Nouveau's generic GSP RM object helpers. The file is an ABI excerpt from NVIDIA's open GPU kernel modules and must match firmware expectations.

Important types: `rpc_gsp_rm_alloc_v03_00` carries `hClient`, `hParent`, `hObject`, `hClass`, status, payload size, flags, reserved bytes, and a flexible `params[]` area. `NVOS00_PARAMETERS_v03_00` describes free parameters with root, parent, old object handle, and status. `rpc_free_v03_00` wraps the free parameters.

Control flow and state: this header has no executable logic. Runtime state lives in RM objects and the flexible parameter payload that callers allocate, fill, and send through `NV_VGPU_MSG_FUNCTION_GSP_RM_ALLOC` or free paths.

Dependencies and integration: included by RM allocation helpers that build object creation RPCs for clients, devices, channels, engines, and memory objects. It depends on `nvrm/nvtypes.h` for fixed-width RM types and alignment macros.

Risks and tests: because the status and flexible-array layout is protocol-owned, padding or field order changes would corrupt every RM allocation. Test signals are broad: all GSP object creation paths, free paths, and error-status translation should work across root, device, subdevice, engine, and memory allocations.
