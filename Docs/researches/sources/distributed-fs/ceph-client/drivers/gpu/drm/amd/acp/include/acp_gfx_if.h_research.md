# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/acp/include/acp_gfx_if.h

Purpose: declares the ACP-to-amdgpu graphics interface used to initialize ACP hardware support.

Important APIs/types/functions: includes `cgs_common.h` and declares `amd_acp_hw_init(struct cgs_device *cgs_device, unsigned acp_version_major, unsigned acp_version_minor)`.

Control flow: no executable flow; callers include this header and call the implementation in `acp_hw.c`.

State/persistence: no state beyond the opaque `struct cgs_device` dependency.

Dependencies/integration: depends on Linux types and AMD CGS common definitions; the amdgpu Makefile adds the ACP include directory.

Risks: changes to CGS or ACP versioning require synchronized caller/implementation updates.

Test signals: amdgpu ACP-enabled compile coverage and runtime validation through `amd_acp_hw_init()`.
