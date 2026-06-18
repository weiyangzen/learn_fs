# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_0_1_offset.h

## Purpose

`osssys_4_0_1_offset.h` is an AMDGPU SOC15-style OSSSYS 4.0.1 register offset header. It maps symbolic register names to offsets inside the `osssys_osssysdec` address block whose documented base address is `0x4280`.

The file is generated-style register documentation. It contains a license header, the `_osssys_4_0_1_OFFSET_HEADER` include guard, and 309 `#define` entries: 154 register offsets, 154 matching `_BASE_IDX` macros, and the include guard define. All register `_BASE_IDX` values in this file are `0`, meaning consumers pass the block instance/base index through SOC15 register-offset helpers rather than selecting multiple base arrays here.

## Important APIs, Types, and Macros

There are no C functions, structs, enums, or storage objects. The public API is a register-offset macro set using the `mm...` naming convention:

- `mmREGISTER`: the register's dword offset inside the OSSSYS block.
- `mmREGISTER_BASE_IDX`: the register base-index selector, always `0` in this file.

Important register groups by offset range:

- `0x0000-0x000f`: `mmIH_VMID_0_LUT` through `mmIH_VMID_15_LUT`, the interrupt-handler VMID-to-PASID lookup registers.
- `0x0010-0x001f`: `mmIH_VMID_0_LUT_MM` through `mmIH_VMID_15_LUT_MM`, the multimedia VMID/PASID lookup bank.
- `0x0020-0x0027`: `mmIH_COOKIE_0` through `mmIH_COOKIE_7`.
- `0x003f`: `mmIH_REGISTER_LAST_PART0`, a range sentinel.
- `0x0040-0x0043`: `mmSEM_REQ_INPUT_0` through `mmSEM_REQ_INPUT_3`.
- `0x007f`: `mmSEM_REGISTER_LAST_PART0`, a semaphore range sentinel.
- `0x0080-0x0098`: primary IH ring registers plus ring1 and ring2 variants, including `mmIH_RB_CNTL`, `mmIH_RB_BASE`, `mmIH_RB_BASE_HI`, `mmIH_RB_RPTR`, `mmIH_RB_WPTR`, `mmIH_RB_WPTR_ADDR_HI`, `mmIH_RB_WPTR_ADDR_LO`, `mmIH_DOORBELL_RPTR`, `mmIH_RB_CNTL_RING1`, `mmIH_RB_BASE_RING1`, `mmIH_RB_RPTR_RING1`, `mmIH_RB_WPTR_RING1`, `mmIH_DOORBELL_RPTR_RING1`, ring2 equivalents, and `mmIH_VERSION`.
- `0x00c0-0x00e5`: IH control, status, perf, DSM matching, VF ring status, flood/storm controls, clock control, interrupt flags, last interrupt info, scratch, credit/error, IOV violation, cookie violation, and MMHUB error registers.
- `0x00ff`: `mmIH_REGISTER_LAST_PART2`, another IH range sentinel.
- `0x0100-0x010f`: SEM clock, UTC/UTCL2, MCIF, perf, status, mailbox, chicken, IOV violation, and outstanding-threshold registers.
- `0x017f`: `mmSEM_REGISTER_LAST_PART2`.
- `0x0180-0x019f`: later IH virtualization/client configuration registers, including active function ID, virtual reset request, client config index/data, CID remap index/data, chicken, MMHUB control, and interrupt-drop match values/masks.
- `0x01a0-0x01bf`: later SEM virtualization/response registers, including active function ID, virtual reset request, per-client responses (`SDMA0`, `SDMA1`, `UVD`, `VCE_0`, `ACP`, `ISP`, `VCE_1`, `VP8`, `GC`), CID remap, atomic op LUT, EDC config, chicken bits2, MMHUB control, and a final range sentinel.

This header supplies addresses only. Field layout for these registers comes from companion shift/mask headers such as `osssys_4_0_1_sh_mask.h`.

## Control Flow

This header has no runtime control flow. Compile-time control is limited to:

1. Guard on `_osssys_4_0_1_OFFSET_HEADER`.
2. Define all OSSSYS 4.0.1 register offsets and `_BASE_IDX` values.
3. Close the include guard.

Runtime flow is in consumers that call helpers such as `SOC15_REG_OFFSET(OSSSYS, instance, mmIH_RB_CNTL)`, then read/write the resolved MMIO address via `RREG32_SOC15` or `WREG32_SOC15`.

