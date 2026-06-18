# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma2/sdma2_4_2_2_offset.h

## Purpose

`sdma2_4_2_2_offset.h` is a generated AMDGPU register offset table for the SDMA2 4.2.2 hardware block. The file declares the symbolic `mmSDMA2_*` register offsets for the `sdma2_sdma2dec` address block, whose documented base address is `0x78000`, plus one `*_BASE_IDX` companion for each offset. It has no executable logic; it is an ABI map used by SOC15 register helpers to convert stable source-level names into hardware MMIO addresses.

The table covers SDMA2-wide control and status registers, microcode upload/checksum registers, VM and SR-IOV controls, clock and power controls, address configuration, UTCL1 translation/cache status, error logging, EDC/performance counters, GFX and PAGE command queues, and eight RLC queue contexts. It pairs with `sdma2_4_2_2_sh_mask.h`, which supplies the bitfield shifts and masks for the register names defined here.

## Important APIs, Types, And Macros

This header exports only preprocessor macros:

- `mmSDMA2_<REG>` constants are 32-bit word offsets within the SDMA2 4.2.2 block. Examples include `mmSDMA2_UCODE_ADDR 0x0000`, `mmSDMA2_CNTL 0x001c`, `mmSDMA2_GFX_RB_CNTL 0x0080`, `mmSDMA2_PAGE_RB_CNTL 0x00d8`, and `mmSDMA2_RLC7_MIDCMD_CNTL 0x03e1`.
- `mmSDMA2_<REG>_BASE_IDX` constants identify the SOC15 base-index slot for each register. In this standalone SDMA2 table they are all `1`, which is significant because aggregate GC offset headers can expose same-named SDMA registers with different base-index values.
- The common SDMA2 block at offsets `0x0000` through `0x0062` includes microcode, VM context, virtualization, public/context register type, power/clock, status, UTCL1, atomic, EDC, performance, GPU IOV, and dummy/public registers.
- The GFX queue block starts at `mmSDMA2_GFX_RB_CNTL 0x0080` and includes ring base/read/write pointers, write-pointer polling, indirect buffer state, context status, doorbell, preemption, AQL, minor pointer update, and mid-command capture registers through `0x00c9`.
- The PAGE queue block starts at `mmSDMA2_PAGE_RB_CNTL 0x00d8` and mirrors the GFX queue layout through `mmSDMA2_PAGE_MIDCMD_CNTL 0x0121`.
- The RLC queue contexts `RLC0` through `RLC7` start at `0x0130`, `0x0188`, `0x01e0`, `0x0238`, `0x0290`, `0x02e8`, `0x0340`, and `0x0398`. Each context repeats the same queue-control shape: ring buffer control/base/read/write pointers, write-pointer polling, read-pointer writeback address, indirect-buffer state, skip/context/doorbell/status registers, CSA/preempt/dummy/AQL/minor-pointer registers, and mid-command data/control registers.

There are no functions, structs, enums, inline helpers, globals, or storage definitions in this file.

## Control Flow

The header itself has no runtime control flow. Its values participate in control flow when included by AMDGPU driver code:

- `amdgpu/amdgpu_amdkfd_arcturus.c` includes this file and uses `mmSDMA2_RLC0_RB_CNTL` in `get_sdma_rlc_reg_offset()`. For `engine_id == 2`, the driver computes the engine's absolute register base as `SOC15_REG_OFFSET(SDMA2, 0, mmSDMA2_RLC0_RB_CNTL) - mmSDMA2_RLC0_RB_CNTL`, then adds a queue stride derived from the RLC register spacing. KFD SDMA queue load/dump paths then access the selected queue registers through that computed base.
- `amdgpu/sdma_v4_0.c` includes this file for SDMA v4.x ASIC support. Its Arcturus and Aldebaran golden-setting tables use SDMA2 offsets such as `mmSDMA2_CHICKEN_BITS`, `mmSDMA2_GB_ADDR_CONFIG`, `mmSDMA2_GB_ADDR_CONFIG_READ`, and `mmSDMA2_UTCL1_TIMEOUT` with `SOC15_REG_GOLDEN_VALUE()`.
- SOC15 helpers such as `SOC15_REG_OFFSET()` and `SOC15_REG_GOLDEN_VALUE()` combine the IP block, instance, offset macro, and base-index metadata to select the MMIO address programmed by lower-level `RREG32`/`WREG32` paths.

The sequencing for firmware upload, ring startup, queue loading, preemption, interrupts, and golden-register programming lives in consumers such as `sdma_v4_0.c` and KFD SDMA MQD code. This header only determines which hardware addresses those flows touch.

## State And Persistence Behavior

The file stores no software state and performs no persistence. It names hardware state that is live in the GPU:

