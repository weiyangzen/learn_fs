# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vpe/vpe_6_1_0_sh_mask.h lines 1-2611

## Scope

This chunk covers the opening 2,611 lines of the generated AMD VPE 6.1.0 shift/mask header. It starts with the license, include guard, and `vpe_vpedec` register field definitions, then covers the complete VPEC command processor/control block, the repeated VPEC queue 0-7 register templates, the VPCNVC input conversion block, the VPDSCL scaler block, and the beginning of the VPCM color-management block through `VPCM_GAMUT_REMAP_C13_C14__VPCM_GAMUT_REMAP_C13_MASK`. The physical header continues after this work item with the rest of `VPCM_GAMUT_REMAP_C13_C14` and later VPE display pipeline, mixer, formatter, CDC, and perfmon definitions; those later lines are intentionally outside this chunk.

The file is a generated C preprocessor hardware register bitfield map. It contains no executable functions, structs, enums, allocation, locking, or local software storage. Its contract is the exact `__SHIFT` and `_MASK` macro values used with AMDGPU register helpers for VPE 6.1 command processing and early video pipeline programming.

## Purpose

`vpe_6_1_0_sh_mask.h` is the bitfield companion to `vpe_6_1_0_offset.h`. The offset header provides `reg...` MMIO register addresses and base indices; this header names the bit positions and masks inside those registers. Runtime code combines both through AMDGPU/SOC15 helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, `SOC15_WAIT_ON_RREG`, and VPE-specific `vpe_get_reg_offset()`.

The first half of this chunk describes VPEC, the VPE command/control engine. It exposes firmware loading, F32 thread control, global clocks and power, trap/interrupt enables, ring-buffer queues, indirect-buffer queues, doorbells, preemption, queue reset, status, CRC, perf counter, scratch, and queue hang fields. The latter part begins the programmable video processing pipeline: VPCNVC format conversion and pre-color-space-conversion, VPDSCL scaling and line-buffer controls, and the first VPCM post-CSC/gamut-remap fields.

## Important Macro Families

The VPEC firmware and engine-control families define the bring-up surface:

- `VPEC_DEC_START`, `VPEC_UCODE_ADDR`, and `VPEC_UCODE_DATA` provide firmware start and microcode address/data loading fields. `VPEC_UCODE_ADDR` includes both `VALUE` and `THID`, while `VPEC_UCODE_DATA` is a raw 32-bit payload.
- `VPEC_F32_CNTL` controls F32 execution state through `HALT`, per-thread checksum clear, reset, enable, and priority fields.
- `VPEC_VPEP_CTRL`, `VPEC_CLK_CTRL`, `VPEC_PG_CNTL`, `VPEC_POWER_CNTL`, and `VPEC_CLOCK_GATING_STATUS` expose VPEP reset, VPE clock enables, soft clock overrides, power gating, light-sleep, and gate-status bits.
- `VPEC_CNTL`, `VPEC_CNTL1`, and `VPEC_CNTL2` expose trap enable, byte swapping, fence swap, mid-command preempt and world-switch controls, UMSCH interrupt enable, NACK interrupt enables, z-state controls, freeze/preempt interrupt enables, SRAM polling/retry controls, F32 postcodes, ucode buffering, FIFO watermarks, and channel read/write watermarks.

Scheduling, timeout, memory, and diagnostics are described by global VPEC registers:

- `VPEC_GB_ADDR_CONFIG` and `_READ` define graphics address configuration fields such as pipe count, interleave size, compressed fragments, packers, shader engines, and RB-per-SE.
- `VPEC_PROCESS_QUANTUM0/1`, `VPEC_CONTEXT_SWITCH_THRESHOLD`, and `VPEC_GLOBAL_QUANTUM` define per-process and global context scheduling quanta.
- `VPEC_WATCHDOG_CNTL`, `VPEC_ATOMIC_CNTL`, `VPEC_MEMREQ_BURST_CNTL`, `VPEC_CREDIT_CNTL`, and `VPEC_RELAX_ORDERING_LUT` tune queue hang detection, atomic loop timing, memory request burst behavior, memory-controller credits, and relaxed-ordering permissions for VPE, fence, poll, conditional execute, atomic, timestamp, world switch, read-pointer writeback, IB fetch, and RB fetch traffic.
- `VPEC_TIMESTAMP_CNTL`, `VPEC_GLOBAL_TIMESTAMP_LO/HI`, `VPEC_FREEZE`, `VPEC_CE_CTRL`, `VPEC_CE_BUSY`, `VPEC_F32_COUNTER`, `VPEC_ATOMIC_PREOP_LO/HI`, `VPEC_HOLE_ADDR_LO/HI`, `VPEC_INT_STATUS`, and `VPEC_ERROR_LOG` provide timestamp capture, freeze/preempt state, copy-engine watermarks/busy bits, counters, atomic preop payloads, address-hole configuration, interrupt status, and error logging.
- `VPEC_PERFCNT_*`, `VPEC_CRC_*`, `VPEC_PUB_DUMMY0..7`, `VPEC_UCODE*_CHECKSUM`, `VPEC_VERSION`, and `VPEC_SCRATCH_RAM_*` provide performance counters, CRC control/data, driver/firmware scratch or dummy registers, checksum values, version fields, and scratch RAM indexed access.