## State and Persistence Behavior

The file does not hold state or persist data. It defines where hardware state lives in the OSSSYS MMIO block:

- IH VMID/PASID lookup state in the two 16-entry LUT banks.
- IH ring-buffer state for ring0, ring1, and ring2.
- IH control/status/flood/storm/error state used by interrupt delivery and diagnostics.
- IH virtualization state, including active function, virtual reset, client config, CID remap, interrupt drop match values/masks, and MMHUB control.
- SEM request/response, mailbox, clock, UTC/UTCL2, MCIF, status, virtualization, and per-client response state.

These states persist in GPU registers until hardware changes them, the driver rewrites them, or the relevant block resets.

## Dependencies

Direct dependencies:

- The C preprocessor and include guard.
- SOC15 register helper code that understands the `mm...` plus `_BASE_IDX` convention.

Semantic dependencies:

- The `OSSSYS` IP block identifier used by SOC15 accessors.
- Companion field-layout headers for OSSSYS 4.0.1.
- Hardware documentation for the `osssys_osssysdec` base address and offsets.
- Consumers must choose the correct ASIC revision. Offsets are not interchangeable with other generations such as `osssys_4_0`, `osssys_4_2_0`, `osssys_5_0_0`, or later `osssys_*` headers.

## Integration Points

This header is part of the AMDGPU register include tree under `include/asic_reg/oss`, alongside neighboring generations such as `osssys_4_0_offset.h`, `osssys_4_0_1_sh_mask.h`, `osssys_4_2_0_offset.h`, and newer OSSSYS 5/6/7 headers.

The exported macro style integrates with SOC15 AMDGPU paths. Examples of the same register family in the tree include:

- Newer IH implementations such as `navi10_ih.c`, `vega20_ih.c`, and `ih_v7_0.c`, which initialize ring register address tables with `SOC15_REG_OFFSET(OSSSYS, 0, mmIH_RB_CNTL)` or generation-specific `regIH_*` macros.
- GMC/KFD paths in later ASICs that access `IH_VMID_0_LUT` plus a VMID index to map VMIDs to PASIDs.
- IH setup and teardown code that uses the resolved offsets together with shift/mask macros for `IH_RB_CNTL`, `IH_CNTL`, `IH_CNTL2`, and ring-specific control registers.
- Virtualization and interrupt filtering paths that use active-function, VF ring status, client config, CID remap, and interrupt-drop registers.

## Risks and Edge Cases

- Offset/header mismatch: using these 4.0.1 offsets on a different OSSSYS generation can compile but address the wrong register.
- Base-address assumptions: comments document base `0x4280`, but normal consumers should use SOC15 helpers rather than manually adding this value.
- Sparse ranges and sentinels: `REGISTER_LAST_PART*` macros and gaps between ranges are intentional. Iteration code must not assume all offsets are valid registers.
- Ring variant confusion: ring0, ring1, and ring2 use similar names with different offsets. Programming the wrong ring can leave the intended interrupt ring disabled or corrupt another queue.
- VMID indexing: `mmIH_VMID_0_LUT + vmid` style access relies on contiguous offsets from `0x0000` through `0x000f`; callers must bound VMID to the available 16 entries. The `_MM` LUT bank is a separate contiguous range.
- Virtualization sensitivity: active function, virtual reset, client config, CID remap, and interrupt-drop registers affect SR-IOV/process isolation and interrupt routing.
- Field-layout separation: this file does not define bit masks. Callers must include the matching shift/mask header for the same ASIC revision.

## Test Signals

Useful validation signals are mostly compile-time plus hardware behavior:

- Compile coverage for any ASIC support that includes OSSSYS 4.0.1 register headers.
- Static checks that every `mm...` offset used with field macros comes from the same generation's offset and shift/mask headers.
- Cross-check generated offsets against AMD register documentation for `osssys_osssysdec` base `0x4280`.
- Runtime interrupt tests: initialize rings 0/1/2, enable/disable interrupts, test write-pointer writeback, doorbell read-pointer paths, overflow handling, and suspend/resume.
- PASID/VMID tests: read/write `IH_VMID_*_LUT` and `_MM` variants and verify VM fault/interrupt attribution.
- Virtualization tests: VF ring status, active function selection, virtual reset request, CID remap, client config, and interrupt-drop filter behavior.
- SEM tests: mailbox traffic, per-client response registers, outstanding threshold behavior, and reset recovery.
