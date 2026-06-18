# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_0_offset.h

### Purpose

`sdma1_4_0_offset.h` is the generated SDMA1 register offset map for SDMA 4.0. It maps symbolic register names to word offsets inside the `sdma1_sdma1dec` address block with base address `0x5180`. AMDGPU uses this kind of header with SOC15 register macros to compute MMIO addresses for SDMA1 engine programming.

The file defines 255 real register offsets plus a `_BASE_IDX` macro for each register. The register families are 86 core SDMA registers, 43 GFX queue registers, 42 PAGE queue registers, and 84 RLC queue registers covering RLC0 and RLC1. All `_BASE_IDX` values are `0`, so this header describes one base-index space.

### Important APIs, types, and functions

There are no functions or data structures. The exported API is a set of preprocessor constants:

- Include guard `_sdma1_4_0_OFFSET_HEADER`.
- `mmSDMA1_*` offset macros such as `mmSDMA1_UCODE_ADDR`, `mmSDMA1_VM_CNTL`, `mmSDMA1_CNTL`, `mmSDMA1_STATUS_REG`, `mmSDMA1_UTCL1_CNTL`, and `mmSDMA1_GPU_IOV_VIOLATION_LOG`.
- Queue windows starting at `mmSDMA1_GFX_RB_CNTL` (`0x0080`), `mmSDMA1_PAGE_RB_CNTL` (`0x00e0`), `mmSDMA1_RLC0_RB_CNTL` (`0x0140`), and `mmSDMA1_RLC1_RB_CNTL` (`0x01a0`).
- Matching `*_BASE_IDX` macros, all set to `0`, used by generated register access helpers.

The offsets are register-index values, not byte addresses. Consumers normally pass them through `SOC15_REG_OFFSET(...)` or related AMDGPU register access macros.

### Control flow

The header has no runtime control flow. It supplies constants to consumers. A representative consumer pattern appears in `amdgpu_amdkfd_gfx_v9.c`, where KFD computes an SDMA RLC queue register base from an engine base plus `queue_id * (mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL)`. In that flow, this header is part of the address arithmetic for SDMA1 engine 1.

### State and persistence behavior

The file stores no mutable state. It defines the persistent contract between driver source and hardware register layout. The most stateful hardware areas represented are:

- Microcode access registers (`UCODE_ADDR`, `UCODE_DATA`, `UCODE_CHECKSUM`).
- VM and virtualization registers (`VM_CNTL`, `VM_CTX_*`, `ACTIVE_FCN_ID`, `VIRT_RESET_REQ`, `VF_ENABLE`, `MMHUB_TRUSTLVL`, `GPU_IOV_VIOLATION_LOG`).
- Ring and indirect-buffer state for GFX, PAGE, RLC0, and RLC1 queues, including base addresses, read/write pointers, poll addresses, doorbells, context status, CSA addresses, preemption, AQL control, and mid-command capture data.
- Diagnostics and performance state (`STATUS*`, EDC counters, error logs, perf counters).

Persistence is entirely in hardware registers and in driver memory programmed through those registers. Changing an offset changes where that state is read or written.

### Dependencies

This header depends on:

- The SOC15 register access layer that combines block, instance, base index, and offset into final MMIO addresses.
- Matching SDMA0 offset headers where arithmetic uses SDMA0 deltas to address SDMA1 queues.
- `sdma1_4_0_sh_mask.h` for bitfield interpretation and `sdma1_4_0_default.h` for expected default values.

Observed include points include `amdgpu_amdkfd_gfx_v9.c` and `soc15.c`.

### Integration points

The key integration surface is KFD and SOC15 SDMA programming. `amdgpu_amdkfd_gfx_v9.c` includes this header and computes SDMA RLC register offsets for queue programming. `soc15.c` includes the SDMA1 4.0 offset map alongside SDMA0, GC, NBIO, MP, UVD, GFXHUB, and MMHUB register maps for SOC15 initialization and access routing.

The register names also line up with the SDMA1 4.0 shift/mask and default headers, so generated code, debugfs dumps, trace helpers, and reset code can use a consistent name across address, field, and default-value layers.

### Risks

- Offset headers are hardware contracts. A single wrong numeric offset can redirect a register write to an unrelated register and cause hangs, queue corruption, VM faults, or failed preemption.
- SDMA1 4.0 has only RLC0 and RLC1 in this header. Code that assumes more RLC queues must use a newer SDMA map such as 4.2.2.
- Queue spacing is part of driver arithmetic. In this file `RLC1_RB_CNTL - RLC0_RB_CNTL` is `0x60`; consumers that derive queue windows depend on that spacing remaining correct.
- Do not substitute `sdma1_4_2_2_offset.h` for this header. The base address and queue offsets differ, including PAGE and RLC window starts.

### Test signals

- Build coverage for `amdgpu_amdkfd_gfx_v9.c` and `soc15.c`.
- Static checks that every offset has a `_BASE_IDX`, every default macro in `sdma1_4_0_default.h` has a matching offset, and every commented register block in `sdma1_4_0_sh_mask.h` has a matching offset.
- Runtime KFD SDMA queue tests that exercise engine 1 and queue IDs 0 and 1.
- Suspend/resume and GPU reset tests that reprogram SDMA1 rings, poll read/write pointers, and verify doorbell behavior.
