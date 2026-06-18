# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v6_0.h

Purpose: Declares UVD 6.x IP block descriptors backed by the shared UVD 6.0 implementation.

Important APIs and types: Exports `uvd_v6_0_ip_block`, `uvd_v6_2_ip_block`, and `uvd_v6_3_ip_block`.

Control flow and integration: ASIC tables can select the correct major/minor descriptor while reusing the same C implementation and function table.

State and persistence: No direct state; descriptor definitions live in `uvd_v6_0.c`.

Dependencies and risks: Inclusion assumes the AMDGPU IP block type is declared. Adding a new 6.x descriptor requires matching declaration and definition.

Test signals: Compile/link tests for all three exported descriptor symbols.
