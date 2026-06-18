# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vpe/vpe_6_1_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003482`: lines 1-2611, `Docs/researches/chunks/subset-b-003482_research.md`
- `subset-b-003483`: lines 2612-4393, `Docs/researches/chunks/subset-b-003483_research.md`

## Chunk Research

### subset-b-003482: lines 1-2611

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

### subset-b-003483: lines 2612-4393

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vpe/vpe_6_1_0_sh_mask.h lines 2612-4393

## Scope

This chunk covers the tail of the generated AMD VPE 6.1.0 shift/mask header. The range starts in the VPCM gamut-remap field definitions and runs through the final `#endif` of the header. It contains only C preprocessor constants that describe hardware register bit positions and masks; it has no functions, structs, variables, control statements, allocation, locking, or runtime code.

The covered line range defines field layouts for these VPE display-processing blocks:

- VPCM color management: remaining gamut-remap coefficients, bias values, gamma-correction controls, LUT index/data/control registers, RAMA PWL region descriptors, HDR multiplier, dealpha, coefficient-format selection, memory-power control/status, and debug index/data.
- VPDPP top: clock gate controls, soft reset bits, CRC values/control, and host-read rate control.
- VPMPCC and VPMPC: top/bottom source selection, compositor mode and alpha/global gain fields, background color, memory-power/status, MPC clock/reset/CRC/bypass/background/read-control/pending-status registers.
- VPMPCC OGAM: output-gamma LUT, RAMA region programming, gamut-remap control, coefficient format, and gamut-remap matrix coefficients.
- VPMPCC MCM: shaper LUT, RAMA PWL regions, 3D LUT, 1D LUT, output normalization/offsets, memory-power, and test/debug registers.
- VPMPC output CSC: output muxing, float/denormal controls, denormal clamps, output CSC coefficient format/mode, and CSC matrix coefficients.
- VPFMT and VPOPP: formatter clamps, dynamic expansion, dithering/bit-depth controls, output pipe control, pipe CRC control/results, and top clock control.
- VPCDC and VPEP support: clock/reset, FE/BE surface and viewport configuration, global sync, ready status, memory power, RBBMIF timeout/status/disable bits.
- DC perfmon: performance-counter selection/control/state, perfmon interrupt/control, counter values, and high/low readback fields.

Because the chunk begins after the first VPCM gamut-remap definitions, some adjacent `VPCM_GAMUT_REMAP_*` fields are documented by the prior chunk. This file should be merged with the rest of the source-file chunks before drawing final per-file conclusions.

## Purpose

`vpe_6_1_0_sh_mask.h` is generated hardware metadata for the AMD VPE 6.1 IP block. The constants in this range define how a 32-bit MMIO register value is packed: each field has a `__SHIFT` value and a `_MASK` value. Driver code combines these masks with register offsets from `vpe_6_1_0_offset.h` and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, and `WREG32` to program individual hardware fields without open-coded bit arithmetic.

