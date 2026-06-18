# Research: subset-b-003348

This grouped report covers the two source files assigned to `subset-b-003348`. Each file section is wrapped with the exact reconciliation markers used by the research guard.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_3_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_3_0_sh_mask.h

## Purpose

`oss_3_0_sh_mask.h` is an AMDGPU ASIC register bitfield header for the OSS 3.0 block. It exports preprocessor constants that describe bit masks and bit shifts for registers in the OSS register space used by older AMD GPU families, especially CIK/VI-era interrupt handling, semaphore, SRBM, SDMA, and HDP/XDP code.

The file is generated-style register documentation, not executable logic. It contains a license header, the `OSS_3_0_SH_MASK_H` include guard, and 3,633 `#define` entries. The dominant pattern is:

- `REGISTER__FIELD_MASK` for the already-positioned field mask.
- `REGISTER__FIELD__SHIFT` for the low-bit index used by `REG_SET_FIELD`, `REG_GET_FIELD`, or manual shifts.

The companion address header for this generation is usually `oss_3_0_d.h`; this file supplies the field layout once the caller has selected a register address such as `mmIH_RB_CNTL` or `mmSDMA0_GFX_RB_CNTL`.

## Important APIs, Types, and Macros

There are no C functions, structs, enums, storage objects, or callable APIs. The public API is the macro namespace consumed by AMDGPU and AMDKFD C code.

Important macro families include:

- Interrupt handler (`IH_*`): VMID-to-PASID LUTs, ring-buffer control, read/write pointers, write-pointer writeback addresses, interrupt enablement, status, perf counters, DSM match filtering, doorbell read-pointer support, active function ID, VF enable/status, and virtual reset request fields.
- Semaphore (`SEM_*`): MCIF config, active function and virtual reset fields, status bits, mailbox client config, mailbox data/control, chicken bits, and extra mailbox config.
- SRBM (`SRBM_*`): graphics/register access control, status and status2/status3, soft reset bits for major GPU blocks, credit recover/reset controls, clock enables, debug snapshot and read-error reporting, interrupt status/ack fields, firewall source/address reporting, DSM trigger controls, perf counters, CAM and domain address selectors, GFX index select/data, and virtualization controls.
- Client/security/reserved regions (`CLIENT0_*` through `CLIENT4_*`, `DH_TEST`, `KHFS*`, `KSESSION*`, `KSIG*`, `KEFUSE*`, `EXP*`, `LX*`): mostly full-register reserved masks or opaque fields that preserve vendor register layout for low-level access.
- SDMA (`SDMA0_*`, `SDMA1_*`, and shared `SDMA_*`): microcode address/data, power and clock controls, main engine control bits, status and status1/status2, perf monitors, freeze/debug, phase quantum, power-gating FSM, EDC, VM context, active function, virtual reset, VF enable, atomic controls, public/context register-type masks, and GFX/RLC0/RLC1 queue register fields.
- HDP/XDP (`HDP_*`, `HDP_XDP_*`): host-data-path read/write cache and non-surface controls, MEMIO command/status/data fields, VF enable, direct-to-HDP flush and BAR-update controls, P2P mailbox and BAR registers, memory-client config, write-combine controls, clock-gating controls, flush/busy/sticky status, debug windows, and high address bits for P2P BARs.

Representative high-value fields:

