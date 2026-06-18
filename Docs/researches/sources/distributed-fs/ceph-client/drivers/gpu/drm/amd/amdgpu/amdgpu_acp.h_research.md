<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acp.h

## Purpose
`amdgpu_acp.h` defines the internal ACP state embedded in `struct amdgpu_device` and declares the ACP IP block descriptor. It is the local interface between the amdgpu core device object and the ACP IP-block implementation in `amdgpu_acp.c`.

## Important APIs, types, and functions
- `struct amdgpu_acp` stores the parent device, CGS device, ACP private pointer, MFD cells, resources, and PM-domain pointer.
- `extern const struct amdgpu_ip_block_version acp_ip_block;` exposes ACP 2.2 IP callbacks for the IP manager.

## Control flow
The header has no runtime flow. Runtime users access `adev->acp` fields during ACP `sw_init`, `hw_init`, `hw_fini`, suspend/resume, and power-gating callbacks.

## State and persistence behavior
The struct fields describe runtime-owned kernel resources. `cgs_device`, `acp_cell`, `acp_res`, and `acp_genpd` are allocated and freed by the ACP implementation. No persistent state is defined here.

## Dependencies and integration points
The header includes `<linux/mfd/core.h>` for `struct mfd_cell`. It is included from `amdgpu.h`, so the ACP state becomes part of the central device structure when `CONFIG_DRM_AMD_ACP` is enabled.

## Risks and edge cases
Because the struct stores raw resource pointers, init/fini ordering must ensure fields are either valid or null when callbacks run. Adding fields here changes `struct amdgpu_device` layout through the embedded ACP member.

## Test signals
Compile with `CONFIG_DRM_AMD_ACP`, successful ACP IP-block registration, and clean probe/remove with no dangling ACP pointers are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acp.h -->