The direct in-tree consumer is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vpe_v6_1.c`, which includes both:

- `vpe/vpe_6_1_0_offset.h`
- `vpe/vpe_6_1_0_sh_mask.h`

The current `vpe_v6_1.c` code shown in this repository mostly exercises VPEC microcode, ring, interrupt, reset, and queue fields from earlier parts of the same header. The fields in this chunk describe the broader VPE pixel pipeline and diagnostic surface that firmware, command packets, debug tooling, golden settings, or future driver paths can use once the VPE data path is configured beyond ring bring-up.

## Important Macro Families

### VPCM Color Management and Gamma Correction

The first part of the range completes VPCM color-management fields:

- `VPCM_GAMUT_REMAP_C21_C22`, `C23_C24`, `C31_C32`, and `C33_C34` pack two 16-bit matrix coefficients per register. The previous chunk contains the earlier coefficient pairs.
- `VPCM_BIAS_CR_R` and `VPCM_BIAS_Y_G_CB_B` define 16-bit bias fields for RGB/YCbCr-style channel naming.
- `VPCM_COEF_FORMAT` selects bias, post-CSC, and gamut-remap coefficient formats.
- `VPCM_DEALPHA` enables dealpha and alpha-blend behavior.
- `VPCM_HDR_MULT_COEF` provides a 19-bit HDR multiplier coefficient.

The VPCM gamma-correction subsection uses the common AMD color LUT layout:

- `VPCM_GAMCOR_CONTROL` selects gamma-correction mode, PWL disable, current mode, and active bank selection.
- `VPCM_GAMCOR_LUT_INDEX`, `VPCM_GAMCOR_LUT_DATA`, and `VPCM_GAMCOR_LUT_CONTROL` provide indexed LUT access, 18-bit LUT data, write color mask, read color selection, debug read, host selection, and config mode.
- `VPCM_GAMCOR_RAMA_START_*`, `END_*`, `OFFSET_*`, and `REGION_*` fields describe the piecewise-linear RAMA curve programming for B/G/R channels.
- Region registers are packed in pairs. Each region has a 9-bit LUT offset and a 3-bit segment count; two regions are packed into one 32-bit register with the second region starting at bit 16 and segment count at bit 28.

The generated constants also expose `VPCM_MEM_PWR_CTRL`, `VPCM_MEM_PWR_STATUS`, `VPCM_TEST_DEBUG_INDEX`, and `VPCM_TEST_DEBUG_DATA`, which allow the gamma/color-management memory and debug windows to be controlled or inspected.

### VPDPP Top-Level Control and CRC

The `vpe_vpep_vpdpp0_dispdec_vpdpp_top_dispdec` address block defines the top-level display pipe processor controls:

- `VPDPP_CONTROL` contains clock enable and multiple gate-disable bits for VPECLK and DISPCLK domains, plus a test clock selector.
- `VPDPP_SOFT_RESET` individually resets VPCNVC, VPDSCL, VPCM, and VPOBUF sub-blocks.
- `VPDPP_CRC_VAL_R_G` and `VPDPP_CRC_VAL_B_A` expose 16-bit CRC values for color channels and alpha.
- `VPDPP_CRC_CTRL` enables CRC, continuous mode, one-shot pending state, 4:2:0 component selection, CRC source selection, pixel-format selection, and a 16-bit CRC mask.
- `VPHOST_READ_CONTROL` controls host-read rate limiting.

These fields are integration points for validation and debug paths that need deterministic CRC signatures from the VPE pixel pipeline. Incorrect source/format/mask programming can make CRC failures look like image-processing failures.

### VPMPCC Compositor and VPMPC Configuration

The `vpe_vpep_vpmpc_vpmpcc0_dispdec` block defines one multipipe compositor component:

- `VPMPCC_TOP_SEL`, `VPMPCC_BOT_SEL`, and `VPMPCC_VPOPP_ID` select source routing and destination/output-pipe identity.
- `VPMPCC_CONTROL` packs compositor mode, alpha blend mode, premultiplied-alpha mode, active-overlap-only behavior, background bits-per-component, bottom gain mode, global alpha, and global gain.
- `VPMPCC_TOP_GAIN`, `VPMPCC_BOT_GAIN_INSIDE`, and `VPMPCC_BOT_GAIN_OUTSIDE` provide 19-bit gain fields.
- `VPMPCC_BG_R_CR`, `VPMPCC_BG_G_Y`, and `VPMPCC_BG_B_CB` define 12-bit background color components.
- `VPMPCC_MEM_PWR_CTRL` and `VPMPCC_STATUS` expose output-gamma memory power state and compositor idle/busy/disabled state.

The adjacent `vpe_vpep_vpmpc_vpmpc_cfg_dispdec` block is MPC-wide configuration:

- `VPMPC_CLOCK_CONTROL` controls VPECLK gate disable and test clock selection.
- `VPMPC_SOFT_RESET` resets `VPMPCC0`, SFR0, SFT0, and the wider VPMPC block.
- `VPMPC_CRC_CTRL`, `VPMPC_CRC_SEL_CONTROL`, and `VPMPC_CRC_RESULT_*` configure and read MPC CRCs.
- `VPMPC_BYPASS_BG_AR` and `VPMPC_BYPASS_BG_GB` define bypass-background alpha/R/G/B component fields.
- `VPMPC_HOST_READ_CONTROL` mirrors host-read rate control for this block.
- `VPMPC_PENDING_STATUS_MISC` exposes `VPMPCC0_CONFIG_UPDATE_PENDING`.

These fields are central to blending, routing, background fill, CRC validation, and update synchronization in the compositor stage.

### VPMPCC Output Gamma and Gamut Remap

The `vpe_vpep_vpmpc_vpmpcc_ogam0_dispdec` block mirrors the VPCM gamma-correction structure for compositor output gamma:

- `VPMPCC_OGAM_CONTROL` selects OGAM mode, PWL disable, current mode, and bank selection.
- `VPMPCC_OGAM_LUT_INDEX`, `VPMPCC_OGAM_LUT_DATA`, and `VPMPCC_OGAM_LUT_CONTROL` provide indexed LUT programming and read/debug controls.
- `VPMPCC_OGAM_RAMA_START_*`, `END_*`, `OFFSET_*`, and `REGION_*` define per-channel PWL curve configuration and the same paired-region offset/segment layout used by VPCM.
- `VPMPCC_GAMUT_REMAP_COEF_FORMAT` and `VPMPCC_GAMUT_REMAP_MODE` select gamut-remap coefficient format and mode/current mode.
- `VPMPC_GAMUT_REMAP_C11_C12_A` through `C33_C34_A` pack 16-bit matrix coefficients for the alpha/output path.

The repeated region families are a risk area because a single field name typo or mask mismatch can affect only one curve segment or channel while the surrounding blocks still appear functional.

### VPMPCC MCM Shaper, 3D LUT, and 1D LUT

The `vpe_vpep_vpmpc_vpmpcc_mcm0_dispdec` block is the largest color-management section in this chunk. It defines:

- `VPMPCC_MCM_SHAPER_CONTROL`, shaper offsets/scales, shaper LUT index/data/write-enable, and shaper RAMA region descriptors.
- `VPMPCC_MCM_3DLUT_MODE`, `INDEX`, `DATA`, `DATA_30BIT`, `READ_WRITE_CONTROL`, output normalization factor, and per-channel output offsets.
- `VPMPCC_MCM_1DLUT_CONTROL`, indexed 1D LUT access, LUT control, 1D RAMA start/slope/base/end/offset registers, and paired region descriptors from region 0 through 33.
- `VPMPCC_MCM_MEM_PWR_CTRL` and MCM test/debug index/data registers.

The 3D LUT fields are especially format-sensitive: some registers carry 12-bit per-channel values, while `VPMPCC_MCM_3DLUT_DATA_30BIT` packs 10-bit B/G/R fields into one register. Read/write control exposes color-plane write mask, read color select, selected LUT bank, and 30-bit mode. Driver code must select the correct data format before writing or reading LUT entries.

The 1D LUT and shaper RAMA families use the same high-level pattern as VPCM/OGAM: start controls, start slopes/bases, end controls, offsets, and paired region offset/segment registers. That regularity helps generation and review, but it also makes copy/paste or generator-offset errors hard to spot by visual inspection.

### Output CSC, Formatter, Output Pipe, and CRC

The output color-space conversion block, `vpe_vpep_vpmpc_vpmpc_ocsc_dispdec`, defines:

- `VPMPC_OUT0_MUX` for output source selection.
- `VPMPC_OUT0_FLOAT_CONTROL`, `VPMPC_OUT0_DENORM_CONTROL`, and denormal clamp registers for G/Y and B/Cb components.
- `VPMPC_OUT_CSC_COEF_FORMAT` and `VPMPC_OUT0_CSC_MODE`.
- `VPMPC_OUT0_CSC_C11_C12_A` through `C33_C34_A`, packing 16-bit CSC coefficients in pairs.

The VPFMT block defines output formatting behavior:

- `VPFMT_CLAMP_COMPONENT_R/G/B` and `VPFMT_CLAMP_CNTL` provide clamp values and clamp selection.
- `VPFMT_DYNAMIC_EXP_CNTL` controls dynamic expansion mode and enable state.
- `VPFMT_CONTROL` contains pixel encoding, sub-sampling order, memory power mode, interlace, truncation, dithering, and pixel-repetition related fields.
- `VPFMT_BIT_DEPTH_CONTROL` selects truncation/dither depth, mode, spatial/temporal dithering, high-pass, frame counter, and RGB random enable.
- `VPFMT_DITHER_RAND_R/G/B_SEED` define random seeds for dithering.

The VPOPP blocks define output pipe control, pipe CRC control/mask/results, and top-level clock control:

- `VPOPP_PIPE_CONTROL` exposes output clock enable.
- `VPOPP_PIPE_CRC_CONTROL`, `VPOPP_PIPE_CRC_MASK`, and `VPOPP_PIPE_CRC_RESULT*` control and read pipe CRCs.
- `VPOPP_TOP_CLK_CONTROL` controls VPECLK/DISPCLK gate disable and test clock selection.

Together these constants describe the end of the VPE image-processing path: CSC, denormal/clamp, format conversion, dithering, pipe output, and CRC validation.

### VPCDC, Memory Power, Timeouts, and Perfmon

The `vpe_vpep_vpcdc_cdc_dispdec` block provides command/data-capture and front/back-end support fields:

- `VPEP_MGCG_CNTL` controls medium-grain clock gating and memory low-power delay.
- `VPCDC_SOFT_RESET` resets FE0, BE0, and global sync.
- `VPCDC_FE0_SURFACE_CONFIG`, `CROSSBAR_CONFIG`, viewport start/dimension, and chroma viewport start/dimension fields describe FE surface layout and routing.
- `VPCDC_BE0_P2B_CONFIG` and `VPCDC_BE0_GLOBAL_SYNC_CONFIG` define backend pipe-to-buffer and sync behavior.
- `VPCDC_GLOBAL_SYNC_TRIGGER` and `VPCDC_VREADY_STATUS` expose global-sync trigger and VREADY status.
- `VPEP_MEM_GLOBAL_PWR_REQ_CNTL`, `VPFE_MEM_PWR_CNTL`, and `VPBE_MEM_PWR_CNTL` control memory power request/force/mode/state/disable behavior.
- `VPEP_RBBMIF_TIMEOUT`, `VPEP_RBBMIF_STATUS`, and `VPEP_RBBMIF_TIMEOUT_DIS` configure and report register-bus timeout behavior per client.

The final address block, `vpe_vpep_vpcdc_vpcdc_dcperfmon_dc_perfmon_dispdec`, defines generic display perfmon registers:

- `PERFCOUNTER_CNTL` selects events, counted value source, increment mode, hardware control, run-enable mode, counter-off behavior, restart, interrupt enable, active state, and counter selector.
- `PERFCOUNTER_CNTL2` selects counted value type, hardware stop selectors, counter-off selector, and secondary counter selector.
- `PERFCOUNTER_STATE` packs state for eight counters with per-counter state select bits.
- `PERFMON_CNTL` and `PERFMON_CNTL2` control perfmon state, report count, counter-off interrupt behavior, clock enable, and run-enable start/stop selectors.
- `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW` expose interrupt status/ack bits and counter value readback.

These fields are not VPE command submission logic, but they are important for diagnostics, performance analysis, and hang triage.

## Control Flow and State

There is no C control flow in this chunk. The effective runtime flow is indirect:

1. Code or firmware chooses a register offset from `vpe_6_1_0_offset.h`.
2. It uses this header's `__SHIFT` and `_MASK` constants through field helpers, or manually with bit operations, to pack or extract a register field.
3. It reads or writes the resulting value through AMDGPU MMIO accessors.
4. The VPE hardware changes image-processing behavior, memory-power state, reset state, routing, CRC output, timeout reporting, or performance-counter state.

The persistent state is hardware state, not C-owned state. Key state surfaces represented by this range include LUT contents and selected banks, PWL region configuration, CSC/gamut matrices, alpha/gain/background settings, CRC enable/results, soft-reset bits, pending-update status, memory power state, surface/viewport/global-sync configuration, timeout status/ack bits, and perfmon counters. Those values persist in registers until hardware reset, power transitions, firmware/driver reinitialization, or a later MMIO write changes them.

The register families also include status and current-mode fields, such as `*_MODE_CURRENT`, `*_SELECT_CURRENT`, `VPMPCC_STATUS`, `VPMPC_CRC_UPDATE_ENABLED`, `VPMPC_CRC_UPDATE_LOCK`, `VPCDC_VREADY_STATUS`, `VPEP_RBBMIF_STATUS`, and perfmon active/state bits. Driver paths should treat those as hardware-observed state rather than ordinary writable configuration unless the corresponding hardware specification says otherwise.

## Dependencies and Integration Points

The direct dependencies are compile-time hardware-contract dependencies:

- `vpe_6_1_0_offset.h` must provide matching `reg*` offsets and base-index macros for every register family whose fields are defined here.
- `vpe_v6_1.c` includes this header together with the offset header and uses the same generated naming convention with AMDGPU MMIO helpers.
- SOC/IP version selection must choose this VPE 6.1.0 layout only for compatible hardware. The file also sits near VPE 6.1.1/6.1.3 firmware paths in `vpe_v6_1.c`; local overrides in that C file show that minor IP versions can move some registers, so these masks must not be blindly reused with incompatible offsets.
- AMDGPU field helpers depend on the exact naming convention `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.
- Display/color-management code, VPE firmware command processing, debugfs or diagnostic readers, CRC validation paths, reset/power-management paths, and performance-monitoring tools can all depend on these definitions matching the ASIC register specification.

