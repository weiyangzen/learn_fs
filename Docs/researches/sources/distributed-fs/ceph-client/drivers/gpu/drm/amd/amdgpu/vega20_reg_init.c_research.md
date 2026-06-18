# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega20_reg_init.c

## Purpose

`vega20_reg_init.c` initializes Vega20-specific register base tables and doorbell index assignments inside `struct amdgpu_device`. These values are foundational configuration used by SOC15 register access macros and by IP blocks that need doorbell slots, including graphics, SDMA, IH, UVD/VCE, VCN, and non-CP clients.

## Important APIs, Types, And Functions

The file defines two functions:

- `int vega20_reg_base_init(struct amdgpu_device *adev)`: fills `adev->reg_offset[HWIP][instance]` for every `i < MAX_INSTANCE` using base arrays from `vega20_ip_offset.h`.
- `void vega20_doorbell_index_init(struct amdgpu_device *adev)`: fills `adev->doorbell_index` with Vega20 doorbell constants such as KIQ, MEC rings, user queue range, graphics ring, SDMA engine slots, IH, UVD/VCE, VCN, first/last non-CP, maximum assignment, and SDMA doorbell range.

Important data touched:

- `adev->reg_offset` indexed by hardware IP IDs: `GC_HWIP`, `HDP_HWIP`, `MMHUB_HWIP`, `ATHUB_HWIP`, `NBIO_HWIP`, `MP0_HWIP`, `MP1_HWIP`, `UVD_HWIP`, `VCE_HWIP`, `DF_HWIP`, `DCE_HWIP`, `OSSSYS_HWIP`, `SDMA0_HWIP`, `SDMA1_HWIP`, `SMUIO_HWIP`, `NBIF_HWIP`, `THM_HWIP`, `CLK_HWIP`, `UMC_HWIP`, and `RSMU_HWIP`.
- `adev->doorbell_index` fields including `kiq`, `mec_ring0..7`, `userqueue_start/end`, `gfx_ring0`, `sdma_engine[0..7]`, `ih`, `uvd_vce.*`, `vcn.*`, `first_non_cp`, `last_non_cp`, `max_assignment`, and `sdma_doorbell_range`.

## Control Flow

`vega20_reg_base_init()` performs a simple loop over hardware instances. For each instance, it assigns each supported hardware IP's register offset pointer to the corresponding `*_BASE.instance[i]` data from `vega20_ip_offset.h`. It returns zero unconditionally.

`vega20_doorbell_index_init()` is straight-line initialization. It copies predefined `AMDGPU_VEGA20_DOORBELL*` constants into the device doorbell-index structure. The function shifts `AMDGPU_VEGA20_DOORBELL_MAX_ASSIGNMENT` left by one for `max_assignment`, consistent with 32-bit doorbell indexing where some constants are 64-bit doorbell slots.

## State And Persistence Behavior

The file mutates runtime device initialization state only. It does not allocate memory, perform MMIO, access hardware directly, or persist anything to disk.

The assigned register-offset pointers persist for the lifetime of the `amdgpu_device` and are consumed by SOC15 access helpers. Doorbell indexes similarly persist as the canonical slot map used by later IP blocks. For example, `vega20_ih.c` derives IH doorbell indices from `adev->doorbell_index.ih`.

## Dependencies

The file includes `amdgpu.h`, `soc15.h`, `soc15_common.h`, and `vega20_ip_offset.h`. It depends on:

- `MAX_INSTANCE` and hardware IP enum indexes.
- Generated Vega20 base structures such as `GC_BASE`, `HDP_BASE`, `OSSSYS_BASE`, `SDMA0_BASE`, and `RSMU_BASE`.
- Vega20 doorbell constants such as `AMDGPU_VEGA20_DOORBELL_IH`, `AMDGPU_VEGA20_DOORBELL_sDMA_ENGINE0`, and `AMDGPU_VEGA20_DOORBELL64_VCN0_1`.
- `struct amdgpu_device` layout for `reg_offset` and `doorbell_index`.

## Integration Points

Repository references show `vega20_reg_base_init()` is called from SOC15/device discovery initialization paths before IP blocks rely on SOC15 register offsets. The IH implementation relies on the `ih` doorbell index assigned here. SDMA, graphics, compute, media, and user queue code rely on their assigned doorbell ranges to ring hardware queues without colliding.

The `NBIF_HWIP` register offset deliberately aliases `NBIO_BASE`, which reflects naming compatibility between NBIO/NBIF users in the driver. SDMA doorbell range is set to `20`, affecting how many doorbell slots are reserved for SDMA engines.

## Risks

- Incorrect register base pointers break all `SOC15_REG_OFFSET` users for the affected hardware IP and can lead to wrong MMIO addresses.
- Doorbell index collisions can cause one engine to ring another engine's queue or corrupt interrupt/read-pointer behavior.
- The comment contains typos, but the functional risk is in the hard-coded hardware map staying synchronized with generated Vega20 offset headers and ASIC variants.
- The function returns success unconditionally; there is no runtime validation that generated base tables are present or sized as expected.
- `max_assignment` uses a left shift. Changing doorbell units elsewhere without updating this function could cause off-by-one or unit mismatches.

## Test Signals

Useful validation signals:

- Early boot logs should show successful SOC15 register access after `vega20_reg_base_init()`.
- IP block initialization for GC, SDMA, IH, NBIO, OSSSYS, and media blocks should not fail due to invalid register offsets.
- Doorbell-based queue submission should work for KIQ, MEC rings, graphics, SDMA engines, IH read pointers, and media rings.
- Interrupt handling tests indirectly verify the IH doorbell assignment.
- Multi-engine SDMA workloads help verify `sdma_engine[0..7]` and `sdma_doorbell_range`.
- Static comparison against generated Vega20 offset and doorbell specification headers can catch drift.