Status and queue-hang families expose observability:

- `VPEC_STATUS` reports global idle, register idle, ring/IB command full/idle, context-empty, inside-IB, memory-read/write idle, packet-ready, previous-command idle, interrupt idle, and interrupt-request stall state.
- `VPEC_STATUS1` breaks down copy-engine IP0/IP1/OP0 idle/full/stall and power-gating status.
- `VPEC_STATUS2`, `VPEC_STATUS3`, and `VPEC_STATUS4` expose command op status, exception idle, interrupt queue ID, active queue ID, polling state, outstanding channel/register work, and VPEP register accesses.
- `VPEC_STATUS5`, `VPEC_STATUS6`, and `VPEC_STATUS7` expose queue enable, preempt, selected, and related queue-state bitmaps.
- `VPEC_QUEUE_STATUS0` packs four status bits per queue for queues 0-7, while `VPEC_QUEUE_HANG_STATUS` names hang causes such as F32 hang, CE hang, EOF mismatch, invalid opcode, and invalid VPEP config address.

The repeated queue register template is the largest part of the chunk. It appears for `VPEC_QUEUE0_*` through `VPEC_QUEUE7_*`:

- `RB_CNTL` fields configure ring enable, ring size, write-pointer polling, byte swapping, F32 write-pointer polling, read-pointer writeback, writeback timer, privilege, and VMID.
- `SCHEDULE_CNTL` fields map queue scheduling IDs and context quantum.
- `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`, `RB_RPTR_ADDR_HI`, and `RB_RPTR_ADDR_LO` define ring GPU address, read/write pointers, and read-pointer writeback address fields. Low writeback addresses are 4-byte aligned through the low-address mask.
- `RB_AQL_CNTL` enables AQL packet parsing, packet size/step, mid-command preemption, preempt data restore, and overlap.
- `MINOR_PTR_UPDATE`, `CD_INFO`, `RB_PREEMPT`, `SKIP_CNTL`, `DOORBELL`, `DOORBELL_OFFSET`, and `DUMMY0..4` provide pointer-update sequencing, context descriptor payloads, RB preempt requests, skip counts, doorbell enable/captured/offset fields, and scratch/dummy storage.
- `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO/HI`, `IB_SIZE`, `CMDIB_CNTL`, `CMDIB_RPTR`, `CMDIB_OFFSET`, `CMDIB_BASE_LO/HI`, and `CMDIB_SIZE` define normal and command indirect-buffer controls, offsets, base addresses, sizes, swap behavior, switch-inside-IB behavior, and command VMID.
- `CSA_ADDR_LO/HI`, `CONTEXT_STATUS`, `DOORBELL_LOG`, `IB_SUB_REMAIN`, and `PREEMPT` expose context-save area addresses, selected/use-IB/idle/expired/exception/context-switchable/preempt-disable/writeback-idle/write-pointer-pending state, doorbell logging, remaining sub-IB size, and IB preempt request.

The VPCNVC block begins the VPE pixel pipeline:

- `VPCNVC_SURFACE_PIXEL_FORMAT` and `VPCNVC_FORMAT_CONTROL` define source format, format expansion, 16-bit conversion, alpha enable, bypass, MSB alignment, positive clamp, chroma clamp, and update-pending status.
- `VPCNVC_FCNV_FP_BIAS_*` and `VPCNVC_FCNV_FP_SCALE_*` provide per-channel 19-bit floating-conversion bias and scale fields.
- `VPCNVC_COLOR_KEYER_CONTROL`, `VPCNVC_COLOR_KEYER_ALPHA/RED/GREEN/BLUE`, and `VPCNVC_ALPHA_2BIT_LUT` define color-key enable/mode, low/high key ranges for alpha/R/G/B, and four 8-bit alpha LUT entries.
- `VPCNVC_PRE_DEALPHA`, `VPCNVC_PRE_REALPHA`, `VPCNVC_PRE_CSC_MODE`, `VPCNVC_PRE_CSC_C*`, `VPCNVC_COEF_FORMAT`, and `VPCNVC_PRE_DEGAM` configure pre-dealpha, pre-realpha, pre-CSC mode/current status, pre-CSC coefficient pairs, coefficient format, and pre-degamma mode/select.

