## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_nbio.h

Purpose: declares NBIO hardware callback interfaces, HDP flush register masks, NBIO RAS state, and helper APIs for RAS and PCIe replay counters.

Important APIs/types: `struct nbio_hdp_flush_reg` stores per-engine HDP flush reference/mask values. `struct amdgpu_nbio_ras` wraps a RAS block plus optional no-BIF-ring interrupt handlers and init hooks. `struct amdgpu_nbio_funcs` is the large NBIO vtable for HDP offsets, PCIe index/data offsets, revision/memsize, doorbell ranges for SDMA/VPE/VCN/GC/IH, doorbell aperture/interrupt control, clock gating/light sleep, IH control, register init/remap, ASPM/link workarounds, ROM offset, compute/memory partition mode, NPS switch request, replay count, and register remap. `struct amdgpu_nbio` stores HDP regs, RAS IRQ sources, RAS interface, funcs, and RAS object.

Control flow contract: ASIC-specific NBIO code installs function table and RAS object. Common MES HDP flush and other subsystems call offset functions; doorbell users call range callbacks; RAS code uses `amdgpu_nbio_ras_sw_init()` and `amdgpu_nbio_ras_late_init()`.

State and persistence: runtime callback pointers, RAS IRQ sources, and RAS interface live in `adev->nbio`. Hardware counters and partition modes are queried live.

Dependencies/integration: NBIO connects PCIe, doorbells, IH, HDP flush, partitioning, ASPM, RAS, and MES/KMS/user queue subsystems.

Risks: the vtable is broad and many callbacks are mandatory for a given ASIC even though the type allows nulls. Doorbell range programming must stay consistent with MES/user queue doorbell allocation. Replay count support checks must match actual firmware/hardware capability.

Test signals: doorbell aperture/range programming, IH doorbells, ASPM/link workarounds, HDP flush via MES, partition mode queries, RAS IRQ setup, and PCIe replay count reads.
