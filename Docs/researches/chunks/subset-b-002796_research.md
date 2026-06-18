# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_sh_mask.h lines 9715-10331

## Scope

This chunk is the final section of the generated MMHUB 2.3.0 shift/mask header. It starts in the middle of the `MMVM_INVALIDATE_ENG6_REQ` field definitions and continues through:

- `MMVM_INVALIDATE_ENG6` through `MMVM_INVALIDATE_ENG17` acknowledgement, address-range, and reserved-register field masks.
- Full invalidation request field masks for engines 7 through 17.
- The `mmhub_mmutcl2_mml2tlbpfdec` address block, currently represented here by `MML2TLB_TLB0_STATUS`.
- The `mmhub_mmutcl2_mml2tlbpldec` performance-counter configuration and result-control masks.
- The `mmhub_mmutcl2_mml2tlbprdec` performance-counter result low/high masks.
- The closing `#endif` for `_mmhub_2_3_0_SH_MASK_HEADER`.

The source file is a generated hardware register bitfield map. This chunk defines preprocessor constants only; it contains no C functions, structs, runtime variables, or executable branches.

## Purpose

The header provides the bit-level ABI used by AMDGPU code when it composes or decodes MMHUB 2.3.0 MMIO register values. The conventional macro pairs are:

- `<REGISTER>__<FIELD>__SHIFT`, the field bit offset.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask for that field.

The sibling `mmhub_2_3_0_offset.h` file supplies register addresses such as `mmMMVM_INVALIDATE_ENG0_REQ`, `mmMMVM_INVALIDATE_ENG0_ACK`, and `mmMMVM_INVALIDATE_ENG0_ADDR_RANGE_LO32`; this file supplies field layout. The direct runtime consumer for this ASIC generation is `amdgpu/mmhub_v2_3.c`, which includes this header and uses the masks through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.

## Important Macro Families

### MMVM Invalidate Engine Fields

The `MMVM_INVALIDATE_ENGn` family describes per-engine VM/TLB invalidation register layouts. The covered chunk starts after the shift definitions for `MMVM_INVALIDATE_ENG6_REQ`, so its first visible entries are the remaining request masks for engine 6. Engines 7 through 17 then repeat the full register pattern:

- `MMVM_INVALIDATE_ENGn_SEM` exposes a single `SEMAPHORE` bit.
- `MMVM_INVALIDATE_ENGn_REQ` exposes `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE0`, `INVALIDATE_L2_PDE1`, `INVALIDATE_L2_PDE2`, `INVALIDATE_L1_PTES`, `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, `LOG_REQUEST`, and `INVALIDATE_4K_PAGES_ONLY`.
- `MMVM_INVALIDATE_ENGn_ACK` exposes `PER_VMID_INVALIDATE_ACK` and `SEMAPHORE`.
- `MMVM_INVALIDATE_ENGn_ADDR_RANGE_LO32` exposes `S_BIT` and the low 31 bits of the logical page address range.
- `MMVM_INVALIDATE_ENGn_ADDR_RANGE_HI32` exposes the high 5 bits of the logical page address range.
- `MMVM_INVALIDATE_ENGn_RESERVE0/1/2` expose full-width `DUMMY` fields.

The request layout is stable across the covered engines: VMID request bits occupy the low 16 bits, `FLUSH_TYPE` occupies bits 16-18, invalidation scope bits occupy bits 19-23, and optional fault-status/log/4K-only controls occupy bits 24-26. The acknowledgement layout mirrors the VMID mask in bits 0-15 and puts the semaphore acknowledgement at bit 16.

### Invalidation Address Range Fields

Each engine has a low and high address-range register. The low register encodes `S_BIT` at bit 0 and `LOGI_PAGE_ADDR_RANGE_LO31` in bits 1-31. The high register carries `LOGI_PAGE_ADDR_RANGE_HI5` in bits 0-4. `mmhub_v2_3_program_invalidation()` initializes every invalidation engine's range to `0xffffffff` low and `0x1f` high, effectively programming the full addressable logical page range before invalidation requests are issued.

### L2 TLB Status

`MML2TLB_TLB0_STATUS` belongs to the `mmhub_mmutcl2_mml2tlbpfdec` address block. It provides:

- `BUSY`, a bit indicating active TLB work.
- `FOUND_PARITY_ERRORS`, a bit indicating parity error detection in the L2 TLB path.

No in-tree MMHUB 2.3.0 C code references these specific macros directly in the checked source, but they are part of the generated register surface available to debug, bring-up, or future error-handling code.

### L2 TLB Performance Counters

The `MML2TLB_PERFCOUNTER0_CFG` through `MML2TLB_PERFCOUNTER3_CFG` registers share the same encoding:

- `PERF_SEL` in bits 0-7 selects the first event.
- `PERF_SEL_END` in bits 8-15 selects the end/range companion event.
- `PERF_MODE` in bits 24-27 selects counter mode.
- `ENABLE` at bit 28 enables the counter.
- `CLEAR` at bit 29 clears the counter.

`MML2TLB_PERFCOUNTER_RSLT_CNTL` selects and controls result capture with `PERF_COUNTER_SELECT`, `START_TRIGGER`, `STOP_TRIGGER`, `ENABLE_ANY`, `CLEAR_ALL`, and `STOP_ALL_ON_SATURATE`.

`MML2TLB_PERFCOUNTER_LO` and `MML2TLB_PERFCOUNTER_HI` expose counter result storage. The low register is a full 32-bit low counter word. The high register splits bits 0-15 as `COUNTER_HI` and bits 16-31 as `COMPARE_VALUE`, which means consumers must not treat the high register as an unqualified 32-bit high counter word.

## Control Flow

There is no local control flow in this header. Runtime control flow is in the MMHUB driver code that includes it:

- `mmhub_v2_3_get_invalidate_req()` builds an invalidation request using `REG_SET_FIELD` with the `MMVM_INVALIDATE_ENG0_REQ` layout. Because engines 6-17 in this chunk use the same request field layout, generic VM hub code can use engine offsets rather than separate field encodings per engine.
- `mmhub_v2_3_program_invalidation()` loops over 18 invalidation engines and writes address range low/high registers by adding `i * hub->eng_addr_distance` to engine 0's address-range register.
- `mmhub_v2_3_init()` records `hub->vm_inv_eng0_sem`, `hub->vm_inv_eng0_req`, `hub->vm_inv_eng0_ack`, `hub->eng_distance`, and `hub->eng_addr_distance`. Those distances let common VM invalidation code address engines 0-17 consistently.
- Higher-level VM flush paths then write request registers, wait for acknowledgement bits, and coordinate semaphore state using the register addresses and field masks supplied by the generated headers.

The performance-counter and TLB-status macros in this chunk are passive definitions until a diagnostics or profiling path programs the corresponding MMIO registers.

## State and Persistence Behavior

The header itself persists no software state. The persistent or latched state described by the macros lives in MMHUB hardware registers:

- Invalidation request registers hold command bits until hardware consumes or overwrites them according to the MMHUB protocol.
- Acknowledgement registers report completion per VMID and semaphore state.
- Address-range registers persist the logical-page range used by invalidation engines. For MMHUB 2.3.0, the driver initializes all 18 engines to the maximal range during GART enablement.
- `MML2TLB_TLB0_STATUS` exposes transient busy state and error indication.
- Performance counter configuration registers persist event selection, mode, enable, and clear state until changed or reset.
- Performance counter result registers expose accumulated hardware counter values and compare state.

Several fields are command or strobe style rather than ordinary durable settings: invalidation request bits trigger TLB/cache invalidation work, `CLEAR` clears individual performance counters, and `CLEAR_ALL` clears the selected result-control domain. Consumers need the owning driver's sequencing and timeout policy; the generated masks do not encode ordering guarantees.

## Dependencies and Integration Points

This chunk depends on the AMDGPU register access infrastructure and the paired generated headers:

- `amdgpu/mmhub_v2_3.c` includes `mmhub_2_3_0_offset.h`, `mmhub_2_3_0_sh_mask.h`, and `mmhub_2_3_0_default.h`.
- `mmhub_2_3_0_offset.h` provides MMIO register numbers. The masks in this chunk are only meaningful when paired with those addresses.
- `soc15_common.h` and AMDGPU SOC15 helpers provide the MMHUB instance addressing used by `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.
- `REG_SET_FIELD` and `REG_GET_FIELD` rely on the exact `__SHIFT` and `_MASK` naming convention used here.
- `struct amdgpu_vmhub` stores engine base addresses and spacing derived from the generated offset header, allowing common VM invalidation logic to walk engines without hard-coding every `ENGn` address.

