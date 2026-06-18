# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_0.h

Purpose: provides JPEG v2 internal register offsets and declarations for packet emission helpers shared across multiple JPEG generations.

Important APIs and types: declares start/end, fence, IB, reg-wait, VM-flush, wreg, and NOP helper functions plus `jpeg_v2_0_ip_block`. Defines internal offsets for JRBC external register access, GPCOM, LMI BARs, VMID, IB size, RB condition wait, status, pitch, IH control, and `JRBC_DEC_EXTERNAL_REG_WRITE_ADDR`.

Control flow and state: no runtime state. The offsets are encoded into PACKETJ streams by `jpeg_v2_0.c` and reused by later generation ring function tables.

Dependencies and integration: included by JPEG v2.0 and many later JPEG implementations to avoid duplicating packet construction logic where hardware packet format remains compatible.

Risks and test signals: because later generations reuse these declarations, offset mistakes can break multiple IP blocks. Test by comparing emitted packets against hardware docs for each consumer generation and by running ring/IB tests on v2.0, v2.5, v3.0, v4.0, and v4.0.5 variants that reference these helpers.
