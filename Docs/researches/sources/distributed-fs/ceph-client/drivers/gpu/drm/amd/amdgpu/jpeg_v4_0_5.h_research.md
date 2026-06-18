# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_5.h

Purpose: declares the JPEG v4.0.5 IP block and a single JPEG RAS sub-block enum.

Important APIs and types: `enum amdgpu_jpeg_v4_0_5_sub_block` currently contains only JPEG0 plus a max marker; `jpeg_v4_0_5_ip_block` exposes the implementation.

Control flow and state: no runtime state. The enum is not heavily used in the current v4.0.5 implementation, where poison IRQ processing is delegated to common JPEG handling.

Dependencies and integration: consumed by `jpeg_v4_0_5.c` and amdgpu IP-version selection.

Risks and test signals: the closing include-guard comment says `__JPEG_V4_0_H__`, which is cosmetic but can confuse review. Validate that IP versions 4.0.5 and 4.0.6 select this block and that future RAS code keeps enum bounds aligned with hardware sub-blocks.