- `IH_RB_CNTL__RB_ENABLE_MASK`, `IH_RB_CNTL__RB_SIZE_MASK`, `IH_RB_CNTL__WPTR_WRITEBACK_ENABLE_MASK`, `IH_RB_CNTL__ENABLE_INTR_MASK`, `IH_RB_CNTL__MC_VMID_MASK`, and `IH_RB_CNTL__WPTR_OVERFLOW_CLEAR_MASK` define interrupt-ring setup and recovery behavior.
- `IH_RB_WPTR__RB_OVERFLOW_MASK`, `IH_RB_WPTR__OFFSET_MASK`, `IH_RB_WPTR__RB_LEFT_NONE_MASK`, and `IH_RB_WPTR__RB_MAY_OVERFLOW_MASK` are used when reading and sanitizing interrupt write pointers.
- `IH_DOORBELL_RPTR__OFFSET_MASK` and `IH_DOORBELL_RPTR__ENABLE_MASK` describe doorbell-driven interrupt read-pointer updates.
- `SRBM_STATUS__IH_BUSY_MASK`, along with other SRBM busy bits, is used during idle waits and reset paths.
- `SRBM_SOFT_RESET__SOFT_RESET_*` fields are broad reset controls. Incorrect writes can reset unrelated GPU IP blocks.
- `SDMA0_GFX_RB_CNTL__RB_ENABLE_MASK`, `SDMA0_GFX_RB_CNTL__RB_SIZE_MASK`, `SDMA0_GFX_IB_CNTL__IB_ENABLE_MASK`, `SDMA0_GFX_IB_CNTL__SWITCH_INSIDE_IB_MASK`, and their `SDMA1_*` equivalents drive SDMA ring and indirect-buffer setup.
- `SDMA0_GFX_DOORBELL__OFFSET_MASK` and `SDMA0_GFX_DOORBELL__ENABLE_MASK`, plus RLC0/RLC1 counterparts, gate SDMA queue doorbells.
- `HDP_MISC_CNTL__READ_CACHE_INVALIDATE_MASK`, `HDP_MEMIO_CNTL__MEMIO_*`, and `HDP_XDP_*_FLUSH*` fields affect CPU-visible memory coherency and host-data-path flushes.

## Control Flow

This header has no runtime control flow. Its compile-time flow is limited to the include guard:

1. If `OSS_3_0_SH_MASK_H` is not defined, define it.
2. Expose the OSS 3.0 bitfield constants.
3. End with `#endif /* OSS_3_0_SH_MASK_H */`.

Runtime control flow appears in consumers. For example, CIK/Iceland interrupt code reads `mmIH_RB_CNTL`, uses `REG_SET_FIELD` or direct mask operations with `IH_RB_CNTL__*`, and writes the result back with `WREG32`. SDMA setup code reads/writes SDMA ring registers and applies `SDMA0_GFX_*` masks when enabling rings, writeback, byte swapping, and indirect buffers. KFD queue code uses SDMA field masks when programming queue descriptors for VI hardware.

## State and Persistence Behavior

The file itself has no mutable state and persists nothing. The constants describe hardware state stored in MMIO registers:

- Interrupt-ring state: base address, read pointer, write pointer, overflow state, writeback address, interrupt enablement, and ring sizing.
- PASID/VMID association state: `IH_VMID_0_LUT` through `IH_VMID_15_LUT` expose 16-bit PASID fields used by VM fault/interrupt attribution.
- Virtualization state: active function IDs, VF enables, VF ring statuses, virtual reset requests, and per-block VF/PF bits.
- Reset and idle state: SRBM soft-reset and status masks describe persistent hardware latch/control bits until changed by driver register writes or hardware events.
- SDMA state: queue base pointers, read/write pointers, IB status, doorbell offsets, VM context, preemption state, atomic controls, and engine idle/frozen indicators.
- HDP/XDP state: cache invalidation, flush arming/status, P2P BAR/mailbox setup, debug windows, and sticky write-one-to-clear status bits.

Because these constants encode hardware contracts, persistence is external to the C preprocessor: a wrong mask or shift can corrupt live GPU register state and survive until the block is reset or reprogrammed.

## Dependencies

Direct dependencies are minimal:

