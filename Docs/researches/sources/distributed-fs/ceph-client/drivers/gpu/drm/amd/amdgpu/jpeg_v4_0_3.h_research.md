# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_3.h

Purpose: declares JPEG v4.0.3 internal packet offsets, RAS sub-block IDs, the IP block export, and packet helper APIs reused by v4.0.3 and newer implementations.

Important APIs and types: defines internal offsets for JRBC external register access, GPCOM, LMI BARs, VMID, IB size, status, scratch/pitch, and MCM addressing. Declares `jpeg_v4_0_3_dec_ring_emit_ib()`, `_emit_fence()`, `_emit_vm_flush()`, `_ring_emit_hdp_flush()`, `_nop()`, `_insert_start()`, `_insert_end()`, `_emit_wreg()`, and `_emit_reg_wait()`.

Control flow and state: no state. The declarations form a shared packet-emission ABI inside the driver; v5.0.0 uses several of these helpers.

Dependencies and integration: included by `jpeg_v4_0_3.c` and `jpeg_v5_0_0.c`, plus generation registration code via `jpeg_v4_0_3_ip_block`.

Risks and test signals: helper declarations make v4.0.3 offset semantics visible to later generations, so changes can regress v5.0.0 packet emission. Validate emitted packet sizes and offsets on v4.0.3 and v5.0.0 rings, especially VM flush/reg-wait normalization and fence DW counts.
