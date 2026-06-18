# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_2_2_offset.h

## Purpose

`sdma0_4_2_2_offset.h` is an AMDGPU ASIC register-offset header for the SDMA0 block, revision 4.2.2. It exposes compile-time register numbers for the `sdma0_sdma0dec` address block, whose local block base is documented in the header as `0x4980`. The register names are emitted as C preprocessor macros such as `mmSDMA0_UCODE_ADDR`, `mmSDMA0_GFX_RB_CNTL`, `mmSDMA0_PAGE_RB_CNTL`, and `mmSDMA0_RLC0_RB_CNTL`; each exported register offset is paired with a `_BASE_IDX` macro, which is `0` throughout this file.

The header has no executable code. Its behavioral role is to give AMDGPU and AMDKFD source files stable symbolic names for memory-mapped hardware register addresses. Consumers combine these local offsets with SOC15 block addressing helpers, register access macros, and the paired `sdma0_4_2_2_sh_mask.h` bitfield definitions to configure SDMA firmware, VM/virtualization state, ring buffers, doorbells, queue state, status collection, and RLC queue management for Arcturus-era hardware.

## Exported API Surface

The file exports only preprocessor constants. There are no C types, functions, inline helpers, global variables, or storage definitions.

Important macro groups:

- Header guard: `_sdma0_4_2_2_OFFSET_HEADER`.
- Public SDMA0 control and firmware loading offsets: `mmSDMA0_UCODE_ADDR`, `mmSDMA0_UCODE_DATA`, `mmSDMA0_VM_CNTL`, `mmSDMA0_VM_CTX_LO`, `mmSDMA0_VM_CTX_HI`, `mmSDMA0_CNTL`, `mmSDMA0_STATUS_REG`, `mmSDMA0_STATUS1_REG`, `mmSDMA0_STATUS2_REG`, `mmSDMA0_STATUS3_REG`, `mmSDMA0_UCODE_CHECKSUM`, and power/clock related registers.
- Virtualization and SR-IOV-facing offsets: `mmSDMA0_ACTIVE_FCN_ID`, `mmSDMA0_VIRT_RESET_REQ`, `mmSDMA0_VF_ENABLE`, `mmSDMA0_GPU_IOV_VIOLATION_LOG`, and `mmSDMA0_GPU_IOV_VIOLATION_LOG2`.
- Context/public register classification offsets: `mmSDMA0_CONTEXT_REG_TYPE0` through `mmSDMA0_CONTEXT_REG_TYPE3`, and `mmSDMA0_PUB_REG_TYPE0` through `mmSDMA0_PUB_REG_TYPE3`.
- GFX queue register window beginning at `mmSDMA0_GFX_RB_CNTL` (`0x0080`) and covering ring-buffer base/read/write pointers, write-pointer polling, indirect-buffer state, doorbell state, context status, CSA addresses, preemption, AQL control, minor pointer update, and mid-command registers.
- PAGE queue register window beginning at `mmSDMA0_PAGE_RB_CNTL` (`0x00d8`) with the same broad ring/IB/status/doorbell/mid-command pattern as the GFX window.
- RLC queue register windows `RLC0` through `RLC7`, each with the repeated ring-buffer, IB, context, status, doorbell, CSA, preemption, AQL, minor pointer, and mid-command register layout. `mmSDMA0_RLC0_RB_CNTL` starts at `0x0130`, and `mmSDMA0_RLC1_RB_CNTL` starts at `0x0188`, making the visible queue-window stride `0x58` register units.

The `_BASE_IDX` companion macros are part of the SOC15 register-description convention. In this file they all evaluate to `0`, so consumers that require a base index can pass or derive a uniform base selector for this SDMA0 block.

## Control Flow

There is no local control flow in this header: preprocessing either includes the macro definitions once through the guard or skips them on repeated inclusion. Runtime control flow appears only in consumers.

The most direct consumer in this tree is `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_arcturus.c`, which includes this header with the matching `sdma0_4_2_2_sh_mask.h` and the sibling SDMA1-SDMA7 4.2.2 headers. Its SDMA queue path uses the macros as follows:

- `get_sdma_rlc_reg_offset()` selects an SDMA engine base using `SOC15_REG_OFFSET(SDMA<N>, 0, mmSDMA<N>_RLC0_RB_CNTL) - mmSDMA<N>_RLC0_RB_CNTL`.
- It computes the queue offset with `queue_id * (mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL)`, so the SDMA0 RLC0/RLC1 offsets define the assumed per-queue stride for all Arcturus SDMA engines.
- `kgd_arcturus_hqd_sdma_load()` writes RLC ring state, doorbell state, read/write pointers, ring base addresses, and `RB_ENABLE` through `WREG32()` at `sdma_rlc_reg_offset + mmSDMA0_RLC0_*`.
- `kgd_arcturus_hqd_sdma_dump()` walks contiguous ranges bounded by these macros to collect queue state for diagnostics.
- `kgd_arcturus_hqd_sdma_is_occupied()` and `kgd_arcturus_hqd_sdma_destroy()` read and update `mmSDMA0_RLC0_RB_CNTL`, poll `mmSDMA0_RLC0_CONTEXT_STATUS`, disable doorbells, and preserve ring read-pointer values back into the MQD.

