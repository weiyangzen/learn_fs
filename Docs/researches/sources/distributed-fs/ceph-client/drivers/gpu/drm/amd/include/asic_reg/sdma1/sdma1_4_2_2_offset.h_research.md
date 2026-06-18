# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_2_2_offset.h

### Purpose

`sdma1_4_2_2_offset.h` is the generated SDMA1 register offset map for SDMA 4.2.2 hardware. It covers the `sdma1_sdma1dec` block with base address `0x6180`. Like the 4.0 offset header, it exposes symbolic `mmSDMA1_*` register offsets and matching `_BASE_IDX` values, but this generation expands the RLC queue set and shifts some queue windows.

The file defines 507 real register offsets plus `_BASE_IDX` macros: 86 core SDMA1 registers, 43 GFX queue registers, 42 PAGE queue registers, and 336 RLC queue registers. The RLC coverage expands to RLC0 through RLC7, with the same repeated queue register layout per RLC queue.

### Important APIs, types, and functions

There are no functions or types. The public surface is:

- Include guard `_sdma1_4_2_2_OFFSET_HEADER`.
- Core offset macros such as `mmSDMA1_UCODE_ADDR`, `mmSDMA1_VM_CNTL`, `mmSDMA1_CNTL`, `mmSDMA1_STATUS_REG`, `mmSDMA1_UTCL1_CNTL`, and `mmSDMA1_GPU_IOV_VIOLATION_LOG`.
- A 4.2.2-specific `mmSDMA1_GPU_IOV_VIOLATION_LOG2` at offset `0x0062`.
- Queue windows: `GFX_RB_CNTL` at `0x0080`, `PAGE_RB_CNTL` at `0x00d8`, `RLC0_RB_CNTL` at `0x0130`, `RLC1_RB_CNTL` at `0x0188`, and additional RLC windows through `RLC7_RB_CNTL` at `0x0398`.
- Matching `*_BASE_IDX` macros, all set to `0`.

Compared with SDMA 4.0, this header drops `MMHUB_TRUSTLVL`, adds `GPU_IOV_VIOLATION_LOG2`, moves PAGE and RLC windows earlier, and increases RLC queue count from two to eight.

### Control flow

The header has no internal control flow. It feeds address calculations in SDMA 4.2.2 consumers. In this tree, `amdgpu_amdkfd_arcturus.c` includes this header and its `get_sdma_rlc_reg_offset()` function calculates queue register offsets for SDMA engines, including SDMA1 through `mmSDMA1_RLC0_RB_CNTL`. The queue offset flow then adds `queue_id * (RLC1_RB_CNTL - RLC0_RB_CNTL)` to reach the selected RLC queue window.

### State and persistence behavior

The file is stateless, but it names persistent hardware register locations:

- Microcode and control state (`UCODE_*`, `CNTL`, `CLK_CTRL`, `POWER_CNTL`, `FREEZE`, phase quantum registers).
- VM, SR-IOV, and fault state (`VM_*`, `ACTIVE_FCN_ID`, `VIRT_RESET_REQ`, `VF_ENABLE`, `GPU_IOV_VIOLATION_LOG`, `GPU_IOV_VIOLATION_LOG2`).
- UTCL1/XNACK/invalidation/page-walk state.
- GFX, PAGE, and eight RLC queue windows containing ring base/pointers, IB state, doorbells, status, watermarks, preemption, AQL, and mid-command capture registers.

Changing an offset changes which hardware state a driver read or write touches, so persistence is a hardware compatibility contract rather than a software-owned variable.

### Dependencies

This header depends on:

- SOC15 register access macros and block definitions for SDMA1.
- Matching SDMA 4.2.2 SDMA0, SDMA2 through SDMA7 headers in Arcturus-style multi-SDMA-engine code.
- The matching `sdma1_4_2_2_sh_mask.h` for field definitions. This work item only maps the offset header, but the shift/mask header exists in the same directory and should be used with it.

Observed direct consumer: `amdgpu_amdkfd_arcturus.c`.

### Integration points

The central integration point is Arcturus KFD SDMA queue support. `amdgpu_amdkfd_arcturus.c` computes per-engine, per-queue RLC register offsets using SDMA engine-specific headers, and SDMA1 uses this file for engine 1. Because this generation supports eight RLC windows, queue enumeration and MQD programming can cover more SDMA queues than SDMA 4.0.

The header also integrates with register dump/debug code, SR-IOV fault handling, VM/TLB invalidation diagnostics, and any SOC15 register access path that needs SDMA1 4.2.2 symbolic offsets.

### Risks

- This header is not a drop-in replacement for SDMA1 4.0. The base address changes from `0x5180` to `0x6180`, `PAGE_RB_CNTL` moves from `0x00e0` to `0x00d8`, `RLC0_RB_CNTL` moves from `0x0140` to `0x0130`, and RLC queue spacing changes from `0x60` in 4.0 to `0x58` in 4.2.2.
- Code that assumes only RLC0/RLC1 will miss RLC2 through RLC7 on 4.2.2 hardware.
- Code that carries over `MMHUB_TRUSTLVL` from 4.0 will not find that macro here; code that ignores `GPU_IOV_VIOLATION_LOG2` may lose fault detail.
- If queue-id bounds are wrong, address arithmetic can step past `RLC7` into unrelated register space.
- All macros compile as constants, so version mixups usually fail at runtime, not at compile time.

### Test signals

- Build coverage for `amdgpu_amdkfd_arcturus.c`.
- Static checks that RLC0 through RLC7 windows are complete and evenly spaced for the expected 4.2.2 layout.
- Runtime KFD SDMA queue tests on Arcturus-class hardware across all exposed SDMA engines and queue IDs, including queues above RLC1.
- SR-IOV and VM fault tests that inspect both `GPU_IOV_VIOLATION_LOG` and `GPU_IOV_VIOLATION_LOG2`.
- Suspend/resume and GPU reset tests that reinitialize SDMA1 4.2.2 rings using the matching offset and shift/mask headers.
