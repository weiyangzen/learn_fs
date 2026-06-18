# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v3_0.h

Purpose: declares the JPEG v3.0 IP block version object.

Important APIs and types: exports `jpeg_v3_0_ip_block` for amdgpu IP discovery and registration.

Control flow and state: no runtime behavior or state.

Dependencies and integration: included by IP-version selection code that wires VCN/JPEG 3.x hardware to `jpeg_v3_0.c`.

Risks and test signals: the header is minimal; the key validation is that the right ASIC/IP version selects this block and links the `jpeg_v3_0_ip_funcs` lifecycle.
