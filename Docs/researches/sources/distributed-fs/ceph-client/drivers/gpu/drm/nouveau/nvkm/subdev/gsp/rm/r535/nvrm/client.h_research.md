# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/client.h

Purpose: defines the R535 RM root client class and allocation payload.

Important definitions: `NV01_ROOT` is the RM class for a root client. `NV_PROC_NAME_MAX_LENGTH` bounds process-name storage. `NV0000_ALLOC_PARAMETERS` begins with `hClient`, then carries `processID` and `processName`.

Control flow and state: no code is present. The root client allocation initializes the top-level RM namespace for all later device, subdevice, event, VAS, channel, and engine objects.

Dependencies and integration: consumed by client constructors in the RM API, and indirectly by `nvkm_gsp_client_device_ctor()` used in VMM, display, and engine paths. The R570 client implementation in this work item uses the analogous R570 header and shows the pattern.

Risks and tests: `hClient` must remain the first member per the source comment; changing that would break RM allocation parsing. Test signals are basic GSP client creation, object handle allocation, and cleanup without leaked IDR entries.