The VPDSCL block defines scaler and line-buffer programming:

- `VPDSCL_COEF_RAM_TAP_SELECT` and `VPDSCL_COEF_RAM_TAP_DATA` select scaler coefficient RAM tap pair, phase, filter type, and even/odd coefficient data/enables.
- `VPDSCL_MODE`, `VPDSCL_TAP_CONTROL`, `VPDSCL_CONTROL`, `VPDSCL_2TAP_CONTROL`, and `VPDSCL_MANUAL_REPLICATE_CONTROL` define scaler mode, coefficient RAM selection, chroma/alpha coefficient mode, luma/chroma tap counts, boundary mode, 2-tap hardcoded coefficient/sharpness controls, and manual replication factors.
- Horizontal and vertical luma/chroma scale ratios and init fractions/integers are exposed through `VPDSCL_HORZ_FILTER_*`, `VPDSCL_VERT_FILTER_*`, and `_C`/`_BOT` variants.
- `VPDSCL_BLACK_COLOR`, `VPDSCL_UPDATE`, `VPDSCL_AUTOCAL`, `VPDSCL_EXT_OVERSCAN_*`, `VPOTG_H_BLANK`, `VPOTG_V_BLANK`, `VPDSCL_RECOUT_START`, `VPDSCL_RECOUT_SIZE`, `VPMPC_SIZE`, `VPLB_DATA_FORMAT`, `VPLB_MEMORY_CTRL`, `VPLB_V_COUNTER`, `VPDSCL_MEM_PWR_CTRL`, and `VPDSCL_MEM_PWR_STATUS` cover black fill color, update pending, autocal mode, overscan, timing blank windows, recout rectangle, MPC dimensions, line-buffer alpha/data/memory partitioning, vertical counters, and scaler memory power-state control/status.

The chunk ends in the early VPCM block:

- `VPCM_CONTROL` exposes bypass and update-pending state.
- `VPCM_POST_CSC_CONTROL` and `VPCM_POST_CSC_C11_C12` through `C33_C34` define post-CSC mode/current state and paired matrix coefficients.
- `VPCM_GAMUT_REMAP_CONTROL`, `VPCM_GAMUT_REMAP_C11_C12`, and the beginning of `VPCM_GAMUT_REMAP_C13_C14` define gamut-remap mode/current state and the first coefficient pairs. The line range stops after the `C13` mask; the `C14` mask and later VPCM fields belong to the next chunk.

## Control Flow

There is no local control flow in this header. All behavior is in consumers that include this generated file and use the macros to compose or extract MMIO bitfields.

The direct consumer in this source tree is `drivers/gpu/drm/amd/amdgpu/vpe_v6_1.c`. Its relevant flow is:

1. Include `vpe_6_1_0_offset.h` and this shift/mask header, then map VPE instance register offsets through `vpe_v6_1_get_reg_offset()`.
2. Halt or release F32 execution by reading `regVPEC_F32_CNTL`, applying `REG_SET_FIELD(..., VPEC_F32_CNTL, HALT, ...)` and `TH1_RESET`, then writing the register back.
3. Load VPE microcode either through PSP SRAM update or by manually writing `regVPEC_UCODE_ADDR` and streaming firmware dwords through `regVPEC_UCODE_DATA`. Before loading, the driver clears `VPEC_CNTL.UMSCH_INT_ENABLE`, enables collaborate mode when configured, and programs DPM.
4. Start the ring by programming `VPEC_QUEUE0_RB_CNTL` size, privilege, VMID, read-pointer writeback, and enable bits; zeroing queue 0 read/write pointers; programming queue 0 RB base and read-pointer writeback addresses; using `VPEC_QUEUE0_MINOR_PTR_UPDATE` while reducing the write pointer; programming `VPEC_QUEUE0_DOORBELL_OFFSET` and `VPEC_QUEUE0_DOORBELL.ENABLE`; and enabling `VPEC_QUEUE0_IB_CNTL.IB_ENABLE`.
5. Stop the ring by asserting `VPEC_QUEUE_RESET_REQ.QUEUE0_RESET`, writing the request register, and waiting for the reset bit to clear with `SOC15_WAIT_ON_RREG`.
6. Enable or disable trap interrupts by writing `VPEC_CNTL.TRAP_ENABLE`. Trap IRQ processing then calls `amdgpu_fence_process()` for the VPE ring.
7. Register common VPE fields into `vpe->regs`, including queue 0 read/write pointer registers, queue 0 preempt register, DPM scratch/dummy registers, and context-indicator scratch state.

