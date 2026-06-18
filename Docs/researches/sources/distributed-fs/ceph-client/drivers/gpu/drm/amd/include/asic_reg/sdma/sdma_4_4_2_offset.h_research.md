# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_2_offset.h

## Purpose

`sdma_4_4_2_offset.h` is a generated AMDGPU ASIC register-offset header for the SDMA 4.4.2 block. It defines symbolic register offsets for the `aid_sdma_insts_sdma0_sdmadec` address block, whose local base address is documented as `0x4980`. The file does not implement executable behavior; it is a compile-time hardware map consumed by SDMA driver code so register access sites can use names such as `regSDMA_GFX_RB_CNTL` instead of raw numeric offsets.

Every register macro is paired with a `<register>_BASE_IDX` macro. In this file all base-index values are `0`, so the address-space selection is fixed for the SDMA register block. The consumer still combines these offsets with per-instance discovery data or SOC15 helpers to obtain the final MMIO address.

## Register Surface

The header is protected by `_sdma_4_4_2_OFFSET_HEADER` and contains only `#define` constants. Major groups are:

- Core SDMA engine/control registers: microcode address/data, F32 control, MMHUB trust, VM context controls, virtualization reset and VF enable, context/public register type maps, status registers, power gating, EDC/RAS/error registers, UTCL1 controls, performance counters, clock/power controls, and global address configuration.
- `GFX` queue window at offsets starting with `regSDMA_GFX_RB_CNTL` (`0x0080`): ring buffer base/read/write pointers, write-pointer polling, IB controls, doorbell controls, context status, CSA addresses, preemption, dummy/minor pointer update, and mid-command state.
- `PAGE` queue window at offsets starting with `regSDMA_PAGE_RB_CNTL` (`0x00d8`): the same broad ring/IB/doorbell/context/mid-command pattern for paging traffic.
- Compute/RLC queue windows `RLC0` through `RLC7`: each exposes a repeated register layout for SDMA queue state. `RLC0_RB_CNTL` starts at `0x0130`; subsequent RLC queues are spaced by the difference between `regSDMA_RLC1_RB_CNTL` and `regSDMA_RLC0_RB_CNTL`. The last defined register is `regSDMA_RLC7_MIDCMD_CNTL` at `0x03e3`.

## Important APIs, Types, and Functions

This header declares no C types, functions, enums, or inline APIs. Its public API is the macro namespace:

- `regSDMA_*`: SDMA register offsets relative to the SDMA instance's discovered MMIO base.
- `regSDMA_*_BASE_IDX`: base-index selectors, currently all `0`.

The companion file `sdma_4_4_2_sh_mask.h` supplies bit-field shifts and masks for the same register names. Typical consumers use an offset from this file with `RREG32`, `WREG32`, `SOC15_REG_OFFSET`, and `REG_SET_FIELD`/mask constants from the shift/mask header.

## Control Flow

There is no runtime control flow in this header. Runtime behavior appears when the macros are included by consumers:

- `drivers/gpu/drm/amd/amdgpu/sdma_v4_4_2.c` includes this file and defines `sdma_v4_4_2_get_reg_offset(adev, instance, offset)`, which returns `adev->reg_offset[SDMA0_HWIP][GET_INST(SDMA0, instance)][0] + offset`.
- That file wraps the offset calculation in `RREG32_SDMA(instance, offset)` and `WREG32_SDMA(instance, offset, value)`, then uses the macros during microcode loading, ring stop/start, queue resume, context-switch enablement, power/clock gating, RAS accounting, and IP-state dumps.
- `amdgpu_amdkfd_gc_9_4_3.c` includes the same offset/mask pair for KFD SDMA queue management. Its `get_sdma_rlc_reg_offset()` derives an RLC queue base from `regSDMA_RLC0_RB_CNTL` and the stride `regSDMA_RLC1_RB_CNTL - regSDMA_RLC0_RB_CNTL`, then adds `RLC0`-relative register offsets to program per-queue MQD state.

## State and Persistence Behavior

The header itself has no mutable state, allocation, persistence, locking, or side effects. It encodes a static hardware ABI: numeric offsets must match the SDMA 4.4.2 register specification and the firmware/ASIC behavior.

Stateful behavior in consumers includes:

