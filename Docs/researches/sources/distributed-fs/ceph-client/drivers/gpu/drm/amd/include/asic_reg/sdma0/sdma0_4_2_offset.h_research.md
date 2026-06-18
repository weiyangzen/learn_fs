# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_2_offset.h

## Purpose

`sdma0_4_2_offset.h` is a generated AMDGPU register-offset header for the SDMA0 hardware block in the SDMA 4.2 register family. It defines symbolic register offsets such as `mmSDMA0_UCODE_ADDR`, `mmSDMA0_GFX_RB_CNTL`, `mmSDMA0_PAGE_RB_CNTL`, and `mmSDMA0_RLC0_RB_CNTL` through `mmSDMA0_RLC7_MIDCMD_CNTL`, plus a matching `_BASE_IDX` macro for each register. The file is protected by `_sdma0_4_2_0_OFFSET_HEADER` and describes one address block, `sdma0_sdma0dec`, with a documented base address of `0x4980`.

The header is not executable code. Its role is to give the driver stable names for memory-mapped SDMA0 register offsets. Runtime code combines these offsets with per-IP/per-instance base addresses, then uses `RREG32`, `WREG32`, `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, and related helpers to read, write, dump, and program SDMA hardware.

## Important APIs, Types, And Macros

There are no C functions or types in this file. The public surface is entirely preprocessor macros:

- Core engine and firmware registers: `mmSDMA0_UCODE_ADDR`, `mmSDMA0_UCODE_DATA`, `mmSDMA0_UCODE_CHECKSUM`, `mmSDMA0_CNTL`, `mmSDMA0_F32_CNTL`, `mmSDMA0_STATUS_REG`, `mmSDMA0_STATUS1_REG`, `mmSDMA0_STATUS2_REG`, `mmSDMA0_STATUS3_REG`, `mmSDMA0_POWER_CNTL`, `mmSDMA0_CLK_CTRL`, `mmSDMA0_FREEZE`, and related diagnostic/perf registers.
- VM, virtualization, and MMHUB registers: `mmSDMA0_VM_CNTL`, `mmSDMA0_VM_CTX_LO`, `mmSDMA0_VM_CTX_HI`, `mmSDMA0_VM_CTX_CNTL`, `mmSDMA0_ACTIVE_FCN_ID`, `mmSDMA0_VIRT_RESET_REQ`, `mmSDMA0_VF_ENABLE`, `mmSDMA0_MMHUB_CNTL`, and context/public register type tables.
- Translation/cache and fault-related registers: `mmSDMA0_UTCL1_CNTL`, `mmSDMA0_UTCL1_WATERMK`, `mmSDMA0_UTCL1_RD_STATUS`, `mmSDMA0_UTCL1_WR_STATUS`, `mmSDMA0_UTCL1_INV*`, `mmSDMA0_UTCL1_*_XNACK*`, `mmSDMA0_UTCL1_TIMEOUT`, and `mmSDMA0_UTCL1_PAGE`.
- Main GFX SDMA queue registers: `mmSDMA0_GFX_RB_CNTL`, `mmSDMA0_GFX_RB_BASE`, `mmSDMA0_GFX_RB_BASE_HI`, `mmSDMA0_GFX_RB_RPTR`, `mmSDMA0_GFX_RB_WPTR`, writeback-address registers, IB registers, doorbell registers, context status, preemption, CSA, watermark, and mid-command save/restore slots.
- Page queue registers: the `mmSDMA0_PAGE_*` group mirrors the GFX queue shape for paging work.
- Compute/RLC queue registers: `mmSDMA0_RLC0_*` through `mmSDMA0_RLC7_*` repeat a per-queue layout for up to eight RLC queues. Each queue includes RB, IB, skip, context status, doorbell, status, CSA, preempt, AQL control, minor pointer update, and mid-command data/control registers.
- Reliability and diagnostics registers: `mmSDMA0_EDC_CONFIG`, `mmSDMA0_EDC_COUNTER`, `mmSDMA0_EDC_COUNTER_CLEAR`, `mmSDMA0_ERROR_LOG`, `mmSDMA0_GPU_IOV_VIOLATION_LOG`, and performance counter registers.

Each offset macro is paired with `<macro>_BASE_IDX`, which is `0` throughout this header. The offset values are register-index offsets, not full CPU virtual addresses. Driver code must add the correct hardware block base address.

## Control Flow

This header has no internal control flow. Its control-flow impact appears in consumers, especially `drivers/gpu/drm/amd/amdgpu/sdma_v4_0.c`, which includes `sdma0/sdma0_4_2_offset.h` and `sdma0/sdma0_4_2_sh_mask.h`.

The main access path in `sdma_v4_0.c` is:

1. SDMA code calls `RREG32_SDMA(instance, offset)` or `WREG32_SDMA(instance, offset, value)`.
2. Those macros call `sdma_v4_0_get_reg_offset(adev, instance, offset)`.
3. `sdma_v4_0_get_reg_offset()` selects `adev->reg_offset[SDMA*_HWIP][...][...]` for the active SDMA instance and adds the offset from this header.
4. The resulting absolute register index is used for MMIO reads/writes.

Examples of runtime flows that depend on these offsets:

- Firmware loading halts SDMA, writes `mmSDMA0_UCODE_ADDR` to zero, streams firmware dwords through `mmSDMA0_UCODE_DATA`, then writes the firmware version back to `mmSDMA0_UCODE_ADDR`.
- Engine start/resume configures GFX and page rings through the `GFX_*` and `PAGE_*` RB/IB/base/read-pointer/write-pointer/doorbell registers, toggles `*_MINOR_PTR_UPDATE` around write-pointer programming, enables RB and IB bits via the paired shift/mask header, and tests the rings.
- Golden-register initialization for SDMA 4.2 uses constants such as `mmSDMA0_CHICKEN_BITS`, `mmSDMA0_CLK_CTRL`, `mmSDMA0_GB_ADDR_CONFIG`, `mmSDMA0_GFX_RB_WPTR_POLL_CNTL`, `mmSDMA0_RLC*_RB_WPTR_POLL_CNTL`, and `mmSDMA0_UTCL1_TIMEOUT`.
- Interrupt setup and handling toggles `mmSDMA0_CNTL` trap bits, `mmSDMA0_EDC_CONFIG` ECC interrupt bits, and later processes fences or RAS data based on IH entries.
- Idle checks poll `mmSDMA0_STATUS_REG` for the idle bit across every SDMA instance.
- IP state dumping uses `sdma_reg_list_4_0`, populated with many `mmSDMA0_*` offsets, to snapshot and print SDMA register values after faults or debug requests.

## State And Persistence Behavior

The header itself holds no mutable state and persists no data. It defines compile-time constants that encode the hardware register layout. The state they address lives in the GPU:

- Firmware microcode state in the ucode address/data/checksum registers.
- Ring buffer state in RB base, RPTR/WPTR, writeback address, doorbell, and enable registers.
- IB execution state in IB base/size/rptr/offset registers.
- Context-switch and preemption state in `mmSDMA0_CNTL`, phase quantum registers, `*_CONTEXT_STATUS`, `*_PREEMPT`, `*_CSA_ADDR_*`, and mid-command registers.
- MMU/cache/fault state in VM and UTCL1 registers.
- Error counters and logs in EDC, error-log, and GPU IOV violation registers.
- Clock/power state in `mmSDMA0_CLK_CTRL`, `mmSDMA0_POWER_CNTL`, power gating FSM registers, and ULV controls.

Persistence across suspend/resume or reset is handled by the surrounding AMDGPU lifecycle, not by this header. `sdma_v4_0_hw_init()` reprograms golden registers and restarts rings. `sdma_v4_0_suspend()`/`sdma_v4_0_resume()` either disable/re-enable SDMA or rely on SMU state save/restore for S0ix. Diagnostic state can be copied to `adev->sdma.ip_dump`, which is allocated in software init and populated by reading offsets from this header.

## Dependencies

This header depends only on the C preprocessor. Effective use requires the broader AMDGPU register infrastructure:

- Matching field definitions in `sdma0/sdma0_4_2_sh_mask.h`; offset macros locate registers, while shift/mask macros locate fields within those registers.
- SDMA sibling headers such as `sdma1_4_2_offset.h` and `sdma*_4_2_2_offset.h` for other instances on multi-SDMA ASICs.
- SOC15 register helpers and IP base tables, including `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, `SOC15_REG_GOLDEN_VALUE`, `RREG32`, `WREG32`, and `adev->reg_offset`.
- AMDGPU SDMA structures and lifecycle code in `amdgpu_device`, `amdgpu_sdma_instance`, `amdgpu_ring`, IRQ sources, RAS data, firmware loading, and VM/PT update paths.
- Packet-building headers such as `vega10_sdma_pkt_open.h` for command-stream content. Those packets are submitted through rings configured using the register offsets in this file.

