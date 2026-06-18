# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_0.h

Purpose: declares JPEG v5.0.0 DPG/SOC24 register offsets and exports the v5.0.0 IP block object.

Important APIs and types: defines DPG register offsets for JPEG CGC gate/control, system interrupt enable, no-op, and decode GFX10 address config. Exports `jpeg_v5_0_0_ip_block`.

Control flow and state: no runtime state. Constants are consumed by v5 DPG start code to write directly or to append indirect SRAM commands.

Dependencies and integration: included by `jpeg_v5_0_0.c` and amdgpu IP discovery tables.

Risks and test signals: these hard-coded offsets are critical for DPG mode. Tests should cover direct and indirect DPG register programming and confirm the offsets match VCN 5.0 hardware packet/SRAM expectations.