- SDMA firmware loading through `regSDMA_UCODE_ADDR` and `regSDMA_UCODE_DATA`.
- Ring and IB state through `RB_BASE`, `RB_RPTR`, `RB_WPTR`, `IB_BASE`, `IB_SIZE`, and related high/low pointer registers.
- Doorbell enable/offset registers used to connect CPU/user doorbell writes to SDMA queue wakeups.
- Status, error, RAS, EDC, timeout, and performance-counter registers used for diagnostics and recovery.

Because these are MMIO registers, reads and writes persist in device hardware state until reset, power transitions, firmware action, or later driver writes change them.

## Dependencies

Direct dependencies are minimal:

- A C preprocessor and include guard discipline.
- AMDGPU register-access infrastructure in consumers, especially `soc15.h`, discovered `adev->reg_offset` tables, `GET_INST()`, `RREG32`, `WREG32`, and `SOC15_REG_OFFSET`.
- The paired `sdma_4_4_2_sh_mask.h` for field encodings. Offsets alone are insufficient for safe read-modify-write sequences.

The file is part of the generated ASIC register tree under `include/asic_reg/sdma`, alongside `sdma_4_4_0_offset.h` and corresponding shift/mask headers.

## Integration Points

Primary integration is with `amdgpu/sdma_v4_4_2.c`:

- Microcode load writes `regSDMA_UCODE_ADDR` and `regSDMA_UCODE_DATA`.
- Engine halt/unhalt uses `regSDMA_F32_CNTL`.
- Context switch and scheduling controls use `regSDMA_CNTL`, `regSDMA_PHASE0_QUANTUM`, `regSDMA_PHASE1_QUANTUM`, `regSDMA_PHASE2_QUANTUM`, and `regSDMA_UTCL1_TIMEOUT`.
- GFX queue setup uses the `regSDMA_GFX_*` ring, IB, doorbell, writeback, polling, and minor-pointer registers.
- Page queue setup uses equivalent `regSDMA_PAGE_*` registers when firmware support enables the paging queue.
- IP-state dump code stores selected offsets in `sdma_reg_list_4_4_2` and reads them per SDMA instance for debug printing.

Secondary integration is with KFD GC 9.4.3 SDMA support in `amdgpu_amdkfd_gc_9_4_3.c`, where `regSDMA_RLC0_*` and the RLC stride drive per-compute-queue MQD load/unload programming.

## Risks and Gotchas

- Numeric offset drift is high impact: an incorrect offset can write the wrong hardware register, leading to hangs, bad DMA, lost interrupts, or failed recovery.
- The RLC queue layout is assumed to be regular. KFD computes queue offsets from the `RLC1 - RLC0` stride, so nonuniform future hardware layouts would need code changes, not just new macro names.
- The offset header must stay synchronized with `sdma_4_4_2_sh_mask.h`; using an offset from one generation with masks from another can silently corrupt fields.
- This file has no runtime validation. Compile success only proves that macro names exist, not that offsets match the target ASIC.
- Register names are shared across similar SDMA generations. Accidentally including `sdma_4_4_0_*` or another generation in an SDMA 4.4.2 path could build but program incompatible hardware.
- Base-index macros are all `0`; consumers that need nonzero base-index routing would have to be updated if a future generated header changes that assumption.

## Test Signals

Useful validation signals come from consumers and hardware-facing tests rather than this header alone:

- Compile coverage for `sdma_v4_4_2.c` and `amdgpu_amdkfd_gc_9_4_3.c`, catching renamed or missing macros.
- SDMA ring tests in `sdma_v4_4_2_ring_test_ring()` and IB tests in `sdma_v4_4_2_ring_test_ib()`, which exercise ring pointer, doorbell, and command submission registers.
- Driver init/resume paths that call `sdma_v4_4_2_inst_start()`, `sdma_v4_4_2_gfx_resume()`, and `sdma_v4_4_2_page_resume()` without timeout or hardware fault.
- KFD SDMA queue load/unload testing, especially across multiple RLC queue IDs, to validate the RLC stride and register-window assumptions.
- Debugfs or DRM printer output from `sdma_v4_4_2_dump_ip_state()`/`print_ip_state()` showing sane values for the selected `sdma_reg_list_4_4_2` offsets.
- RAS/error injection or recovery tests that read `regSDMA_RAS_STATUS`, UE status registers, and EDC counters through the SDMA 4.4.2 paths.
