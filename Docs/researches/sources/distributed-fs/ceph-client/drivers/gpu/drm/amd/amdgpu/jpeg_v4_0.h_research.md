# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0.h

Purpose: declares JPEG v4.0 sub-block IDs used for RAS poison checks and exports the v4.0 IP block object.

Important APIs and types: `enum amdgpu_jpeg_v4_0_sub_block` identifies JPEG0 and JPEG1 RAS status sub-blocks; `jpeg_v4_0_ip_block` exposes the generation implementation.

Control flow and state: no runtime logic. The enum bounds the RAS poison-status loop in `jpeg_v4_0.c`.

Dependencies and integration: consumed by the v4.0 implementation and amdgpu IP discovery tables.

Risks and test signals: enum/register switch alignment is the main risk. Test by injecting or reading poison status for both sub-block values and verifying IP selection for JPEG 4.0.0 hardware.
