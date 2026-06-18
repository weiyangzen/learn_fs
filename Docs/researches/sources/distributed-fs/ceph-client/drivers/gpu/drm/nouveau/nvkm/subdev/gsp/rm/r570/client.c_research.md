# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/client.c

Purpose: implements the R570 root-client constructor for GSP-RM.

Important API: `r570_gsp_client_ctor()` allocates an `NV01_ROOT` object using `NV0000_ALLOC_PARAMETERS`, sets `hClient` to the object's handle and `processID` to `~0`, then commits the allocation. `r570_client` exposes this as `.ctor`.

Control flow and state: the constructor operates on `client->object` as both parent and destination, which is normal for a root object. On success, the client handle becomes the root for later RM allocations under this client. No process name is set in the zeroed payload.

Dependencies and integration: includes `rm/rm.h` and R570 `nvrm/client.h`. It is selected by the R570 API table and used wherever Nouveau creates a GSP client/device pair.

Risks and tests: the R570 root-client ABI may differ from R535, so using the matching header is important. Test signals are successful root client creation, follow-on device/subdevice allocations, and cleanup without leaked client handles.