- `UCODE_*`, `PROGRAM`, and `UCODE_CHECKSUM` registers are involved in SDMA firmware or microcode programming and verification.
- `GFX_*`, `PAGE_*`, and `RLC*_*` ring and indirect-buffer registers describe command queue state, read/write pointers, doorbell inputs, polling addresses, preemption state, and mid-command snapshot state.
- `VM_*`, `MMHUB_CNTL`, `UTCL1_*`, `PHYSICAL_ADDR_*`, and XNACK/status registers connect SDMA command execution to GPU virtual-memory translation and fault behavior.
- `VF_ENABLE`, `ACTIVE_FCN_ID`, `VIRT_RESET_REQ`, `GPU_IOV_VIOLATION_LOG*`, context register type, public register type, and context-group boundary registers are tied to virtualization and PF/VF isolation.
- `STATUS*`, `ERROR_LOG`, `EDC_*`, `PERFCOUNTER*`, and `F32_*` registers expose transient or sticky diagnostic state that consumers may read or clear according to hardware semantics.
- `POWER_CNTL`, `POWER_CNTL_IDLE`, `CLK_CTRL`, `ULV_CNTL`, and related controls affect the block's power and clock behavior.

Persistence is hardware-defined. Some register values are reset on GPU reset or block reset, some are written during driver initialization, and some diagnostic/status bits may remain sticky until a consumer explicitly clears them. None of those semantics are encoded in this header.

## Dependencies And Integration Points

The file is coupled to:

- `sdma2_4_2_2_sh_mask.h` for field layout definitions matching these offsets.
- The parallel SDMA instance headers `sdma0_4_2_2_offset.h`, `sdma1_4_2_2_offset.h`, and `sdma3` through `sdma7` equivalents, which let Arcturus-style devices address multiple SDMA engines with comparable register layouts.
- `amdgpu_amdkfd_arcturus.c`, where SDMA2 queue register bases are selected for KFD/HSA SDMA queues.
- `sdma_v4_0.c`, where SDMA2 golden register settings are applied for ASIC initialization and tuning.
- SOC15 register-address infrastructure, including `SOC15_REG_OFFSET`, `SOC15_REG_GOLDEN_VALUE`, `SOC15_REG_ENTRY`, and the lower-level MMIO read/write helpers used by the driver.
- Firmware and queue-management flows for SDMA v4 hardware, where ring and IB registers named here must match the command packet format and MQD state programmed by the driver.

Because this header is generated register ABI, its symbolic names and numeric offsets are source-level contracts. Even a seemingly local rename can break compile-time users, and a numeric change can silently misprogram hardware if it still compiles.

## Risks

- Offset drift is high impact: a wrong numeric offset can redirect reads or writes into a different SDMA register, corrupt queue state, disable command processing, or produce hard-to-debug GPU hangs.
- Base-index drift is subtle. This standalone SDMA2 table uses base index `1` for all registers; copying values from aggregate GC headers or other generated tables with different base-index values can make SOC15 address calculation wrong.
- Queue stride assumptions matter. KFD computes per-queue RLC bases using the distance between RLC queue register blocks, so any incorrect `RLC0`/`RLC1` spacing affects every nonzero queue.
- Revision confusion is easy because SDMA0/1 4.2 headers, SDMA2 4.2.2 headers, and GC aggregate headers share many register names but can differ in instance coverage, base index, or mid-command register count.
- Virtualization and VM registers carry isolation risk. Incorrect PF/VF, active-function, GPU IOV violation, VM context, or UTCL1 offsets can break SR-IOV behavior or fault attribution.
- This file has no self-validation logic. Correctness depends on generated-source provenance, build coverage, static comparison against known-good AMD headers, and hardware tests.

## Test Signals

Useful validation signals include:

- A kernel build that compiles `amdgpu_amdkfd_arcturus.c` and `sdma_v4_0.c` with this header and its companion mask header.
- Static diffs against upstream or vendor-generated AMDGPU SDMA2 4.2.2 register headers, especially for base address, base indexes, RLC block starts, and golden-setting registers.
- Device probe on Arcturus/Aldebaran-family hardware reaches SDMA initialization and golden-register programming without MMIO faults, timeout logs, or firmware checksum errors.
- KFD SDMA queue tests exercise `engine_id == 2` and multiple `queue_id` values, confirming that RLC queue base computation lands on the expected `RLC0` through `RLC7` register windows.
- DMA copy/fill, page queue, and GFX queue workloads complete without ring pointer stalls, invalid doorbell behavior, IB faults, or preemption hangs.
- VM/fault tests cover UTCL1 status, XNACK, VM context, and physical-address diagnostic registers under valid and invalid memory accesses.
- SR-IOV testing checks VF enable/reset paths, active function ID state, GPU IOV violation logging, and context/public register-type boundaries.
- RAS and diagnostics tests read EDC counters, error logs, status registers, and performance counters and confirm that expected sticky bits clear only through the intended hardware paths.