The integration boundary is narrow but strict: this header says where bits live inside a register, while the sibling offset header says where the register lives in MMIO space. A correct mask paired with a wrong offset, or a correct offset paired with a wrong mask, is still a hardware programming bug.

## Risks

- A wrong shift or mask compiles cleanly but can program the wrong hardware field at runtime. The failure may appear as bad color output, incorrect blending, broken CRCs, stuck update-pending state, timeouts, or performance-counter misreads.
- Many fields pack two or three channel values into one register. Channel ordering errors, especially between RGB and YCbCr-style names (`R_CR`, `G_Y`, `B_CB`), can produce subtle color defects.
- LUT and RAMA programming is highly repetitive. Generator or copy errors in one region, channel, or LUT family can affect only a narrow range of a transfer curve and be hard to diagnose visually.
- The MCM 3D LUT has both normal and 30-bit data paths. Using 12-bit-style fields when the hardware expects 10-bit packed `DATA_30BIT`, or the reverse, can corrupt LUT programming without obvious MMIO errors.
- Reset and clock-gating fields are mixed into the same generated header as color fields. Incorrect use during active processing can hang a pipeline or leave sub-blocks disabled.
- Memory-power controls expose force, disable, low-power mode, and state bits. Treating status bits as configuration, or powering down memory while LUTs are in use, risks underflow, stale data, or hangs.
- CRC and perfmon fields are validation tools as well as hardware controls. Misprogramming masks, source selectors, or run-enable controls can invalidate test results.
- The chunk starts mid-VPCM gamut-remap family, so this chunk alone is incomplete for full VPCM matrix analysis.
- The final line is the file's include-guard terminator. Any later merged report must account for all earlier chunks because this chunk does not include the license/header guard start or the VPEC ring/firmware fields.

