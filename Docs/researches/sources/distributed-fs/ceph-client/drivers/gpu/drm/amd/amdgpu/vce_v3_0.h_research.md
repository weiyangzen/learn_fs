# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v3_0.h

Purpose: Declares the VCE 3.x IP block descriptors implemented by `vce_v3_0.c`.

Important APIs and types: Exports `vce_v3_0_ip_block`, `vce_v3_1_ip_block`, and `vce_v3_4_ip_block`.

Control flow and integration: ASIC block tables use the matching descriptor for VCE major/minor variants while sharing the same implementation.

State and persistence: The header owns no runtime state.

Dependencies and risks: Requires matching definitions for all three descriptors. New minor variants require both a C definition and a header declaration.

Test signals: Compile/link coverage for ASIC configurations referencing any of the three VCE 3.x descriptors.