No direct consumer use of the VPCNVC, VPDSCL, or VPCM fields was found in `vpe_v6_1.c`; those macros still define the hardware ABI for VPE command packets, firmware, future display-pipeline setup, diagnostics, or shared helper code that may program the VPEP processing pipe.

## State and Persistence Behavior

The header itself has no state. It describes stateful hardware registers whose lifetime is controlled by GPU reset, VPE firmware loading, VPE ring setup/teardown, doorbell configuration, power management, and display-pipeline programming.

- Firmware state is represented by `VPEC_UCODE_*`, `VPEC_F32_CNTL`, `VPEC_UCODE_VERSION`, and checksum fields. Manual loading writes these registers directly; PSP loading asks firmware services to patch SRAM and then releases F32 halt/reset.
- Ring state persists in VPEC queue registers until reset or reprogrammed. Software mirrors active queue state in `struct amdgpu_ring` fields such as ring GPU address, ring size, write pointer, read-pointer writeback address, doorbell index, and scheduler readiness.
- Doorbell state crosses the VPE block and NBIO doorbell aperture. The queue doorbell offset and enable bits must match `adev->nbio.funcs->vpe_doorbell_range()` setup.
- Queue reset bits are transient hardware-controlled state. The driver writes a reset request and waits for hardware to clear it.
- Interrupt/trap enable state persists in `VPEC_CNTL` until rewritten; interrupt completion is handled by the AMDGPU IRQ and fence layers.
- DPM and context indicator fields currently use generated dummy/scratch registers from this range. Their semantic ownership is established by VPE driver/firmware conventions rather than by the generated names.
- VPCNVC, VPDSCL, and VPCM fields represent retained pipeline configuration: pixel format, alpha handling, color-key ranges, CSC matrices, scaler taps/ratios/window geometry, line-buffer partitioning, and memory power modes. The header does not encode reset defaults, double-buffering rules, or write sequencing beyond naming `*_UPDATE_PENDING` status bits.

## Dependencies and Integration Points

Direct include in this tree:

- `drivers/gpu/drm/amd/amdgpu/vpe_v6_1.c`

Primary companion header:

- `drivers/gpu/drm/amd/include/asic_reg/vpe/vpe_6_1_0_offset.h`, which supplies the `regVPEC_*`, `regVPCNVC_*`, `regVPDSCL_*`, and `regVPCM_*` register offsets paired with these masks/shifts.

Key integration points:

- AMDGPU register helpers: `RREG32`, `WREG32`, `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_WAIT_ON_RREG`, `lower_32_bits`, `upper_32_bits`, and `order_base_2`.
- VPE driver objects: `struct amdgpu_vpe`, `struct amdgpu_ring`, `struct amdgpu_device`, `vpe_get_reg_offset()`, `vpe->num_instances`, `vpe->regs`, and `vpe->trap_irq`.
- Firmware path: `amdgpu_vpe_init_microcode`, VPE firmware images `amdgpu/vpe_6_1_0.bin`, `vpe_6_1_1.bin`, `vpe_6_1_3.bin`, `struct vpe_firmware_header_v1_0`, PSP firmware loading, and manual microcode streaming.
- Ring scheduling: queue 0 RB/IB control, pointer, base, writeback, preempt, and doorbell registers are wired into the generic AMDGPU ring and fence infrastructure.
- Interrupt path: VPE trap source IDs from `ivsrcid/vpe/irqsrcs_vpe_6_1.h`, `amdgpu_irq_add_id()`, `amdgpu_fence_process()`, and `VPEC_CNTL.TRAP_ENABLE`.
- Power and DPM path: `amdgpu_vpe_configure_dpm()` and generated dummy registers used for DPM enable, ratio, request interval, decision thresholds, clamp thresholds, request level, and context indicator.
- Display/VPEP pipeline programming: VPCNVC, VPDSCL, and VPCM fields align with VPEP sub-block address blocks and are expected to be consumed by firmware command streams or future host-side VPE pipeline setup alongside the corresponding offset macros.

