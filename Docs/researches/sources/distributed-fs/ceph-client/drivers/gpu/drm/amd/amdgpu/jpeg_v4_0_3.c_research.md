# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_3.c

Purpose: implements JPEG v4.0.3 for multi-instance, multi-ring hardware. It adds RRMT-aware register normalization, up to eight decode rings per instance, SR-IOV MMSCH setup for multiple rings, custom packet helpers, per-core stall reset, and richer RAS/ACA error reporting.

Important APIs and functions: exports `jpeg_v4_0_3_ip_block` and packet helpers declared in the header: emit IB/fence/VM flush/HDP flush/NOP/start/end/wreg/reg-wait. Lifecycle functions initialize ring funcs, IRQ funcs, RAS funcs, rings, register dumps, sysfs reset masks, power/clock states, and suspend/resume. Reset uses `jpeg_v4_0_3_core_stall_reset()` plus `jpeg_v4_0_3_start_jrbc()` under the paired VCN reset mutex.

Control flow and state: early init sets `num_jpeg_rings` to `AMDGPU_MAX_JPEG_RINGS_4_0_3`. SW init registers one decode IRQ source per ring plus poison IRQs, initializes rings for every `adev->jpeg.num_jpeg_inst`, assigns MMHUB by AID, calculates VF and PF doorbell layouts, and stores per-ring external scratch/pitch offsets. HW init either builds per-instance MMSCH tables for VFs or detects RRMT, programs NBIO/VCN doorbells, and ring-tests every ring. Runtime state spans `ring->me`, `ring->pipe`, `aid_id`, writeback `wptr_offs`, `adev->jpeg.caps`, and block-wide `cur_state`.

Dependencies and integration: depends on VCN 4.0.3 register headers, `mmsch_v4_0_3.h`, SOC15 offset accessors, `node_id_to_phys_map`, amdgpu JPEG/RAS/ACA infrastructure, MMHUB IP versions, and scheduler ring callbacks.

Risks and test signals: `jpeg_v4_0_3_is_idle()` initializes `ret` to false and ANDs into it, so it appears to always return false; clockgating may therefore return `-EBUSY`. `wait_for_idle()` similarly ANDs return codes starting at zero, which can mask failures. Interrupt routing depends on node ID to physical AID mapping and per-source ring mapping. Tests should cover all ring IRQ source IDs, PF and VF doorbell layouts, RRMT and non-RRMT register normalization, per-ring reset under VCN mutex, RAS count/reset paths, ACA bank parsing, and DPG/HDP flush behavior where the JPEG HDP flush is intentionally a no-op.