## Test Signals

Useful validation signals for this generated header are a mix of build, static, and hardware tests:

- Kernel build coverage for `drivers/gpu/drm/amd/amdgpu/vpe_v6_1.c` with `vpe_6_1_0_offset.h` and `vpe_6_1_0_sh_mask.h` included.
- Static generated-header checks that every field in this range has a coherent `__SHIFT`/`_MASK` pair and that masks are contained within 32 bits.
- Cross-header checks that every `regVPCM_*`, `regVPDPP_*`, `regVPMPCC_*`, `regVPMPC_*`, `regVPFMT_*`, `regVPOPP_*`, `regVPCDC_*`, `regVPEP_*`, and perfmon register in the offset header has matching field definitions where expected.
- Hardware smoke tests on compatible VPE 6.1 hardware: VPE probe, firmware load, ring start, command submission, suspend/resume, and GPU reset should not regress after header changes.
- Color-management validation that programs VPCM/OGAM/MCM LUTs and matrices and compares known output or CRC values.
- CRC tests that enable VPDPP, VPMPC, and VPOPP CRC paths with known frames and verify stable channel results and mask behavior.
- Formatter tests for clamp, bit depth, truncation, dithering, random seeds, dynamic expansion, and CSC output on RGB and YCbCr-like formats.
- Power-management tests that toggle clock gating, soft resets, memory power states, and low-power modes while checking for idle/busy/status convergence.
- Timeout and recovery tests that verify `VPEP_RBBMIF_STATUS` timeout status/ack/mask behavior and per-client disable bits.
- Perfmon tests that select events, start/stop counters, read high/low values, acknowledge interrupts, and confirm active/state bits behave as expected.