## Integration Points

The most direct integration point is `amdgpu/sdma_v4_0.c`, which includes the header and uses its macros in:

- Golden settings arrays for SDMA 4.0, 4.1, 4.2, Arcturus, Aldebaran, and related ASIC variants.
- `sdma_reg_list_4_0` for debug/IP-dump register selection.
- `sdma_v4_0_get_reg_offset()` callers through `RREG32_SDMA` and `WREG32_SDMA`.
- Ring initialization/resume paths for GFX and page queues.
- Firmware upload through SDMA ucode registers.
- Clock-gating, light-sleep, power-gating, ULV, context-switch, and idle logic.
- RAS error count reads from `mmSDMA0_EDC_COUNTER` and ECC interrupt control via `mmSDMA0_EDC_CONFIG`.

Other AMDGPU paths indirectly rely on the same register namespace when they configure doorbells, process SDMA interrupts, dump device state, or map queue state for KFD/compute integration. The file also aligns with generated SDMA0 headers for adjacent versions; keeping its numeric layout coherent with `sdma0_4_2_sh_mask.h`, SDMA1 equivalents, and ASIC IP base tables is essential.

## Risks

- A wrong offset silently targets the wrong MMIO register. Consequences can include failed firmware load, broken ring submission, invalid doorbell routing, GPU hangs, VM faults, or corrupted diagnostics.
- Offsets are tightly coupled to ASIC register layout. Reusing this 4.2 header for a non-compatible SDMA version can misprogram hardware even if field names compile.
- `*_BASE_IDX` values are all `0`; if a future generated layout needs different base indices, consumers that assume the current pattern could miss required base selection changes.
- The repeated `GFX`, `PAGE`, and `RLC0` through `RLC7` layouts make copy/paste and generation errors easy to overlook. Queue stride assumptions in KFD and SDMA code depend on these register groups remaining regular.
- Field manipulation requires the matching shift/mask header. Offset changes without synchronized mask changes can compile but write incorrect bits.
- Fault/debug paths read many registers after errors; stale or incorrect offsets can obscure the real failure by producing misleading dumps.

## Test Signals

Useful validation signals for this header are mostly integration and hardware-facing:

- The driver builds with `sdma_v4_0.c` including this header and `sdma0_4_2_sh_mask.h`, with no missing or duplicate register macro errors.
- SDMA firmware loading succeeds on SDMA 4.2 hardware; failures around `mmSDMA0_UCODE_ADDR`/`DATA` are strong offset-regression indicators.
- `amdgpu_ring_test_helper()` succeeds for each SDMA GFX ring and page ring after `sdma_v4_0_start()`.
- `sdma_v4_0_ring_test_ring()` and `sdma_v4_0_ring_test_ib()` write the expected sentinel value through SDMA command streams before timeout.
- Idle polling through `mmSDMA0_STATUS_REG` reaches the `IDLE` state during `wait_for_idle`.
- Doorbell tests and normal command submission do not produce `SDMA_DOORBELL_INVALID`, VM hole, polling timeout, or SRBM write protection interrupts.
- RAS/ECC paths can enable interrupts with `mmSDMA0_EDC_CONFIG`, read `mmSDMA0_EDC_COUNTER`, and reset or harvest counts as expected.
- IP dump output includes plausible values for `STATUS`, `RB`, `IB`, `UTCL1`, and VM registers across every active SDMA instance.
