# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/acp/Makefile

Purpose: defines the ACP hardware object list consumed by the amdgpu build.

Important APIs/types/functions: sets `AMD_ACP_FILES := $(AMDACPPATH)/acp_hw.o`.

Control flow: the parent amdgpu Makefile defines `AMDACPPATH`, includes this file when `DRM_AMD_ACP` is enabled, and appends `$(AMD_ACP_FILES)` to `amdgpu-y`.

State/persistence: build-time variable state only.

Dependencies/integration: integrates `acp_hw.o` into the monolithic `amdgpu.o`.

Risks: relative path variables must stay aligned with the parent Makefile; source renames require updates.

Test signals: build amdgpu with `DRM_AMD_ACP=y` and confirm `../acp/acp_hw.o` is included.