- The C preprocessor and include guard.
- Companion OSS address headers such as `oss_3_0_d.h` for `mm*` register addresses.
- AMDGPU register helper macros, especially `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, and related SOC-specific wrappers in consumer C files.

Semantic dependencies are stronger:

- The mask/shift names must match AMD hardware register documentation for OSS 3.0.
- Register names must align with address macros in the same ASIC generation.
- Field names must match the expectations baked into AMDGPU, AMDKFD, and power-management call sites.

## Integration Points

Observed consumers under the AMD driver tree include:

- `drivers/gpu/drm/amd/amdgpu/cik_ih.c` and `drivers/gpu/drm/amd/amdgpu/iceland_ih.c`, which include/use `IH_RB_CNTL`, `IH_CNTL`, `IH_RB_WPTR`, and `SRBM_STATUS` masks for interrupt ring initialization, enable/disable, overflow handling, pointer updates, and idle waits.
- `drivers/gpu/drm/amd/amdgpu/cik_sdma.c`, which uses `SDMA0_GFX_*` masks with SDMA register addresses for ring enablement, pointer writeback, indirect-buffer control, VM setup, and queue reset.
- `drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_vi.c` and `drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_vi.c`, which include this header for VI-era queue management.
- `drivers/gpu/drm/amd/pm/powerplay/inc/smu7_common.h`, which includes this header as part of SMU7/powerplay register programming support.
- `drivers/gpu/drm/amd/amdgpu/dce_v10_0.c` and `drivers/gpu/drm/amd/amdgpu/vi.c`, which rely on OSS/HDP fields for display-era and VI-level register programming.

Newer SOC15 interrupt paths use later `osssys_*` headers, but the macro pattern and field names are intentionally consistent so shared code can use `REG_SET_FIELD` and ASIC-specific register headers.

## Risks and Edge Cases

- Hardware ABI risk: each numeric mask and shift is a hardware ABI. A one-bit error can disable interrupts, program wrong VMIDs/PASIDs, acknowledge the wrong status bit, or reset a different IP block.
- Address/header mismatch: using this OSS 3.0 field header with an incompatible address header can compile but program the wrong register layout.
- Write-one-to-clear semantics: fields such as interrupt overflow clear or sticky XDP status require caller discipline. A read/modify/write using a mask without understanding W1C behavior can clear events unexpectedly.
- Ring alignment assumptions: many pointer and address masks reserve low bits (`OFFSET` or `ADDR` fields shifted by 2 or 5). Callers must program aligned GPU addresses and pointer values.
- Virtualization isolation: VF/PF, active-function, VMID, and PASID fields affect SR-IOV and process isolation. Bad values can attribute faults incorrectly or break VF reset paths.
- Reset blast radius: `SRBM_SOFT_RESET` contains many block reset controls in one register. Mask drift can broaden a reset sequence beyond the intended IP.
- Generated-name quirks: the file includes generated irregularities such as `HDP_XDP_HDP_MC_CFG__HDP_MC_CFG_MC_STALL_ON_BUF_FULL_MASK_MASK`. Consumers may depend on exact generated names, so cleanup refactors are risky.
- Reserved fields: many client/security sections expose full-register `RESERVED` masks. Treating those as safe writable fields can violate hardware expectations.

## Test Signals

There are no unit-testable functions in this header. Useful validation signals are build-time and hardware/driver behavior:

- Compile coverage for all C files that include this header, especially CIK, Iceland, VI, KFD VI, SMU7, DCE10, and SDMA code.
- Preprocessor checks that every field used by `REG_SET_FIELD(x, REGISTER, FIELD, value)` has matching `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` macros.
- Cross-header consistency checks against `oss_3_0_d.h` and AMD register documentation.
- Boot and module-load tests on affected ASICs.
- Interrupt tests: IH ring initialization, enable/disable, overflow recovery, write-pointer writeback, doorbell read-pointer updates, and suspend/resume.
- SDMA tests: ring start/stop, IB execution, preemption, doorbell writes, VM-context DMA, and reset recovery.
- Virtualization tests: PASID lookup, VF enable/reset paths, active-function selection, and interrupt attribution under SR-IOV.
- Memory coherency tests: HDP flush/invalidate paths and CPU/GPU visibility after DMA or peer-to-peer BAR operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_3_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_0_1_offset.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_0_1_offset.h -->
