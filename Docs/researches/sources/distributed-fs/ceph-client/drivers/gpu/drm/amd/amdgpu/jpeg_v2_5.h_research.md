# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_5.h

Purpose: declares JPEG v2.5/v2.6 IP block exports and the v2.6 RAS poison sub-block identifiers.

Important APIs and types: `enum amdgpu_jpeg_v2_6_sub_block` names JPEG0 and JPEG1 poison status sub-blocks; `jpeg_v2_5_ip_block` and `jpeg_v2_6_ip_block` are exported for IP discovery.

Control flow and state: no runtime logic. The enum bounds drive loops in v2.6 poison-status querying.

Dependencies and integration: consumed by `jpeg_v2_5.c` and by amdgpu IP-version tables that register the correct JPEG block.

Risks and test signals: enum ordering must match the RAS status register switch in the implementation. Test signal is successful poison query coverage for both JPEG sub-blocks and correct IP block selection for Arcturus/Aldebaran-style hardware.