This file is source-tree-aligned with the Linux AMDGPU ASIC register headers under `drivers/gpu/drm/amd/include/asic_reg/mmhub`. It should be regenerated from AMD register descriptions rather than hand-edited when hardware definitions change.

## Risks and Edge Cases

- The chunk starts mid-register at line 9715. Engine 6 request shift definitions are in the preceding chunk, while the corresponding masks are in this chunk. Any merged per-file report should join these halves before describing engine 6 as a complete register.
- Field layout drift is high risk. `REG_SET_FIELD` will silently compose incorrect MMIO values if a mask or shift is wrong, potentially causing incomplete TLB invalidation, stale translations, missed acknowledgements, or VM fault storms.
- The driver loops over 18 invalidation engines. If future hardware changes the engine count, the register spacing, or the engine layout, both generated headers and the C loop assumptions need review.
- `PER_VMID_INVALIDATE_REQ` and `PER_VMID_INVALIDATE_ACK` are 16-bit fields. Callers must avoid invalid VMID shifts outside the supported range.
- The `MML2TLB_PERFCOUNTER_HI` register is split between `COUNTER_HI` and `COMPARE_VALUE`; interpreting it as a plain 64-bit counter high word would corrupt profiler results.
- Reserved `DUMMY` fields should not be treated as usable ABI without hardware documentation. Writing non-default values to reserved registers can have undefined hardware effects.
- Performance-counter control bits such as `ENABLE`, `CLEAR`, `ENABLE_ANY`, `CLEAR_ALL`, and `STOP_ALL_ON_SATURATE` affect live counters and should be coordinated with any concurrent profiling or diagnostics user.
- TLB status/error bits are hardware-observed state; polling code must account for timeout and reset behavior rather than assuming `BUSY` always clears promptly.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build coverage for `amdgpu/mmhub_v2_3.c` confirms that `REG_SET_FIELD(..., MMVM_INVALIDATE_ENG0_REQ, ...)` and related masks still compile with the generated header.
- VM/GART enablement on MMHUB 2.3.0 hardware should execute `mmhub_v2_3_program_invalidation()` and successfully program all 18 invalidation address ranges.
- GPUVM stress tests should show successful TLB invalidation completion with matching per-VMID acknowledgement bits and no hangs in invalidation wait paths.
- VM fault tests should still print meaningful MMHUB protection fault status and should not regress into repeated stale-translation faults after page table updates.
- Profiling or debug tests that use MML2TLB performance counters should verify counter clear, enable, saturation/stop behavior, event selection, and 48-bit-style result reconstruction from `LO` plus the 16-bit `COUNTER_HI` field.
- Error-injection or low-level diagnostics, when available, can check that `MML2TLB_TLB0_STATUS__FOUND_PARITY_ERRORS_MASK` is decoded as a single-bit status indicator.