This means the header influences runtime register selection even though it contains no executable branches. Incorrect offsets compile cleanly but redirect later MMIO reads/writes.

## State And Persistence

The header itself maintains no memory, no persistent state, and no initialization side effects. It is a declarative map from symbolic register names to hardware register offsets.

The state represented by the macros lives in the GPU:

- Firmware upload and version/checksum registers model SDMA microcode state.
- Ring-buffer and indirect-buffer registers hold queue execution state.
- Doorbell and write-pointer polling registers connect CPU/KFD queue submissions to SDMA execution.
- Context status, preemption, CSA, and mid-command registers expose scheduling and save/restore state.
- VM, MMHUB, UTCL1, XNACK, and page/translation-related registers expose memory-management state.
- IOV and VF-related registers expose virtualization control and fault/violation logging.

Driver persistence across suspend, reset, process teardown, or KFD queue destruction is handled in consumers such as `amdgpu_amdkfd_arcturus.c`, not here. Those consumers rely on the numeric register constants remaining aligned with the actual ASIC register layout.

## Dependencies

Direct dependencies are minimal:

- The C preprocessor and include guard semantics.
- The MIT-style license block inherited from AMD register header generation.

Important external dependencies for correct use:

- `soc15.h` / `soc15d.h` and SOC15 register addressing macros such as `SOC15_REG_OFFSET()`.
- AMDGPU register access helpers such as `RREG32()` and `WREG32()`.
- The sibling bitfield header `sdma0_4_2_2_sh_mask.h`, which defines masks/shifts for the registers named here.
- Sibling engine offset headers `sdma1_4_2_2_offset.h` through `sdma7_4_2_2_offset.h`, used with this file in Arcturus KFD SDMA queue code.
- SDMA MQD definitions, especially `struct v9_sdma_mqd`, whose fields are written into the registers identified by these macros.

## Integration Points

The primary integration point is the AMDGPU/AMDKFD Arcturus SDMA path. `amdgpu_amdkfd_arcturus.c` includes this exact header and uses the RLC macros to implement KFD SDMA queue load, dump, occupancy, and destroy callbacks registered in `arcturus_kfd2kgd`.

The header also participates in the broader AMD register-header pattern under `drivers/gpu/drm/amd/include/asic_reg/`, where offset headers and `*_sh_mask.h` headers are included by IP-version-specific driver code. The offsets are normally not inspected at runtime; they become immediate constants in MMIO access expressions.

Compared with the related `sdma0_4_2_offset.h`, this 4.2.2 revision is not purely a renamed copy. It adds registers such as `mmSDMA0_UNBREAKABLE` and `mmSDMA0_GPU_IOV_VIOLATION_LOG2`, and the PAGE/RLC register windows are shifted earlier relative to the 4.2 header. That makes version-specific include selection important: using the wrong SDMA0 revision can produce valid-looking builds with wrong hardware accesses.

## Risks

- Offset drift is high impact. A wrong numeric macro can direct `RREG32()` or `WREG32()` to a different hardware register without producing a compiler error.
- The RLC queue stride assumption depends on `mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL`. Arcturus KFD code uses that delta for every queue on selected SDMA engines, so a bad RLC0 or RLC1 value would misaddress all nonzero SDMA queue IDs.
- Diagnostic dump ranges assume that register groups are contiguous between selected start/end macros. Holes in the hardware layout or incorrect endpoints can cause dumps to omit state or read unintended registers.
- This file must remain paired with the matching `sdma0_4_2_2_sh_mask.h`. Mixing 4.2.2 offsets with masks from another SDMA revision could set or test incorrect fields.
- Copying code from older SDMA revisions is risky because 4.2.2 changes queue-window offsets relative to `sdma0_4_2_offset.h`; the compile-time names are similar enough that review can miss a wrong include.
- The constants are generated hardware contract data, so ad hoc edits are more dangerous than regenerating from the authoritative register database.

## Test Signals

Useful validation signals are mostly build-time and hardware/runtime integration checks:

- Compile AMDGPU with Arcturus KFD support and ensure `amdgpu_amdkfd_arcturus.c` builds with this header and its sibling SDMA1-SDMA7 and mask headers.
- Static checks can verify expected invariants such as all `_BASE_IDX` values being `0`, `mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL == 0x58`, and analogous stride consistency across `RLC0` through `RLC7`.
- Runtime KFD SDMA queue load/destroy tests on Arcturus hardware should show queues becoming enabled, idle polling completing, doorbells functioning, and read/write pointer state being preserved across destroy.
- SDMA queue dump paths should return the expected `HQD_N_REGS` count and register addresses for RLC queues.
- Firmware initialization or low-level SDMA bring-up logs should not report SDMA microcode, checksum, VM, MMHUB, or doorbell failures attributable to invalid register accesses.
- SR-IOV or virtualization test coverage should include IOV violation logging paths where available, because 4.2.2 adds `GPU_IOV_VIOLATION_LOG2` relative to older SDMA0 4.2 headers.