## Risks

- Hardware ABI drift is the main risk. These generated constants must match VPE 6.1.0 register layout exactly. A wrong shift or mask can silently write another hardware field and cause firmware load failures, queue hangs, missed traps, invalid doorbells, or incorrect pixel processing.
- The header spans multiple IP revisions in practice. `vpe_v6_1.c` already carries local offset overrides for VPE 6.1.1 registers while still using field names from this header. New code must verify register offsets and field compatibility before reusing a 6.1.0 field on 6.1.1 or 6.1.3 hardware.
- Queue templates are highly repetitive. Accidentally using queue 0 masks with a non-queue-0 register may compile because layouts are similar, but it can break only one queue or one DPM scratch use. Conversely, the current driver intentionally uses queue 0 fields for queue 0 setup only.
- Ring address fields use hardware-specific alignment and split-address conventions. `RB_BASE` is programmed from `ring->gpu_addr >> 8`, `RB_BASE_HI` from `>> 40`, and read-pointer writeback low addresses are masked to 4-byte alignment. Changing these units without hardware confirmation risks DMA to the wrong address.
- Write-pointer programming has ordering requirements. The driver sets `VPEC_QUEUE0_MINOR_PTR_UPDATE` before reducing `RB_WPTR` and clears it afterward; skipping that sequence can leave firmware observing an invalid pointer transition.
- Doorbell programming crosses register and NBIO state. A mismatch between `VPEC_QUEUE0_DOORBELL_OFFSET`, `VPEC_QUEUE0_DOORBELL.ENABLE`, and NBIO doorbell range setup can produce jobs that never wake the engine.
- Trap and UMSCH interrupt bits share `VPEC_CNTL` with many other control bits. Read-modify-write helpers must preserve unrelated fields such as byte swap, preempt, z-state, NACK, and freeze interrupt controls.
- VPCNVC/VPDSCL/VPCM matrix, LUT, scaler, and memory-power fields are dense fixed-point hardware interfaces. Wrong coefficient format, tap count, scale ratio, or update sequencing can produce subtle image corruption rather than an obvious kernel error.
- This work item ends mid-register at `VPCM_GAMUT_REMAP_C13_C14`; any generated documentation or code review must merge with the next chunk before treating the VPCM gamut-remap family as complete.

## Test Signals

Useful validation signals for code consuming this chunk include:

- Kernel build coverage for `vpe_v6_1.c` with `vpe_6_1_0_offset.h` and this shift/mask header.
- VPE firmware-load tests on VPE 6.1.x hardware that exercise manual and PSP load paths, validate `VPEC_UCODE_ADDR/DATA` writes, and confirm F32 halt/reset release through `VPEC_F32_CNTL`.
- Ring bring-up tests that submit VPE jobs through queue 0, verify `VPEC_QUEUE0_RB_CNTL.RB_ENABLE`, `VPEC_QUEUE0_IB_CNTL.IB_ENABLE`, read/write pointer movement, read-pointer writeback, doorbell wakeups, trap IRQs, and fence completion.
- Ring stop/reset tests that assert `VPEC_QUEUE_RESET_REQ.QUEUE0_RESET` and verify the wait-for-clear path completes without timeout.
- Doorbell tests that compare the queue doorbell offset register against the NBIO VPE doorbell range and confirm jobs do not require polling fallback.
- Interrupt tests that toggle `VPEC_CNTL.TRAP_ENABLE`, generate a VPE trap, and confirm `amdgpu_fence_process()` retires the ring fence.
- Multi-instance VPE tests that run the same firmware and queue programming over every `vpe->num_instances` instance and catch instance-offset or collaborate-mode mistakes.
- DPM tests that verify the dummy/scratch registers assigned in `vpe->regs` still match firmware expectations for DPM enable, ratio, request interval, thresholds, request level, and context indicator.
- VPEP image-processing validation for future consumers of VPCNVC/VPDSCL/VPCM fields: format conversion, alpha/color keying, pre/post CSC, degamma, scaler coefficient RAM, tap counts, scale ratios, overscan/recout geometry, line-buffer partitioning, and memory power transitions should be checked with visible output or CRC comparisons.
- Register-readback diagnostics through debugfs or targeted MMIO traces for `VPEC_F32_CNTL`, `VPEC_CNTL`, queue 0 RB/IB/doorbell registers, queue reset/status registers, `VPEC_STATUS*`, and early VPCNVC/VPDSCL/VPCM pipeline registers.
